#!/bin/sh

# Prototype autostart. Production images will replace this with a stricter session manager.
if [ "$(id -u)" -ne 0 ] && [ "$(tty 2>/dev/null || true)" = "/dev/tty1" ] && [ -z "${WAYLAND_DISPLAY:-}" ]; then
  exec /usr/local/bin/safeexamos-session
fi
