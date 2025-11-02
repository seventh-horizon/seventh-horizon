import sys
from pathlib import Path

# make repo root importable
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from scripts import redact_public  # import the whole module


def test_markdown_redaction_basic(tmp_path: Path):
    src = tmp_path / "in.md"
    dst = tmp_path / "out.md"

    src.write_text(
        """# Title
Visible line
<!-- INTERNAL -->
secret line
another secret line
<!-- /INTERNAL -->
Draft: true
contact: test@example.com
phone: +1 555-123-4567
""",
        encoding="utf-8",
    )

    # simulate CLI: python scripts/redact_public.py md in.md out.md
    sys.argv = ["redact_public.py", "md", str(src), str(dst)]
    redact_public.main()

    out = dst.read_text(encoding="utf-8")

    # INTERNAL block removed
    assert "secret line" not in out
    assert "another secret line" not in out

    # Draft flag removed
    assert "Draft:" not in out

    # Email redacted
    assert "[redacted-email]" in out

    # Phone redacted (with current regex)
    assert "[redacted-phone]" in out

    # Regular content kept
    assert "Visible line" in out
    assert "# Title" in out