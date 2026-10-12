"""Regenerate the transition diagrams of the Stage 3 automata.

Usage (from the repository root):

    python scripts/export_diagrams.py            # Mermaid + DOT + docs/diagrams/automata.md
    python scripts/export_diagrams.py --svg      # also render SVGs (needs Graphviz `dot`)
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from resumelens.diagrams import export_all  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=str(ROOT / "docs" / "diagrams"), help="output folder")
    parser.add_argument("--svg", action="store_true", help="render .svg files with Graphviz")
    args = parser.parse_args()

    files = export_all(args.out)
    if args.svg:
        dot = shutil.which("dot")
        if dot is None:
            print("Graphviz 'dot' not found; skipping SVG rendering.", file=sys.stderr)
        else:
            for source in [f for f in files if f.suffix == ".dot"]:
                target = source.with_suffix(".svg")
                subprocess.run([dot, "-Tsvg", str(source), "-o", str(target)], check=True)
                files.append(target)
    for path in files:
        print(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
