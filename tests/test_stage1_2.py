"""Integration tests for ResumeLens Stages 1 and 2."""

from pathlib import Path

import pytest

from resumelens.extraction import extract
from resumelens.models import ExtractionResult, NormalizationResult
from resumelens.normalization import normalize
from resumelens.vocabulary import default_vocabulary

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "samples"
SAMPLE_FILES = sorted(SAMPLES_DIR.glob("*"))
SAMPLE_EXPECTATIONS: dict[str, tuple[list[str], list[str], dict[str, str], list[str]]] = {
    "grace_hopper.txt": (
        ["Python", "SQL", "Spark", "Airflow", "Kafka", "Git"],
        ["PYTHON", "SQL", "SPARK", "AIRFLOW", "KAFKA", "GIT"],
        {
            "Python": "PYTHON",
            "SQL": "SQL",
            "Spark": "SPARK",
            "Airflow": "AIRFLOW",
            "Kafka": "KAFKA",
            "Git": "GIT",
        },
        [],
    ),
    "here_dataset.md": ([], [], {}, []),
    "linus_torvalds.txt": (
        ["Linux", "Git", "CI/CD", "Docker", "Kubernetes", "AWS"],
        ["LINUX", "GIT", "CI_CD", "DOCKER", "KUBERNETES", "AWS"],
        {
            "Linux": "LINUX",
            "Git": "GIT",
            "CI/CD": "CI_CD",
            "Docker": "DOCKER",
            "Kubernetes": "KUBERNETES",
            "AWS": "AWS",
        },
        [],
    ),
    "mary_jane_watson.txt": (
        ["Python", "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "SQL", "Git"],
        ["PYTHON", "PANDAS", "NUMPY", "SCIKIT_LEARN", "TENSORFLOW", "SQL", "GIT"],
        {
            "Python": "PYTHON",
            "Pandas": "PANDAS",
            "NumPy": "NUMPY",
            "Scikit-learn": "SCIKIT_LEARN",
            "TensorFlow": "TENSORFLOW",
            "SQL": "SQL",
            "Git": "GIT",
        },
        [],
    ),
    "rejected_candidate.txt": (
        ["Figma", "Photoshop", "Microsoft Word", "Jira", "Git"],
        ["GIT"],
        {"Git": "GIT"},
        ["Figma", "Photoshop", "Microsoft Word", "Jira"],
    ),
    "wednesday_addams.txt": (
        ["JS", "React.js", "NodeJS", "Postgres", "Git"],
        ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"],
        {
            "JS": "JAVASCRIPT",
            "React.js": "REACT",
            "NodeJS": "NODE_JS",
            "Postgres": "POSTGRESQL",
            "Git": "GIT",
        },
        [],
    ),
}


def assert_stage_invariants(text: str, raw_skills: list[str]) -> None:
    """Check the shared output, vocabulary, determinism, and purity contracts."""
    original_text = text
    extraction = extract(text)
    result = normalize(extraction.raw_skills)

    assert isinstance(extraction, ExtractionResult)
    assert isinstance(extraction.raw_skills, list)
    assert all(isinstance(raw, str) for raw in extraction.raw_skills)
    assert isinstance(result, NormalizationResult)
    assert isinstance(result.tokens, list)
    assert isinstance(result.mapping, dict)
    assert isinstance(result.unrecognized, list)
    assert set(result.mapping) | set(result.unrecognized) == set(raw_skills)
    assert set(result.mapping).isdisjoint(result.unrecognized)
    assert set(result.tokens) <= set(default_vocabulary())
    assert len(result.tokens) == len(set(result.tokens))
    assert text == original_text
    assert extract(text) == extraction
    assert normalize(extraction.raw_skills) == result


def test_wednesday_addams_assignment_fragment() -> None:
    """Normalize the assignment's Wednesday Addams fragment exactly."""
    text = (
        "Wednesday Addams\n"
        "3 years of experience developing web applications.\n"
        "Technical Skills:\n"
        "JS, React.js, NodeJS, Postgres, Git."
    )
    extraction = extract(text)
    result = normalize(extraction.raw_skills)

    assert extraction.raw_skills == ["JS", "React.js", "NodeJS", "Postgres", "Git"]
    assert result.tokens == ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]
    assert result.unrecognized == []
    assert_stage_invariants(text, extraction.raw_skills)


def test_mary_jane_watson_assignment_fragment() -> None:
    """Normalize the assignment's Mary Jane Watson fragment exactly."""
    text = (
        "Mary Jane Watson\n"
        "2 years of experience developing predictive models and data-processing pipelines.\n"
        "Technical Skills:\n"
        "Python, Pandas, NumPy, Scikit-learn, TensorFlow, SQL, Git."
    )
    extraction = extract(text)
    result = normalize(extraction.raw_skills)

    assert extraction.raw_skills == [
        "Python",
        "Pandas",
        "NumPy",
        "Scikit-learn",
        "TensorFlow",
        "SQL",
        "Git",
    ]
    assert result.tokens == [
        "PYTHON",
        "PANDAS",
        "NUMPY",
        "SCIKIT_LEARN",
        "TENSORFLOW",
        "SQL",
        "GIT",
    ]
    assert_stage_invariants(text, extraction.raw_skills)


