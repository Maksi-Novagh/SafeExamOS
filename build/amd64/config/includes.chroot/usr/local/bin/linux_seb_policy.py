"""Pure security-policy model for the experimental Linux SEB application.

This package is independent of the Windows implementation. It does not
implement Browser Exam Key, Config Key, encrypted .seb, or SEB Server.
It enforces only a deliberately narrow, institution-authored JSON lab profile.
"""
from __future__ import annotations

import ipaddress
import json
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

MAX_BYTES = 64 * 1024
LABEL = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")
UNSUPPORTED_SECURITY_KEYS = frozenset({
    "browser_exam_key", "configuration_key", "seb_server",
    "encrypted_seb", "allow_external_apps", "allow_shell",
})


class PolicyError(ValueError):
    """An invalid or unsupported configuration must not launch a browser."""


def validate_origin(value: str) -> str:
    if not isinstance(value, str) or len(value) > 256:
        raise PolicyError("Invalid origin")
    if any(ch.isspace() or ord(ch) < 32 for ch in value):
        raise PolicyError("Whitespace in origin")
    u = urlsplit(value)
    if (u.scheme != "https" or not u.hostname or u.username or u.password
            or u.port is not None or u.path not in ("", "/") or u.query or u.fragment
            or u.netloc != u.hostname):
        raise PolicyError("Only canonical HTTPS origins are supported")
    host = u.hostname
    if host.endswith(".") or host == "localhost" or host == "local":
        raise PolicyError("Local hostnames are not allowed")
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        raise PolicyError("IP literals are not supported for exam origins")
    if "." not in host or not all(LABEL.fullmatch(p) for p in host.split(".")):
        raise PolicyError("Invalid domain name")
    return "https://" + host


def validate_url(value: str) -> tuple[str, str]:
    if not isinstance(value, str) or len(value) > 2048:
        raise PolicyError("Invalid URL")
    if any(ch.isspace() or ord(ch) < 32 or ch == "\\" for ch in value):
        raise PolicyError("Unsafe URL characters")
    u = urlsplit(value)
    if (u.scheme != "https" or not u.hostname or u.username or u.password
            or u.port is not None or u.fragment or u.netloc != u.hostname):
        raise PolicyError("Only canonical HTTPS URLs are supported")
    origin = validate_origin("https://" + u.hostname)
    return origin, value


@dataclass(frozen=True)
class ExamPolicy:
    title: str
    start_url: str
    origins: frozenset[str]
    downloads: bool = False
    uploads: bool = False
    max_browser_windows: int = 1
    allow_secondary_windows: bool = False

    def permits(self, uri: str) -> bool:
        try:
            origin, _ = validate_url(uri)
        except (PolicyError, ValueError):
            return False
        return origin in self.origins


def parse_config(data: object) -> ExamPolicy:
    if not isinstance(data, dict):
        raise PolicyError("Configuration must be an object")
    required = {"schema", "title", "start_url", "allowed_origins"}
    optional = {"allow_downloads", "allow_uploads", "max_browser_windows", "allow_secondary_windows"}
    unknown = set(data) - required - optional
    if unknown or not required.issubset(data):
        raise PolicyError("Unknown, incomplete, or unsupported configuration fields")
    if any(k in data for k in UNSUPPORTED_SECURITY_KEYS):
        raise PolicyError("Unsupported security-sensitive setting")
    if data["schema"] != "safeexamos-linux-seb-lab-v1":
        raise PolicyError("Unsupported configuration schema")
    title = data["title"]
    if not isinstance(title, str) or not (1 <= len(title) <= 80):
        raise PolicyError("Invalid title")
    if any(ord(char) < 32 for char in title):
        raise PolicyError("Control characters in title")
    allowed = data["allowed_origins"]
    if not isinstance(allowed, list) or not (1 <= len(allowed) <= 16):
        raise PolicyError("Expected 1 to 16 explicitly allowed HTTPS origins")
    origins = frozenset(validate_origin(item) for item in allowed)
    if len(origins) != len(allowed):
        raise PolicyError("Duplicate allowed origin")
    start_origin, start_url = validate_url(data["start_url"])
    if start_origin not in origins:
        raise PolicyError("Start URL is not within an allowed origin")
    downloads = data.get("allow_downloads", False)
    uploads = data.get("allow_uploads", False)
    if downloads is not False or uploads is not False:
        raise PolicyError("Downloads and uploads are not implemented safely yet")
    limit = data.get("max_browser_windows", 1)
    allow_secondary = data.get("allow_secondary_windows", False)
    if type(limit) is not int or not (1 <= limit <= 3):
        raise PolicyError("Browser window limit must be an integer between 1 and 3")
    if type(allow_secondary) is not bool:
        raise PolicyError("Secondary window permission must be a boolean")
    if (limit > 1) != allow_secondary:
        raise PolicyError("Multiwindow settings must explicitly agree")
    return ExamPolicy(title, start_url, origins, downloads, uploads,
                      limit, allow_secondary)


def load_config(path: str | Path) -> ExamPolicy:
    path = Path(path)
    if not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise PolicyError("Configuration missing or larger than 64 KiB")
    try:
        with path.open("rb") as stream:
            data = stream.read(MAX_BYTES + 1)
        return parse_config(json.loads(data))
    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        if isinstance(exc, PolicyError):
            raise
        raise PolicyError("Invalid configuration JSON") from exc
