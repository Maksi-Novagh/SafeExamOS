"""Single-use Unix FD transport for an experimental Wayland client handoff.

The caller must create a private AF_UNIX SOCK_STREAM socketpair and establish
peer identity *before* invoking this transport. This module grants no identity,
process, compositor, or session authorization on its own.
"""
from __future__ import annotations

import array
import os
import socket


class HandoffError(ValueError):
    """Malformed or missing transferred connection; fail closed."""


def send_wayland_fd(channel: socket.socket, connected_socket: socket.socket) -> None:
    """Send one already connected Unix stream socket over a trusted channel."""
    if channel.family != socket.AF_UNIX or channel.type & socket.SOCK_STREAM != socket.SOCK_STREAM:
        raise HandoffError("Transport must be a Unix stream socket")
    if connected_socket.family != socket.AF_UNIX or connected_socket.getsockopt(
        socket.SOL_SOCKET, socket.SO_TYPE
    ) != socket.SOCK_STREAM:
        raise HandoffError("Wayland connection must be a Unix stream socket")
    rights = array.array("i", [connected_socket.fileno()])
    sent = channel.sendmsg([b"W"], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, rights)])
    if sent != 1:
        raise HandoffError("Incomplete Wayland descriptor transfer")


def receive_wayland_fd(channel: socket.socket) -> int:
    """Receive exactly one connected stream descriptor, never an arbitrary path."""
    if channel.family != socket.AF_UNIX:
        raise HandoffError("Invalid transport family")
    width = array.array("i").itemsize
    data, anc, flags, _ = channel.recvmsg(1, socket.CMSG_SPACE(width * 2))
    fds: list[int] = []
    try:
        for level, kind, raw in anc:
            if level == socket.SOL_SOCKET and kind == socket.SCM_RIGHTS:
                values = array.array("i")
                values.frombytes(raw[:len(raw) - len(raw) % width])
                fds.extend(values)
        if data != b"W" or flags & (socket.MSG_CTRUNC | socket.MSG_TRUNC) or len(fds) != 1:
            raise HandoffError("Expected exactly one Wayland descriptor")
        fd = fds[0]
        # Do not permit unexpected device/file descriptors through this channel.
        client = socket.socket(fileno=fd)
        try:
            if client.family != socket.AF_UNIX or client.getsockopt(
                socket.SOL_SOCKET, socket.SO_TYPE
            ) != socket.SOCK_STREAM:
                raise HandoffError("Received descriptor is not a Unix stream socket")
            os.set_inheritable(fd, False)
            return client.detach()
        finally:
            client.close()
    except (OSError, ValueError) as exc:
        if isinstance(exc, HandoffError):
            raise
        raise HandoffError("Invalid transferred socket") from exc
    finally:
        # Ownership of exactly one validated descriptor transfers to caller.
        # On failures ensure every extracted descriptor is closed.
        if "fd" not in locals() or (data != b"W" or flags & (socket.MSG_CTRUNC | socket.MSG_TRUNC) or len(fds) != 1):
            for item in fds:
                try:
                    os.close(item)
                except OSError:
                    pass
