"""ResumeLens: formal language-based résumé screening.

Pipeline (see docs/contracts.md):

1. Extraction        -> regular expressions      (extraction.py)
2. Normalization     -> finite-state transducers (normalization.py)
2b. Sorting/filtering -> profile canonical order (sorting.py)
3. Recognition       -> finite automata          (recognition.py)
4. Candidate language -> context-free grammar    (dsl.py, candidate.tx)
4b. Visualization    -> HTML / Markdown          (render.py)
"""

from resumelens.app import main
from resumelens.dsl import to_dsl, validate
from resumelens.errors import (
    DSLValidationError,
    ExtractionError,
    ProfileConfigError,
    ResumeLensError,
    VocabularyError,
)
from resumelens.models import (
    Candidate,
    Education,
    Experience,
    ExtractionResult,
    NormalizationResult,
    PipelineResult,
    ProfileResult,
)
from resumelens.pipeline import run
from resumelens.render import to_html, to_markdown

__version__ = "0.1.0"

__all__ = [
    "Candidate",
    "DSLValidationError",
    "Education",
    "Experience",
    "ExtractionError",
    "ExtractionResult",
    "NormalizationResult",
    "PipelineResult",
    "ProfileConfigError",
    "ProfileResult",
    "ResumeLensError",
    "VocabularyError",
    "__version__",
    "main",
    "run",
    "to_dsl",
    "to_html",
    "to_markdown",
    "validate",
]
