import pytest

from resumelens import (
    Candidate,
    Education,
    Experience,
    ProfileResult,
    to_dsl,
    to_html,
    to_markdown,
    validate,
)


def _get_reference_model():
    dsl = """
    candidate "Wednesday Addams" {
      contact {
        email "wednesday@nevermore.edu"
        phone "+1 555-0199"
        link "https://github.com/wednesday"
      }
      education {
        degree "B.Sc. Computer Engineering"
        institution "Universidad Icesi"
        year "2024"
      }
      experience {
        years 3
        description "developing web applications"
      }
      skills {
        JAVASCRIPT REACT NODE_JS POSTGRESQL GIT
      }
      classification {
        FULL_STACK_DEVELOPER: ACCEPTED
        MACHINE_LEARNING_ENGINEER: REJECTED
        DEVOPS_ENGINEER: REJECTED
        DATA_ENGINEER: REJECTED
      }
    }
    """
    return validate(dsl)


def test_markdown_rendering_complete():
    model = _get_reference_model()
    md = to_markdown(model)

    assert "# Candidate Profile: Wednesday Addams" in md
    assert "## Contact Information" in md
    assert "- **Email:** wednesday@nevermore.edu" in md
    assert "- **Phone:** +1 555-0199" in md
    assert "- **Link:** https://github.com/wednesday" in md
    assert "## Education" in md
    assert "**B.Sc. Computer Engineering** — Universidad Icesi — (2024)" in md
    assert "## Professional Experience" in md
    assert "**3 years:** developing web applications" in md
    assert "## Skills" in md
    assert "`JAVASCRIPT`, `REACT`, `NODE_JS`, `POSTGRESQL`, `GIT`" in md
    assert "## Qualification Pattern Results" in md
    assert "| FULL_STACK_DEVELOPER | ACCEPTED |" in md
    assert "| MACHINE_LEARNING_ENGINEER | REJECTED |" in md


def test_html_rendering_complete():
    model = _get_reference_model()
    html_output = to_html(model)

    assert "<!DOCTYPE html>" in html_output
    assert "<title>Candidate Profile - Wednesday Addams</title>" in html_output
    assert "<h1>Candidate Profile: Wednesday Addams</h1>" in html_output
    assert 'mailto:wednesday@nevermore.edu' in html_output
    assert "B.Sc. Computer Engineering" in html_output
    assert "Universidad Icesi" in html_output
    assert "3 years:" in html_output
    assert '<span class="skill-tag">JAVASCRIPT</span>' in html_output
    assert '<span class="badge badge-accepted">ACCEPTED</span>' in html_output
    assert '<span class="badge badge-rejected">REJECTED</span>' in html_output


def test_html_security_escaping():
    candidate = Candidate(
        name='<script>alert("XSS")</script>',
        emails=['"evil"@example.com<script>'],
        education=[Education(degree='<b>BS</b> & "Eng"')],
        experience=[Experience(years=1.0, description='Dev & "Lead" <tag>')],
    )
    tokens = ["GIT"]
    results = [ProfileResult("FULL_STACK_DEVELOPER", tokens, True)]

    dsl = to_dsl(candidate, tokens, results)
    model = validate(dsl)
    html_output = to_html(model)

    assert "<script>" not in html_output
    assert "&lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;" in html_output
    assert "&lt;b&gt;BS&lt;/b&gt; &amp; &quot;Eng&quot;" in html_output
    assert "Dev &amp; &quot;Lead&quot; &lt;tag&gt;" in html_output


def test_markdown_and_html_empty_states():
    candidate = Candidate(name="")
    tokens: list[str] = []
    results = [ProfileResult("FULL_STACK_DEVELOPER", [], False)]

    dsl = to_dsl(candidate, tokens, results)
    model = validate(dsl)

    md = to_markdown(model)
    assert "*No contact information provided.*" in md
    assert "*No education records provided.*" in md
    assert "*No professional experience records provided.*" in md
    assert "*No skills identified.*" in md
    assert "| FULL_STACK_DEVELOPER | REJECTED |" in md

    html_output = to_html(model)
    assert "No contact information provided." in html_output
    assert "No education records provided." in html_output
    assert "No professional experience records provided." in html_output
    assert "No skills identified." in html_output
    assert '<span class="badge badge-rejected">REJECTED</span>' in html_output


def test_render_experience_singular_year_and_fractional():
    candidate = Candidate(
        name="Junior Dev",
        experience=[
            Experience(years=1.0, description="Junior role"),
            Experience(years=2.5, description="Mid role"),
        ],
    )
    results = [ProfileResult("FULL_STACK_DEVELOPER", [], True)]
    dsl = to_dsl(candidate, [], results)
    model = validate(dsl)

    md = to_markdown(model)
    assert "**1 year:** Junior role" in md
    assert "**2.5 years:** Mid role" in md

    html_output = to_html(model)
    assert "<strong>1 year:</strong>" in html_output
    assert "<strong>2.5 years:</strong>" in html_output


def test_render_rejects_invalid_model():
    with pytest.raises(TypeError, match="Expected a valid textX CandidateModel instance"):
        to_markdown(None)
    with pytest.raises(TypeError, match="Expected a valid textX CandidateModel instance"):
        to_html({"name": "Test"})