@pytest.mark.parametrize("sample_path", SAMPLE_FILES, ids=lambda path: path.name)
def test_every_sample_has_exact_stage1_and_stage2_results(sample_path: Path) -> None:
    """Check the exact expected extraction and normalization for each sample."""
    text = sample_path.read_text(encoding="utf-8")
    expected_raw, expected_tokens, expected_mapping, expected_unrecognized = (
        SAMPLE_EXPECTATIONS[sample_path.name]
    )
    extraction = extract(text)
    result = normalize(extraction.raw_skills)

    assert extraction.raw_skills == expected_raw
    assert result.tokens == expected_tokens
    assert result.mapping == expected_mapping
    assert result.unrecognized == expected_unrecognized
    assert_stage_invariants(text, extraction.raw_skills)


@pytest.mark.parametrize("sample_path", SAMPLE_FILES, ids=lambda path: path.name)
def test_every_sample_has_expected_values_entry(sample_path: Path) -> None:
    """Fail clearly when a newly added sample lacks expected values."""
    assert sample_path.name in SAMPLE_EXPECTATIONS, (
        f"New sample {sample_path.name!r} has no expected Stage 1/2 values; "
        "add it to SAMPLE_EXPECTATIONS."
    )


def test_out_of_order_skills_keep_first_appearance_order() -> None:
    """Stage 2 must not apply Stage 2b profile sorting."""
    text = "Skills: Git, NodeJS, JS, Postgres, React.js"
    extraction = extract(text)
    result = normalize(extraction.raw_skills)

    assert result.tokens == ["GIT", "NODE_JS", "JAVASCRIPT", "POSTGRESQL", "REACT"]
    assert_stage_invariants(text, extraction.raw_skills)


def test_noise_and_unknown_skills_are_traceable() -> None:
    """Unknown skills are excluded from tokens and retained as unrecognized."""
    text = "Skills: JS, Figma, Docker, Git"
    extraction = extract(text)
    result = normalize(extraction.raw_skills)

    assert result.tokens == ["JAVASCRIPT", "DOCKER", "GIT"]
    assert result.unrecognized == ["Figma"]
    assert_stage_invariants(text, extraction.raw_skills)


def test_duplicate_javascript_spellings_map_to_one_token() -> None:
    """Extraction preserves duplicate spellings while normalization deduplicates."""
    text = "Skills: js, JS, Javascript"
    extraction = extract(text)
    result = normalize(extraction.raw_skills)

    assert extraction.raw_skills == ["js", "JS", "Javascript"]
    assert result.tokens == ["JAVASCRIPT"]
    assert result.mapping == {
        "js": "JAVASCRIPT",
        "JS": "JAVASCRIPT",
        "Javascript": "JAVASCRIPT",
    }
    assert_stage_invariants(text, extraction.raw_skills)


def test_surface_variations_preserve_raw_mapping_keys() -> None:
    """Normalization keys remain the exact strings returned by extraction."""
    text = "Technical Skills:\nReact.js; scikit learn | CI/CD\nPostgres."
    extraction = extract(text)
    result = normalize(extraction.raw_skills)

    assert extraction.raw_skills == ["React.js", "scikit learn", "CI/CD", "Postgres"]
    assert set(result.mapping) == set(extraction.raw_skills)
    assert result.tokens == ["REACT", "SCIKIT_LEARN", "CI_CD", "POSTGRESQL"]
    assert_stage_invariants(text, extraction.raw_skills)


@pytest.mark.parametrize(
    ("text", "expected_raw", "expected_tokens"),
    [
        ("I build APIs with React.js and Git at work.", ["React.js", "Git"], ["REACT", "GIT"]),
        ("the rest of the team uses ML and TF", [], []),
    ],
    ids=["free-text-known-skills", "free-text-short-ambiguous-aliases"],
)
def test_fallback_skill_extraction(
    text: str, expected_raw: list[str], expected_tokens: list[str]
) -> None:
    """Use vocabulary fallback for clear free-text skills, not short aliases."""
    extraction = extract(text)
    result = normalize(extraction.raw_skills)

    assert extraction.raw_skills == expected_raw
    assert result.tokens == expected_tokens
    assert_stage_invariants(text, extraction.raw_skills)


@pytest.mark.parametrize("text", ["", "   ", "\n\t  "])
def test_empty_and_whitespace_only_text(text: str) -> None:
    """Empty input produces empty Stage 1/2 skill outputs."""
    extraction = extract(text)
    result = normalize(extraction.raw_skills)

    assert extraction.raw_skills == []
    assert result.tokens == []
    assert result.mapping == {}
    assert result.unrecognized == []
    assert_stage_invariants(text, extraction.raw_skills)
