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
    if channel.family != socket.AF_UNIX or channel.getsockopt(
        socket.SOL_SOCKET, socket.SO_TYPE
    ) != socket.SOCK_STREAM:
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
    """Receive one Unix stream descriptor and reject all malformed transfers.

    The transport is not authentication. A trusted parent must verify its
    intended child/peer and must not expose the channel as a public socket.
    """
    if channel.family != socket.AF_UNIX or channel.getsockopt(
        socket.SOL_SOCKET, socket.SO_TYPE
    ) != socket.SOCK_STREAM:
        raise HandoffError("Invalid transport")
    width = array.array("i").itemsize
    data, anc, flags, _ = channel.recvmsg(1, socket.CMSG_SPACE(width * 2))
    received: list[int] = []
    accepted: int | None = None
    try:
        for level, kind, raw in anc:
            if level == socket.SOL_SOCKET and kind == socket.SCM_RIGHTS:
                values = array.array("i")
                values.frombytes(raw[:len(raw) - len(raw) % width])
                received.extend(values)
        if data != b"W" or flags & (socket.MSG_CTRUNC | socket.MSG_TRUNC) or len(received) != 1:
            raise HandoffError("Expected exactly one Wayland descriptor")
        candidate = socket.socket(fileno=received[0])
        try:
            if candidate.family != socket.AF_UNIX or candidate.getsockopt(
                socket.SOL_SOCKET, socket.SO_TYPE
            ) != socket.SOCK_STREAM:
                raise HandoffError("Received descriptor is not a Unix stream socket")
            os.set_inheritable(candidate.fileno(), False)
            accepted = candidate.detach()
            return accepted
        finally:
            # If validation fails, the socket object owns and closes the FD.
            candidate.close()
    except (OSError, ValueError) as exc:
        if isinstance(exc, HandoffError):
            raise
        raise HandoffError("Invalid transferred socket") from exc
    finally:
        # The socket constructor above takes ownership of the first FD. It
        # may already have closed it on validation failure. Close only the
        # remaining descriptors, avoiding double-close/reused-FD races.
        for item in received[1:]:
            try:
                os.close(item)
            except OSError:
                pass
        if received and accepted is None and "candidate" not in locals():
            try:
                os.close(received[0])
            except OSError:
                pass
