#!/usr/bin/env python3
import re
import sys
import json
from datetime import datetime
from pathlib import Path

# email: keep as-is
EMAIL_RE = re.compile(r'[\w.\-+]+@[\w.\-]+\.\w+')

# phone: stricter, must have at least 7 digits AND at least 1 separator,
# and must NOT look like YYYY-MM-DD
PHONE_RE = re.compile(
    r"""
    (?!\d{4}-\d{2}-\d{2})      # not a date like 2025-10-28
    (?<!\d)                    # no digit before
    (\+?\d[\d\-\s]{6,}\d)      # core phone pattern (min ~8 chars)
    (?!\d)                     # no digit after
    """,
    re.VERBOSE,
)

REDACTED = "[REDACTED]"


def redact_markdown(src: Path, dst: Path) -> None:
    hide = False
    with src.open("r", encoding="utf-8") as f, dst.open("w", encoding="utf-8") as o:
        for line in f:
            if "<!-- INTERNAL -->" in line:
                hide = True
                continue
            if "<!-- /INTERNAL -->" in line:
                hide = False
                continue
            if hide:
                continue

            # drop explicit draft flags
            if line.strip().lower().startswith("draft:"):
                continue

            # redact PII
            line = EMAIL_RE.sub("[redacted-email]", line)
            line = PHONE_RE.sub("[redacted-phone]", line)

            o.write(line)
    print(f"[redact_public] markdown: {src} → {dst}")


def load_jsonl(path: Path):
    """Try JSONL first, then JSON array."""
    text = path.read_text(encoding="utf-8")
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    objs = []
    for ln in lines:
        try:
            objs.append(json.loads(ln))
        except json.JSONDecodeError:
            # not JSONL? fall back to single JSON
            return json.loads(text)
    return objs


def walk_redact(obj, match_substrings, redacted_keys, stats):
    # strings
    if isinstance(obj, str):
        original = obj

        # emails
        obj = EMAIL_RE.sub("[redacted-email]", obj)
        # phones
        obj = PHONE_RE.sub("[redacted-phone]", obj)

        # substring matches (tokens, bearer, etc.)
        for m in match_substrings:
            if m and m in obj:
                obj = REDACTED
                break

        if obj != original:
            stats["fields_redacted"] += 1

        return obj

    # dicts
    if isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            if k in redacted_keys:
                new_obj[k] = REDACTED
                stats["fields_redacted"] += 1
            else:
                new_obj[k] = walk_redact(v, match_substrings, redacted_keys, stats)
        return new_obj

    # lists
    if isinstance(obj, list):
        return [walk_redact(x, match_substrings, redacted_keys, stats) for x in obj]

    # everything else
    return obj


def redact_ledger(src: Path, dst: Path, match_substrings, redacted_keys):
    data = load_jsonl(src)
    # normalize to list
    if not isinstance(data, list):
        data = [data]

    stats = {"entries_total": len(data), "entries_redacted": 0, "fields_redacted": 0}
    out_lines = []

    for entry in data:
        before = json.dumps(entry, sort_keys=True)
        redacted = walk_redact(entry, match_substrings, redacted_keys, stats)
        after = json.dumps(redacted, sort_keys=True)
        if before != after:
            stats["entries_redacted"] += 1
        out_lines.append(redacted)

    meta = {
        "_meta": {
            "redacted_at": datetime.utcnow().isoformat() + "Z",
            "source": str(src),
            "matches": match_substrings,
            "keys": redacted_keys,
            "entries_total": stats["entries_total"],
            "entries_redacted": stats["entries_redacted"],
            "fields_redacted": stats["fields_redacted"],
        }
    }

    with dst.open("w", encoding="utf-8") as f:
        f.write(json.dumps(meta) + "\n")
        for obj in out_lines:
            f.write(json.dumps(obj) + "\n")

    print(
        f"[redact_public] ledger: {stats['entries_total']} entries, "
        f"{stats['fields_redacted']} fields redacted → {dst}"
    )


def main():
    if len(sys.argv) < 4:
        print("Usage:")
        print("  redact_public.py md <src_md> <dst_md>")
        print("  redact_public.py ledger <src.jsonl> <dst.jsonl> [--match ...] [--key ...]")
        sys.exit(2)

    mode = sys.argv[1]
    src = Path(sys.argv[2])
    dst = Path(sys.argv[3])

    if mode == "md":
        redact_markdown(src, dst)
    elif mode == "ledger":
        matches = []
        keys = []
        # rest args
        args = sys.argv[4:]
        i = 0
        while i < len(args):
            if args[i] == "--match" and i + 1 < len(args):
                matches.append(args[i + 1])
                i += 2
            elif args[i] == "--key" and i + 1 < len(args):
                keys.append(args[i + 1])
                i += 2
            else:
                i += 1
        redact_ledger(src, dst, matches, keys)
    else:
        print(f"unknown mode: {mode}")
        sys.exit(2)


if __name__ == "__main__":
    main()