"""Exception hierarchy shared by every ResumeLens stage (contract, Section 9).

Unknown or unsupported skills are NOT errors: they are reported in
``NormalizationResult.unrecognized``.
"""

from __future__ import annotations


class ResumeLensError(Exception):
    """Base class for every error raised by ResumeLens."""


class ExtractionError(ResumeLensError):
    """Stage 1: the input given to ``extract`` is not a ``str``."""


class VocabularyError(ResumeLensError):
    """``vocabulary.json`` is missing, malformed, or violates contract Section 3.2."""


class ProfileConfigError(ResumeLensError):
    """A profile file in ``profiles/`` violates contract Section 7.3."""


class DSLValidationError(ResumeLensError):
    """Stage 4: DSL text violates the lexical or syntactic rules of the grammar.

    ``line`` and ``column`` are filled when textX reports a position.
    """

    def __init__(self, message: str, line: int | None = None, column: int | None = None) -> None:
        self.line = line
        self.column = column
        if line is not None and column is not None:
            message = f"{message} (line {line}, column {column})"
        super().__init__(message)
