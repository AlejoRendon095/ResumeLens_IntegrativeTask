from __future__ import annotations

import html
from typing import Any


def _format_years(years: float) -> str:
    if years.is_integer():
        val = int(years)
    else:
        val = years
    unit = "year" if val == 1 else "years"
    return f"{val} {unit}"


def to_markdown(model: Any) -> str:
    if not hasattr(model, "name") or not hasattr(model, "classification"):
        raise TypeError("Expected a valid textX CandidateModel instance.")

    lines: list[str] = []
    name = model.name.strip() if model.name else "Unnamed Candidate"
    lines.append(f"# Candidate Profile: {name}\n")

    lines.append("## Contact Information")
    contact = getattr(model, "contact", None)
    contact_items: list[str] = []
    if contact:
        for email in getattr(contact, "emails", []):
            contact_items.append(f"- **Email:** {email}")
        for phone in getattr(contact, "phones", []):
            contact_items.append(f"- **Phone:** {phone}")
        for link in getattr(contact, "links", []):
            contact_items.append(f"- **Link:** {link}")
    if contact_items:
        lines.extend(contact_items)
    else:
        lines.append("*No contact information provided.*")
    lines.append("")

    lines.append("## Education")
    education_records = getattr(model, "education", [])
    if education_records:
        for edu in education_records:
            parts: list[str] = []
            if edu.degree:
                parts.append(f"**{edu.degree}**")
            if edu.institution:
                parts.append(edu.institution)
            if edu.year:
                parts.append(f"({edu.year})")
            if parts:
                lines.append(f"- {' — '.join(parts)}")
            else:
                lines.append("- *(Empty education record)*")
    else:
        lines.append("*No education records provided.*")
    lines.append("")

    lines.append("## Professional Experience")
    experience_records = getattr(model, "experience", [])
    if experience_records:
        for exp in experience_records:
            parts = []
            if getattr(exp, "years", 0.0) > 0:
                parts.append(f"**{_format_years(exp.years)}:**")
            if exp.description:
                parts.append(exp.description)
            if parts:
                lines.append(f"- {' '.join(parts)}")
            else:
                lines.append("- *(Empty experience record)*")
    else:
        lines.append("*No professional experience records provided.*")
    lines.append("")

    lines.append("## Skills")
    skills_block = getattr(model, "skills", None)
    skills = getattr(skills_block, "skills", []) if skills_block else []
    if skills:
        lines.append(", ".join(f"`{token}`" for token in skills))
    else:
        lines.append("*No skills identified.*")
    lines.append("")

    lines.append("## Qualification Pattern Results")
    lines.append("| Profile | Verdict |")
    lines.append("|---|---|")
    classification = getattr(model, "classification", None)
    entries = getattr(classification, "entries", []) if classification else []
    for entry in entries:
        lines.append(f"| {entry.profile_id} | {entry.verdict} |")
    lines.append("")

    return "\n".join(lines).strip() + "\n"


