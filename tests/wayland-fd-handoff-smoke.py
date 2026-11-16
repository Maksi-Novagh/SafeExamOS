#!/usr/bin/env python3
"""Offline SCM_RIGHTS transport regression; not compositor authorization."""
import importlib.util
import os
import socket
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
            import array
            try:
                a.sendmsg([b"W"], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, array.array("i", [f.fileno()]))])
                with self.assertRaises(handoff.HandoffError):
                    handoff.receive_wayland_fd(b)
            finally:
                a.close()
                b.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
