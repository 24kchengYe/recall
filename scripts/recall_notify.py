#!/usr/bin/env python3
"""
Recall Notification — TaskCompleted hook script.

Sends a WeChat notification via Server酱 (ServerChan) when a task is marked as completed.
Reads JSON from stdin containing task information from Claude Code's TaskCompleted hook.

Configuration is stored in {basePath}/_config.json under the "notify" field.
"""

import json
import os
import platform
import sys
import urllib.request
import urllib.parse
from pathlib import Path

# Fix Windows terminal encoding
if platform.system() == "Windows" or "MSYS" in os.environ.get("MSYSTEM", ""):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_BASE_PATH = r"D:\claude-sessions"
SERVERCHAN_API = "https://sctapi.ftqq.com/{sendkey}.send"


def _normalize_path(path_str: str) -> str:
    """Convert MSYS-style paths to Windows paths if needed."""
    if len(path_str) >= 3 and path_str[0] == "/" and path_str[2] == "/":
        drive_letter = path_str[1].upper()
        return f"{drive_letter}:{path_str[2:]}".replace("/", "\\")
    return path_str


def _load_config() -> dict:
    """Load _config.json from the central directory."""
    default = Path(_normalize_path(DEFAULT_BASE_PATH))
    config_path = default / "_config.json"
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _get_notify_config(config: dict) -> dict:
    """Extract notification configuration."""
    return config.get("notify", {})


def _send_serverchan(sendkey: str, title: str, desp: str) -> bool:
    """Send notification via Server酱 API.

    Args:
        sendkey: Server酱 SENDKEY
        title: Notification title (max 32 chars)
        desp: Notification body (supports markdown)

    Returns:
        True if sent successfully
    """
    url = SERVERCHAN_API.format(sendkey=sendkey)
    data = urllib.parse.urlencode({
        "title": title[:32],
        "desp": desp
    }).encode("utf-8")

    try:
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("code") == 0 or result.get("errno") == 0
    except Exception as e:
        print(f"[recall notify] error sending notification: {e}", file=sys.stderr)
        return False


def main():
    # Read hook input from stdin
    try:
        raw = sys.stdin.read()
        if raw.strip():
            hook_data = json.loads(raw)
        else:
            hook_data = {}
    except (json.JSONDecodeError, Exception):
        hook_data = {}

    # Load config
    config = _load_config()
    notify_config = _get_notify_config(config)

    if not notify_config.get("enabled", False):
        sys.exit(0)  # Notifications disabled

    sendkey = notify_config.get("sendkey", "")
    if not sendkey:
        sys.exit(0)  # No sendkey configured

    provider = notify_config.get("provider", "serverchan")
    if provider != "serverchan":
        print(f"[recall notify] unsupported provider: {provider}", file=sys.stderr)
        sys.exit(0)

    # Extract task info from hook data
    # Claude Code TaskCompleted hook provides task details
    task_subject = hook_data.get("task_subject", "") or hook_data.get("subject", "")
    task_status = hook_data.get("task_status", "") or hook_data.get("status", "completed")
    cwd = hook_data.get("cwd", "") or os.getcwd()
    session_id = hook_data.get("session_id", "")

    # Build notification content
    if task_subject:
        title = f"Task Done: {task_subject}"[:32]
    else:
        title = "Claude Code Task Completed"

    # Build markdown body
    lines = []
    lines.append("## Claude Code 任务完成通知")
    lines.append("")
    if task_subject:
        lines.append(f"**任务**: {task_subject}")
    lines.append(f"**状态**: {task_status}")
    lines.append(f"**项目**: `{cwd}`")
    if session_id:
        lines.append(f"**会话ID**: `{session_id[:8]}...`")
    lines.append("")
    lines.append(f"*Sent by Recall v2.0*")

    desp = "\n".join(lines)

    # Send notification
    success = _send_serverchan(sendkey, title, desp)
    if not success:
        print("[recall notify] failed to send notification", file=sys.stderr)


if __name__ == "__main__":
    main()