def to_html(model: Any) -> str:
    if not hasattr(model, "name") or not hasattr(model, "classification"):
        raise TypeError("Expected a valid textX CandidateModel instance.")

    raw_name = model.name.strip() if model.name else "Unnamed Candidate"
    esc_name = html.escape(raw_name, quote=True)

    css = """
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      line-height: 1.6;
      color: #24292e;
      max-width: 800px;
      margin: 40px auto;
      padding: 0 20px;
    }
    h1 {
      border-bottom: 2px solid #eaecef;
      padding-bottom: 0.3em;
      color: #1a1e22;
    }
    h2 {
      border-bottom: 1px solid #eaecef;
      padding-bottom: 0.3em;
      margin-top: 24px;
      color: #24292e;
    }
    ul {
      padding-left: 20px;
    }
    .skill-tag {
      display: inline-block;
      background-color: #f1f8ff;
      color: #0366d6;
      border: 1px solid #c8e1ff;
      border-radius: 4px;
      padding: 2px 8px;
      margin: 3px 4px;
      font-family: monospace;
      font-size: 0.9em;
    }
    table {
      border-collapse: collapse;
      width: 100%;
      margin: 16px 0;
    }
    th, td {
      border: 1px solid #dfe2e5;
      padding: 8px 14px;
      text-align: left;
    }
    th {
      background-color: #f6f8fa;
    }
    .badge {
      display: inline-block;
      padding: 3px 10px;
      border-radius: 12px;
      font-size: 0.85em;
      font-weight: 600;
    }
    .badge-accepted {
      background-color: #dcffe4;
      color: #155724;
      border: 1px solid #c3e6cb;
    }
    .badge-rejected {
      background-color: #f8d7da;
      color: #721c24;
      border: 1px solid #f5c6cb;
    }
    .empty-state {
      color: #6a737d;
      font-style: italic;
    }
    """.strip()

    sections: list[str] = []

    sections.append(f"  <h1>Candidate Profile: {esc_name}</h1>")

    sections.append("  <section>")
    sections.append("    <h2>Contact Information</h2>")
    contact = getattr(model, "contact", None)
    c_items: list[str] = []
    if contact:
        for email in getattr(contact, "emails", []):
            esc = html.escape(email, quote=True)
            c_items.append(f'<li><strong>Email:</strong> <a href="mailto:{esc}">{esc}</a></li>')
        for phone in getattr(contact, "phones", []):
            esc = html.escape(phone, quote=True)
            c_items.append(f'<li><strong>Phone:</strong> {esc}</li>')
        for link in getattr(contact, "links", []):
            esc = html.escape(link, quote=True)
            c_items.append(f'<li><strong>Link:</strong> <a href="{esc}">{esc}</a></li>')
    if c_items:
        sections.append("    <ul>")
        for item in c_items:
            sections.append(f"      {item}")
        sections.append("    </ul>")
    else:
        sections.append('    <p class="empty-state">No contact information provided.</p>')
    sections.append("  </section>")

    sections.append("  <section>")
    sections.append("    <h2>Education</h2>")
    education_records = getattr(model, "education", [])
    if education_records:
        sections.append("    <ul>")
        for edu in education_records:
            parts = []
            if edu.degree:
                parts.append(f"<strong>{html.escape(edu.degree, quote=True)}</strong>")
            if edu.institution:
                parts.append(html.escape(edu.institution, quote=True))
            if edu.year:
                parts.append(f"({html.escape(edu.year, quote=True)})")
            content = " — ".join(parts) if parts else "<em>(Empty education record)</em>"
            sections.append(f"      <li>{content}</li>")
        sections.append("    </ul>")
    else:
        sections.append('    <p class="empty-state">No education records provided.</p>')
    sections.append("  </section>")

    sections.append("  <section>")
    sections.append("    <h2>Professional Experience</h2>")
    experience_records = getattr(model, "experience", [])
    if experience_records:
        sections.append("    <ul>")
        for exp in experience_records:
            parts = []
            if getattr(exp, "years", 0.0) > 0:
                parts.append(f"<strong>{_format_years(exp.years)}:</strong>")
            if exp.description:
                parts.append(html.escape(exp.description, quote=True))
            content = " ".join(parts) if parts else "<em>(Empty experience record)</em>"
            sections.append(f"      <li>{content}</li>")
        sections.append("    </ul>")
    else:
        sections.append('    <p class="empty-state">No professional experience records provided.</p>')
    sections.append("  </section>")

    sections.append("  <section>")
    sections.append("    <h2>Skills</h2>")
    skills_block = getattr(model, "skills", None)
    skills = getattr(skills_block, "skills", []) if skills_block else []
    if skills:
        sections.append('    <div class="skills-container">')
        for token in skills:
            esc = html.escape(token, quote=True)
            sections.append(f'      <span class="skill-tag">{esc}</span>')
        sections.append("    </div>")
    else:
        sections.append('    <p class="empty-state">No skills identified.</p>')
    sections.append("  </section>")

    sections.append("  <section>")
    sections.append("    <h2>Qualification Pattern Results</h2>")
    sections.append("    <table>")
    sections.append("      <thead>")
    sections.append("        <tr><th>Profile</th><th>Verdict</th></tr>")
    sections.append("      </thead>")
    sections.append("      <tbody>")
    classification = getattr(model, "classification", None)
    entries = getattr(classification, "entries", []) if classification else []
    for entry in entries:
        pid = html.escape(entry.profile_id, quote=True)
        v = entry.verdict
        badge_cls = "badge-accepted" if v == "ACCEPTED" else "badge-rejected"
        sections.append(
            f'        <tr><td>{pid}</td><td><span class="badge {badge_cls}">{html.escape(v, quote=True)}</span></td></tr>'
        )
    sections.append("      </tbody>")
    sections.append("    </table>")
    sections.append("  </section>")

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Candidate Profile - {esc_name}</title>
  <style>
{css}
  </style>
</head>
<body>
{chr(10).join(sections)}
</body>
</html>
"""
    return html_content


__all__ = [
    "to_html",
    "to_markdown",
]
