from pathlib import Path

from resumelens.app import main
from resumelens.pipeline import run
from resumelens.vocabulary import canonical_tokens

SAMPLES_DIR = Path(__file__).parent.parent / "samples"


def test_integration_wednesday_addams_full_stack():
    cv_path = SAMPLES_DIR / "wednesday_addams.txt"
    content = cv_path.read_text(encoding="utf-8")
    result = run(content)

    assert result.extraction.candidate.name == "Wednesday Addams"
    verdicts = {res.profile_id: res.accepted for res in result.classifications}
    assert verdicts["FULL_STACK_DEVELOPER"] is True
    assert verdicts["MACHINE_LEARNING_ENGINEER"] is False
    assert verdicts["DEVOPS_ENGINEER"] is False
    assert verdicts["DATA_ENGINEER"] is False


def test_integration_mary_jane_watson_ml():
    cv_path = SAMPLES_DIR / "mary_jane_watson.txt"
    content = cv_path.read_text(encoding="utf-8")
    result = run(content)

    assert result.extraction.candidate.name == "Mary Jane Watson"
    verdicts = {res.profile_id: res.accepted for res in result.classifications}
    assert verdicts["MACHINE_LEARNING_ENGINEER"] is True
    assert verdicts["FULL_STACK_DEVELOPER"] is False


def test_integration_linus_torvalds_devops():
    cv_path = SAMPLES_DIR / "linus_torvalds.txt"
    content = cv_path.read_text(encoding="utf-8")
    result = run(content)

    assert result.extraction.candidate.name == "Linus Torvalds"
    verdicts = {res.profile_id: res.accepted for res in result.classifications}
    assert verdicts["DEVOPS_ENGINEER"] is True
    assert verdicts["FULL_STACK_DEVELOPER"] is False


def test_integration_grace_hopper_data_engineer():
    cv_path = SAMPLES_DIR / "grace_hopper.txt"
    content = cv_path.read_text(encoding="utf-8")
    result = run(content)

    assert result.extraction.candidate.name == "Grace Hopper"
    verdicts = {res.profile_id: res.accepted for res in result.classifications}
    assert verdicts["DATA_ENGINEER"] is True
    assert verdicts["FULL_STACK_DEVELOPER"] is False


def test_integration_rejected_candidate():
    cv_path = SAMPLES_DIR / "rejected_candidate.txt"
    content = cv_path.read_text(encoding="utf-8")
    result = run(content)

    assert result.extraction.candidate.name == "John Doe"
    for classification in result.classifications:
        assert classification.accepted is False


def test_integration_cli_artifacts_export_for_all_samples(tmp_path):
    sample_files = list(SAMPLES_DIR.glob("*.txt"))
    assert len(sample_files) == 5

    for sample in sample_files:
        out_dir = tmp_path / sample.stem
        ret = main([str(sample), "-o", str(out_dir), "-q"])
        assert ret == 0
        assert (out_dir / f"{sample.stem}.dsl").is_file()
        assert (out_dir / f"{sample.stem}.html").is_file()
        assert (out_dir / f"{sample.stem}.md").is_file()


def test_integration_skill_permutation_invariance():
    original_text = (SAMPLES_DIR / "wednesday_addams.txt").read_text(encoding="utf-8")
    permuted_text = """Wednesday Addams
wednesday@nevermore.edu
3 years of experience developing web applications.
Technical Skills:
Git, Postgres, NodeJS, React.js, JS.
"""
    res1 = run(original_text)
    res2 = run(permuted_text)

    verdicts1 = {c.profile_id: c.accepted for c in res1.classifications}
    verdicts2 = {c.profile_id: c.accepted for c in res2.classifications}
    assert verdicts1 == verdicts2
