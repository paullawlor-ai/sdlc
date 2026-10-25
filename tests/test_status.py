from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from status import count_adrs  # noqa: E402


class StatusTests(unittest.TestCase):
    def test_proposed_adr_count_excludes_drafts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            decisions = Path(directory)
            proposed = decisions / "proposed"
            proposed.mkdir()
            proposed.joinpath("ADR-0001-draft.md").write_text(
                "## Status\n- **Current status**: Draft\n", encoding="utf-8"
            )
            proposed.joinpath("ADR-0002-proposed.md").write_text(
                "## Status\n- **Current status**: Proposed\n", encoding="utf-8"
            )
            self.assertEqual(count_adrs(decisions)["proposed"], 1)


if __name__ == "__main__":
    unittest.main()
