from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from resumelens.errors import ResumeLensError
from resumelens.pipeline import run


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="resumelens",
        description="ResumeLens: Formal language-based résumé screening pipeline.",
    )
    parser.add_argument(
        "resume_path",
        type=Path,
        help="Path to the plain-text résumé file to process.",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=None,
        help="Directory to save generated artifacts (.dsl, .html, .md).",
    )
    parser.add_argument(
        "--format",
        choices=["summary", "dsl", "markdown", "html"],
        default="summary",
        help="Output format to display in stdout (default: summary).",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress console output.",
    )
    return parser


def format_summary(result) -> str:
    candidate_name = result.extraction.candidate.name or "Unnamed Candidate"
    lines: list[str] = [
        "=" * 60,
        f" ResumeLens — Candidate Analysis: {candidate_name}",
        "=" * 60,
        "",
        "Normalized Skills:",
        "  " + (", ".join(result.normalization.tokens) if result.normalization.tokens else "(None detected)"),
    ]
    if result.normalization.unrecognized:
        lines.append("Unrecognized Skills:")
        lines.append("  " + ", ".join(result.normalization.unrecognized))

    lines.append("")
    lines.append("Qualification Pattern Recognition:")
    for res in result.classifications:
        symbol = "ACCEPTED" if res.accepted else "REJECTED"
        lines.append(f"  [{symbol:<8}] {res.profile_id}")

    lines.append("=" * 60)
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.resume_path.is_file():
        sys.stderr.write(f"Error: file not found: {args.resume_path}\n")
        return 1

    try:
        content = args.resume_path.read_text(encoding="utf-8")
        result = run(content)
    except ResumeLensError as exc:
        sys.stderr.write(f"Processing error: {exc}\n")
        return 2
    except Exception as exc:
        sys.stderr.write(f"Unexpected error: {exc}\n")
        return 3

    if args.output_dir:
        out_dir = Path(args.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        stem = args.resume_path.stem
        (out_dir / f"{stem}.dsl").write_text(result.dsl_text, encoding="utf-8")
        (out_dir / f"{stem}.html").write_text(result.html, encoding="utf-8")
        (out_dir / f"{stem}.md").write_text(result.markdown, encoding="utf-8")

    if not args.quiet:
        if args.format == "summary":
            sys.stdout.write(format_summary(result) + "\n")
        elif args.format == "dsl":
            sys.stdout.write(result.dsl_text + "\n")
        elif args.format == "markdown":
            sys.stdout.write(result.markdown + "\n")
        elif args.format == "html":
            sys.stdout.write(result.html + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
