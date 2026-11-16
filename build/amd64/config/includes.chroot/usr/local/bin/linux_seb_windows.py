"""Fail-closed registry for native SEB-managed browser windows.

This registry only authorizes child *WebKit WebViews*. It does not spawn
applications or trust window titles, executable names, or student requests.
The Wayland compositor is not yet a hard enforcement boundary.
"""
from __future__ import annotations

from dataclasses import dataclass


class WindowPolicyError(ValueError):
    pass


@dataclass(frozen=True)
class WindowRecord:
    window_id: int
    parent_id: int | None
    role: str
    target: str


class ManagedWindows:
    def __init__(self, policy):
        self.policy = policy
        self.records: dict[int, WindowRecord] = {}
        self.next_id = 1

    def open_main(self) -> WindowRecord:
        if self.records:
            raise WindowPolicyError("Main window already exists")
        record = WindowRecord(self.next_id, None, "main", self.policy.start_url)
        self.records[record.window_id] = record
        self.next_id += 1
        return record

    def open_child(self, parent_id: int, target: str) -> WindowRecord:
        # Only the primary exam WebView may request additional windows.
        # This prevents a child popup from creating an unbounded tree and
        # avoids orphaned descendants when a child is closed.
        if type(parent_id) is not int or parent_id not in self.records:
            raise WindowPolicyError("Unmanaged parent window")
        if self.records[parent_id].role != "main":
            raise WindowPolicyError("Only the main exam window can open children")
        if not self.policy.allow_secondary_windows:
            raise WindowPolicyError("Secondary browser windows disabled")
        if len(self.records) >= self.policy.max_browser_windows:
            raise WindowPolicyError("Browser window capacity reached")
        if not self.policy.permits(target):
            raise WindowPolicyError("Child window URL outside approved origins")
        record = WindowRecord(self.next_id, parent_id, "secondary", target)
        self.records[record.window_id] = record
        self.next_id += 1
        return record

    def close(self, window_id: int) -> bool:
        if window_id not in self.records:
            return False
        # An exam cannot be made to quit by closing its main browser window.
        if self.records[window_id].role == "main":
            raise WindowPolicyError("Main examination window cannot close itself")
        self.records.pop(window_id)
        return True

    def clear(self):
        self.records.clear()
