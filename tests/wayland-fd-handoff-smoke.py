#!/usr/bin/env python3
"""Offline SCM_RIGHTS transport regression; not compositor authorization."""
import importlib.util
import os
import array
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("wayland_fd_handoff", ROOT / "linux-seb/fd_handoff.py")
handoff = importlib.util.module_from_spec(spec)
spec.loader.exec_module(handoff)


class HandoffTests(unittest.TestCase):
    def test_connection_can_be_transferred_without_exposing_socket_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "private-wayland")
            listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            listener.bind(path)
            listener.listen(1)
            sender, receiver = socket.socketpair()
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            try:
                client.connect(path)
                server, _ = listener.accept()
                try:
                    os.chmod(tmp, 0o000)
                    handoff.send_wayland_fd(sender, client)
                    transferred = handoff.receive_wayland_fd(receiver)
                    try:
                        self.assertFalse(os.get_inheritable(transferred))
                        os.write(transferred, b"ready")
                        self.assertEqual(server.recv(5), b"ready")
                    finally:
                        os.close(transferred)
                finally:
                    server.close()
            finally:
                client.close()
                sender.close()
                receiver.close()
                listener.close()

    def test_missing_descriptor_rejected(self):
        a, b = socket.socketpair()
        try:
            a.sendall(b"W")
            with self.assertRaises(handoff.HandoffError):
                handoff.receive_wayland_fd(b)
        finally:
            a.close()
            b.close()

    def test_unexpected_descriptor_type_rejected(self):
        a, b = socket.socketpair()
        with tempfile.TemporaryFile() as f:
            try:
                a.sendmsg([b"W"], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, array.array("i", [f.fileno()]))])
                with self.assertRaises(handoff.HandoffError):
                    handoff.receive_wayland_fd(b)
            finally:
                a.close()
                b.close()


    def test_multiple_descriptors_rejected(self):
        a, b = socket.socketpair()
        first, second = socket.socketpair()
        try:
            rights = array.array("i", [first.fileno(), second.fileno()])
            a.sendmsg([b"W"], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, rights)])
            with self.assertRaises(handoff.HandoffError):
                handoff.receive_wayland_fd(b)
        finally:
            a.close()
            b.close()
            first.close()
            second.close()

    def test_exec_child_receives_only_explicit_wayland_descriptor(self):
        """Exercise a real exec boundary, but not Unix-account isolation."""
        with tempfile.TemporaryDirectory() as tmp:
            listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            listener.bind(str(Path(tmp) / "private-wayland"))
            listener.listen(1)
            channel_parent, channel_child = socket.socketpair()
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            try:
                client.connect(str(Path(tmp) / "private-wayland"))
                server, _ = listener.accept()
                try:
                    child_script = """
import importlib.util, os, socket
spec = importlib.util.spec_from_file_location('handoff', os.environ['HANDOFF_SOURCE'])
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
channel = socket.socket(fileno=int(os.environ['TRANSFER_FD']))
fd = module.receive_wayland_fd(channel)
channel.close()
# The exec'd browser would inherit this as WAYLAND_SOCKET.
os.set_inheritable(fd, True)
os.environ['WAYLAND_SOCKET'] = str(fd)
os.write(fd, b'child-ready')
os.close(fd)
"""
                    environment = dict(os.environ, TRANSFER_FD=str(channel_child.fileno()),
                                       HANDOFF_SOURCE=str(ROOT / "linux-seb/fd_handoff.py"))
                    proc = subprocess.Popen([sys.executable, "-c", child_script],
                                            env=environment, pass_fds=(channel_child.fileno(),))
                    channel_child.close()
                    handoff.send_wayland_fd(channel_parent, client)
                    channel_parent.close()
                    server.settimeout(5)
                    self.assertEqual(server.recv(11), b"child-ready")
                    self.assertEqual(proc.wait(timeout=5), 0)
                finally:
                    server.close()
            finally:
                client.close()
                listener.close()
                channel_parent.close()
                channel_child.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
