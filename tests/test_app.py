import pytest

from resumelens.app import main


def test_app_help_flag():
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])
    assert exc_info.value.code == 0


def test_app_nonexistent_file(capsys):
    ret = main(["non_existent_file.txt"])
    assert ret == 1
    captured = capsys.readouterr()
    assert "file not found" in captured.err


def test_app_successful_run_summary(tmp_path, capsys):
    cv_file = tmp_path / "wednesday.txt"
    cv_file.write_text(
        """
        Wednesday Addams
        3 years of experience developing web applications.
        Technical Skills:
        JS, React.js, NodeJS, Postgres, Git.
        """,
        encoding="utf-8",
    )

    ret = main([str(cv_file)])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Wednesday Addams" in captured.out
    assert "FULL_STACK_DEVELOPER" in captured.out
    assert "ACCEPTED" in captured.out


def test_app_format_flag_dsl_and_markdown(tmp_path, capsys):
    cv_file = tmp_path / "cv.txt"
    cv_file.write_text(
        """
        Dev Candidate
        Technical Skills:
        Python, Git.
        """,
        encoding="utf-8",
    )

    ret_dsl = main([str(cv_file), "--format", "dsl"])
    assert ret_dsl == 0
    captured_dsl = capsys.readouterr()
    assert 'candidate "Dev Candidate"' in captured_dsl.out

    ret_md = main([str(cv_file), "--format", "markdown"])
    assert ret_md == 0
    captured_md = capsys.readouterr()
    assert "# Candidate Profile: Dev Candidate" in captured_md.out


def test_app_output_directory_export(tmp_path):
    cv_file = tmp_path / "candidate_sample.txt"
    cv_file.write_text(
        """
        Candidate Sample
        1 year of experience programming.
        Technical Skills:
        JS, React.js, Git.
        """,
        encoding="utf-8",
    )
    out_dir = tmp_path / "output_artifacts"

    ret = main([str(cv_file), "-o", str(out_dir), "-q"])
    assert ret == 0

    assert (out_dir / "candidate_sample.dsl").is_file()
    assert (out_dir / "candidate_sample.html").is_file()
    assert (out_dir / "candidate_sample.md").is_file()

    dsl_content = (out_dir / "candidate_sample.dsl").read_text(encoding="utf-8")
    assert 'candidate "Candidate Sample"' in dsl_content
