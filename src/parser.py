from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
import re
from dateutil import parser as dtparser
from dateutil.tz import gettz
import pandas as pd
import emoji

# Compile all patterns with IGNORECASE so 'pm'/'am' also match
FLAGS = re.IGNORECASE

# User message patterns (Android/iOS, with/without [brackets], with/without seconds)
PATTERNS = [
    re.compile(
        r"^(?P<date>\d{1,2}/\d{1,2}/\d{2,4}), (?P<time>\d{1,2}:\d{2}(?::\d{2})?)"
        r"(?:\s?(?P<ampm>[AP]M))?\s-\s(?P<name>[^:]+): (?P<msg>.*)$",
        FLAGS
    ),
    re.compile(
        r"^\[(?P<date>\d{1,2}/\d{1,2}/\d{2,4}), (?P<time>\d{1,2}:\d{2}(?::\d{2})?)"
        r"(?:\s?(?P<ampm>[AP]M))?\]\s(?P<name>[^:]+): (?P<msg>.*)$",
        FLAGS
    ),
]

# System message patterns (no sender)
SYS_PATTERNS = [
    re.compile(
        r"^(?P<date>\d{1,2}/\d{1,2}/\d{2,4}), (?P<time>\d{1,2}:\d{2}(?::\d{2})?)"
        r"(?:\s?(?P<ampm>[AP]M))?\s-\s(?P<msg>.*)$",
        FLAGS
    ),
    re.compile(
        r"^\[(?P<date>\d{1,2}/\d{1,2}/\d{2,4}), (?P<time>\d{1,2}:\d{2}(?::\d{2})?)"
        r"(?:\s?(?P<ampm>[AP]M))?\]\s(?P<msg>.*)$",
        FLAGS
    ),
]

MEDIA_MARKERS = (
    "<Media omitted>", "image omitted", "video omitted",
    "sticker omitted", "audio omitted", "\u200eimage omitted",
    "\u200evideo omitted"
)

@dataclass
class ChatLine:
    ts: pd.Timestamp | None
    name: str | None
    msg: str
    is_system: bool

def _match_any(line: str, pats: Iterable[re.Pattern]):
    for p in pats:
        m = p.match(line)
        if m:
            return m
    return None

def parse_chat(path: Path, timezone: str = "Asia/Kolkata") -> pd.DataFrame:
    tz = gettz(timezone)
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()

    records: list[ChatLine] = []
    current: ChatLine | None = None

    def flush(cur: ChatLine | None):
        if cur:
            records.append(cur)

    for raw in lines:
        raw = raw.replace("\u200e", "").rstrip("\n")
        mu = _match_any(raw, PATTERNS)
        ms = _match_any(raw, SYS_PATTERNS) if not mu else None

        if mu:
            if current: flush(current)
            d = mu.groupdict()
            dt_str = f"{d['date']} {d['time']} {d.get('ampm') or ''}".strip()
            try:
                parsed = dtparser.parse(dt_str)  # dateutil handles many formats
                ts = (pd.Timestamp(parsed).tz_localize(tz)
                      if parsed.tzinfo is None else pd.Timestamp(parsed).tz_convert(tz))
            except Exception:
                ts = None
            current = ChatLine(ts=ts, name=d["name"].strip(), msg=d["msg"], is_system=False)
        elif ms:
            if current: flush(current)
            d = ms.groupdict()
            dt_str = f"{d['date']} {d['time']} {d.get('ampm') or ''}".strip()
            try:
                parsed = dtparser.parse(dt_str)
                ts = (pd.Timestamp(parsed).tz_localize(tz)
                      if parsed.tzinfo is None else pd.Timestamp(parsed).tz_convert(tz))
            except Exception:
                ts = None
            current = ChatLine(ts=ts, name=None, msg=d["msg"], is_system=True)
        else:
            # continuation of previous message
            if current is None:
                current = ChatLine(ts=None, name=None, msg=raw, is_system=True)
            else:
                current.msg += "\n" + raw

    flush(current)

    rows = []
    for r in records:
        text = (r.msg or "").strip()
        is_media = any(m in text for m in MEDIA_MARKERS)
        emjs = [ch for ch in text if ch in emoji.EMOJI_DATA]
        rows.append({
            "timestamp": r.ts,
            "date": r.ts.date().isoformat() if r.ts else None,
            "time": r.ts.strftime("%H:%M:%S") if r.ts else None,
            "weekday": r.ts.strftime("%A") if r.ts else None,
            "hour": r.ts.hour if r.ts else None,
            "sender": r.name,
            "message": text,
            "is_system": r.is_system,
            "is_media": is_media,
            "emoji_list": "".join(emjs),
            "emoji_count": len(emjs),
        })

    df = pd.DataFrame(rows)
    # Keep only meaningful rows (non-empty messages or system markers)
    return df
