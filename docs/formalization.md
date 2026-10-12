# Formalization of Computational Models

This document presents the formal definitions and theoretical models used across the ResumeLens pipeline.

---

# Formalization of Regular Expressions 

# Part 1. Stage 1: Regular expressions

## 1.1 Role of Stage 1 in the pipeline

Stage 1 receives the raw text of a résumé and returns an `ExtractionResult`: the candidate data (name, emails, phones, links, education, experience) and `raw_skills`, the list of skill strings found in the text.

Stage 1 only **detects** candidate strings. It does not decide that `JS` and `JavaScript` are the same technology (that is the job of the transducers in Stage 2), and it does not decide whether the candidate satisfies a professional profile (that is Stage 3). For that reason:

* Skills keep their **original spelling and case**, their **order of appearance**, and their **duplicates**.
* `extract()` is **deterministic** and pure: the same text always produces the same result, and the input is never modified.
* The vocabulary (`vocabulary.json`) is read at runtime only by the fallback scan (section 1.4.9), to find known skill spellings when a résumé has no skills section.
* Empty or unparsable text returns an `ExtractionResult` with empty fields, never `None`. A non-`str` input raises `ExtractionError`.

## 1.2 Why regular expressions fit this stage

The information extracted in Stage 1 follows **local surface patterns**: an `@` between two names, groups of digits, a degree keyword, a heading followed by a list, a separator between items. Recognizing each of them does not require remembering an unbounded amount of context or matching nested structures, so each one is describable by a regular language. A finite automaton, which is what the `re` engine compiles a pattern into for this kind of expression, is enough. More structured information (the candidate profile as a whole, with repeated and nested elements) is left to the context-free grammar of Stage 4.

## 1.3 Notation

To describe the languages formally, the following notation is used:

* `a | b` union, `ab` concatenation, `a*` zero or more, `a+` one or more, `a?` optional, `a{m,n}` between `m` and `n` repetitions.
* `[...]` a set of characters (a finite union of symbols).
* `WS` any whitespace character, `D` a decimal digit.
* `L` a Unicode letter. In the code it is written `[^\W\d_]`: "word character that is neither a digit nor an underscore".
* `¬W` means that the neighbouring character must **not** be a word character. It is checked with a lookaround, which does not consume characters.

Python's `re` module offers features beyond textbook regular expressions: flags (`(?i)`, `(?m)`, `(?s)`), lookahead and lookbehind assertions, and named groups. In this stage:

* **Flags** only change which symbols are considered equal (case) or what `^`, `$` and `.` match. They do not add recognition power.
* **Named groups** only label a part of the match for extraction. They do not change the language.
* **Lookarounds** used here have **fixed, bounded width** and check a neighbouring character or a bounded pattern. They can be expressed as an intersection or complement with a regular language, so the language remains regular in practice. No backreferences are used.

## 1.4 The patterns

Each regular expression is defined as a compiled module-level constant in `src/resumelens/extraction.py`. The patterns below are shown as written in the code.

### Summary

| Constant | Information | Recognizes |
|---|---|---|
| `EMAIL_RE` | Email addresses | Local part, `@`, and a domain with at least one dot |
| `PHONE_RE` | Phone numbers | Optional country code, 3-digit or parenthesized area code, then 3 and 4 digits |
| `LINK_RE` | Links | `http(s)` URLs, GitHub paths and LinkedIn profile paths |
| `NAME_RE` | Candidate name | 2 to 4 words made of letters |
| `EXPERIENCE_RE` | Professional experience | A number of years, an experience phrase and a description (English or Spanish) |
| `EDUCATION_RE` | Academic qualifications | A line with a degree keyword, optional institution and optional year |
| `SKILLS_SECTION_RE` | Skills section | A skills heading and its body |
| `_SKILL_SPLIT_RE` | Skill separators | Commas, semicolons, vertical bars, bullets and line breaks |
| Alias fallback | Skills in free text | Known vocabulary aliases as whole words |

### 1.4.1 `EMAIL_RE`

```python
EMAIL_RE = re.compile(r"(?i)\b[a-z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-z0-9-]+(?:\.[a-z0-9-]+)+\b")
```

**Pieces.**

* `(?i)`: case-insensitive.
* `\b`: word boundary at both ends of the address.
* `[a-z0-9.!#$%&'*+/=?^_`{|}~-]+`: one or more characters allowed in the local part.
* `@`: the literal at-sign.
* `[a-z0-9-]+`: the first domain label.
* `(?:\.[a-z0-9-]+)+`: one or more further labels, each preceded by a dot.

**Language.** An email-like string with a non-empty local part and a domain with at least one dot. Formally:

```
L+ "@" D+ ("." D+)+      with L = [a-z0-9.!#$%&'*+/=?^_`{|}~-] and D = [a-z0-9-]
```

The boundary `\b` and the case flag do not extend the language beyond a regular one.

**Accepted:** `jose@example.com`, `a+b@x.co` (a `+` is allowed in the local part), `second@example.org`.

**Rejected:** `jose@example` (the domain has no dot), `x@y` (same reason), `@example.com` (empty local part).

**Limitations.** It is meant for extraction, not validation: it accepts some invalid addresses (consecutive dots in the local part, labels starting or ending with `-`), it does not support quoted local parts, and it does not check that the domain exists.

### 1.4.2 `PHONE_RE`

```python
PHONE_RE = re.compile(r"(?<!\w)(?:\+\d{1,3}[\s-]?)?(?:\(\d{2,4}\)|\d{3})[\s-]?\d{3}[\s-]?\d{4}(?!\w)")
```

**Pieces.**

* `(?<!\w)` and `(?!\w)`: the match must not touch a word character on either side.
* `(?:\+\d{1,3}[\s-]?)?`: an optional country code such as `+57`, with an optional space or hyphen.
* `(?:\(\d{2,4}\)|\d{3})`: either a parenthesized area code of 2 to 4 digits, or 3 digits.
* `[\s-]?\d{3}[\s-]?\d{4}`: 3 digits, an optional separator, and 4 digits.

**Language.**

```
¬W ("+" D{1,3} S?)? ("(" D{2,4} ")" | D{3}) S? D{3} S? D{4} ¬W      with S = [\s-]
```

**Accepted:** `+57 300 123 4567`, `(300) 123-4567`, `300-123-4567`.

**Rejected:** `123` (too short), `300123456` (only nine digits), `abc300-123-4567x` (the digits touch word characters).

**Limitations.** It accepts any digit string with this shape, for instance a long numeric identifier, and it does not check real numbering plans. Extensions (`ext. 12`) and other national layouts are not supported.

### 1.4.3 `LINK_RE`

```python
LINK_RE = re.compile(
    r"(?i)(?<![\w@])(?:https?://)?(?:www\.)?"
    r"(?:github\.com/[^\s,;|]+|linkedin\.com/in/[^\s,;|]+|https?://[^\s,;|]+)"
)
```

**Pieces.**

* `(?<![\w@])`: the link cannot start right after a word character or an `@` (this avoids matching inside an email address).
* `(?:https?://)?(?:www\.)?`: an optional protocol and an optional `www.`.
* Three alternatives: a GitHub path, a LinkedIn profile path, or any `http(s)` URL.
* `[^\s,;|]+`: the body continues until whitespace, a comma, a semicolon or a vertical bar.

**Language.**

```
¬[\w@] ("http" "s"? "://")? ("www.")?
( "github.com/" X+ | "linkedin.com/in/" X+ | "http" "s"? "://" X+ )
with X = any character except whitespace, ",", ";" and "|"
```

After matching, the extractor removes trailing sentence punctuation (`.,;:!?)]}`) from each link.

**Accepted:** `https://example.com`, `github.com/jose`, `linkedin.com/in/jose`.

**Rejected:** `ftp://example.com` (only `http` and `https` are supported), `github.com` (no path), `text@github.com/user` (preceded by `@`).

**Limitations.** Arbitrary domains without a protocol (`example.com`) are not captured, and the URL is not validated beyond its shape.

### 1.4.4 `NAME_RE`

```python
NAME_RE = re.compile(
    r"^[^\W\d_]+(?:[-'][^\W\d_]+)?"
    r"(?:\s+[^\W\d_]+(?:[-'][^\W\d_]+)?){1,3}$",
    re.UNICODE,
)
```

**Pieces.**

* `^` and `$`: the whole line must match.
* `[^\W\d_]+`: one or more Unicode letters.
* `(?:[-'][^\W\d_]+)?`: an optional hyphenated or apostrophe part (`O'Connor`).
* `(?:\s+ ... ){1,3}`: between one and three more words, so the name has 2 to 4 words.

**Language.**

```
W ([-'] W)? ( WS+ W ([-'] W)? ){1,3}      with W = L+
```

**Accepted:** `José Peña`, `Ada Lovelace`, `John O'Connor`.

**Rejected:** `Ada` (only one word), `John 123` (digits), `John_Smith` (underscore, and a single word).

**How it is used.** The extractor applies `NAME_RE` only to the **first non-empty line** of the résumé; if that line is not a name, the name stays `""`.

**Limitations.** One-word names, names with more than four words and names with titles or periods (`Dr. Ada Lovelace`) are not recognized. Any first line made of 2 to 4 letter-only words (for example a job title) is a false positive.

### 1.4.5 `EXPERIENCE_RE`

```python
EXPERIENCE_RE = re.compile(
    r"(?im)^\s*(?P<years>\d+(?:\.\d+)?)\s*\+?\s*(?:years?|años?)"
    r"\s+(?:of\s+|de\s+)?(?:experience|experiencia)\s*(?:en\s+)?"
    r"(?P<description>[^.\r\n]+)\.?\s*$"
)
```

**Pieces.**

* `(?im)`: case-insensitive and multiline (so `^` and `$` delimit a line).
* `(?P<years>\d+(?:\.\d+)?)`: an integer or decimal number, captured as `years`.
* `\s*\+?\s*`: an optional plus sign (`5+ years`).
* `(?:years?|años?)`: the unit word in English or Spanish.
* `(?:of\s+|de\s+)?(?:experience|experiencia)`: an optional connector and the word for experience.
* `(?:en\s+)?`: an optional Spanish connector.
* `(?P<description>[^.\r\n]+)`: the description, captured until a period or the end of the line.

**Language.**

```
WS* N WS* "+"? ("year"|"years"|"año"|"años") WS+ (("of"|"de") WS+)?
("experience"|"experiencia") WS* ("en" WS+)? T+ "."? WS*
with N = D+ ("." D+)? and T = any character except ".", CR and LF
```

The extractor converts `years` to a `float` and strips the `description`.

**Accepted:** `3 years of experience developing web applications.`, `5+ years of experience leading teams.`, `3 años de experiencia en análisis de datos.`

**Rejected:** `years of experience` (no number), `3 years of experience.` (no description), `3 months of experience coding.` (only years are supported).

**Limitations.** The statement must start its line. Descriptions cannot contain an inner period. Written numbers (`three years`), months and phrasings such as "over 3 years" are not supported.

### 1.4.6 `EDUCATION_RE`

```python
EDUCATION_RE = re.compile(
    r"(?im)^\s*(?P<degree>.*?\b(?:B\.?\s*Sc\.?|M\.?\s*Sc\.?|Ph\.?D\.?|"
    r"bachelor(?:'s)?|master(?:'s)?|engineer(?:ing)?|ingenier[ií]a|"
    r"licenciatura|doctorate|degree)\b.*?)"
    r"(?:\s*[-,|]\s*|\s+)(?P<institution>(?:Universidad|University(?:\s+of)?)[^,|;\r\n]*?)?"
    r"(?:\s*[-,|]?\s*(?P<year>\d{4}(?:\s*-\s*\d{4})?))?\s*$"
)
```

**Pieces.**

* `(?P<degree>.*?\b(?:...)\b.*?)`: a line fragment that contains one degree keyword (BSc, MSc, PhD, bachelor, master, engineer, engineering, ingeniería, licenciatura, doctorate, degree).
* `(?:\s*[-,|]\s*|\s+)`: a **mandatory separator** (a hyphen, comma or bar, or whitespace) after the degree.
* `(?P<institution>...)?`: an optional institution that starts with `Universidad` or `University` (`University of`).
* `(?P<year>\d{4}(?:\s*-\s*\d{4})?)`: an optional year or year range.
* `\s*$`: the end of the line.

**Language.** A line with a degree keyword, followed by a separator, optionally followed by a university-style institution and optionally by a year or range:

```
WS* DEGREE_TEXT SEP (INSTITUTION)? ( WS* [-,|]? WS* YEAR )? WS*
with SEP = (WS* [-,|] WS* | WS+) and YEAR = D{4} (WS* "-" WS* D{4})?
```

**How it is used.** Besides the pattern, `extract()` discards a match whose degree is only `Engineer` or `Engineering` unless the line also has an institution or a year. This avoids reading a job title such as "Software Engineer" as education.

**Accepted:** `B.Sc. Computer Science - Universidad de los Andes - 2020-2024` (degree `B.Sc. Computer Science`, institution `Universidad de los Andes`, year `2020-2024`), `PhD University X`, `Master's Degree - University of Toronto - 2024`.

**Rejected:** `Computer Science - College X` (no degree keyword), `B.Sc. Computer Science - 20` (the year needs four digits), `B.Sc. Computer Science` (a degree line with **no separator, institution or year** after it; see the limitations).

**Limitations.** Only institutions that begin with `Universidad` or `University` are recognized. Because the pattern requires a separator after the degree, a line that contains **only** the degree (`B.Sc. Computer Science`, `Bachelor in Computer Science`) is not captured, unless it has trailing whitespace. Institution extraction is a best effort.

### 1.4.7 `SKILLS_SECTION_RE`

```python
SKILLS_SECTION_RE = re.compile(
    r"(?ims)^[ \t]*(?:technical skills|skills|tech stack)[ \t]*:?[ \t]*(?:\r?\n)?"
    r"(?P<body>.*?)(?=\r?\n[ \t]*\r?\n"
    r"|\r?\n[ \t]*[^:\r\n]{1,60}[ \t]*:[ \t]*(?:\r?\n|$)"
    r"|\r?\n[ \t]*(?:education|experience|projects|languages|certifications|contact|summary)"
    r"[ \t]*(?:\r?$)|\Z)"
)
```

**Pieces.**

* `(?ims)`: case-insensitive, multiline, and `.` also matches line breaks.
* `^[ \t]*(?:technical skills|skills|tech stack)[ \t]*:?`: a heading, with an optional colon.
* `(?P<body>.*?)`: the body, taken lazily (the shortest text up to a terminator).
* The lookahead `(?= ... )` ends the body at the first of: a blank line, a new heading that ends with a colon, a known heading without colon (`education`, `experience`, `projects`, `languages`, `certifications`, `contact`, `summary`), or the end of the text.

**Language.** A skills heading followed by the shortest body that precedes one of the terminators above.

**Accepted:** `Technical Skills:\nJS, React.js` (body `JS, React.js`), `Skills: Python\n\nEducation` (body `Python`, stopped by the blank line), `Technical Skills:\nPython, Git\nEducation\nB.Sc. X` (body `Python, Git`, stopped by the heading `Education` without colon).

**Rejected as a heading:** `Technical Skill` (singular), `Abilities:` (not one of the three accepted headings).

**Limitations.** Only three heading names are recognized. The body stops at any short line that ends with a colon, even if it is not a heading. If no terminator appears, the body extends to the end of the text. The pattern does not check that each item is a known skill.

### 1.4.8 `_SKILL_SPLIT_RE`

```python
_SKILL_SPLIT_RE = re.compile(r"[,;|\u2022\r\n]+")
```

**Pieces.** A character class with the separators comma, semicolon, vertical bar, bullet (`•`), carriage return and line feed, repeated one or more times.

**Language.** `(","|";"|"|"|"•"|CR|LF)+`

**Accepted as a separator:** `,`, `;|`, `•`, a line break.

**Rejected:** a single space (`JS React` is **one** item), `/` (so `CI/CD` is not split), `:`.

**How it is used.** The skills body is split with this expression; each piece is then stripped of surrounding whitespace and of **one** trailing period, and empty pieces are discarded. The order, the case and the duplicates are preserved.

**Limitations.** Skills separated only by spaces are not split, and a skill name that contains one of the separators cannot be represented.

### 1.4.9 Alias fallback (free-text scan)

When the résumé has **no** skills section, `extract()` looks for known skill spellings in the whole text. The pattern is built at runtime from the aliases in `vocabulary.json` (via `alias_index()`):

```python
aliases = sorted(
    (alias for alias in alias_index()
     if len(alias) >= 3 and alias.casefold() not in _FALLBACK_STOPWORDS),
    key=len, reverse=True,
)
alias_pattern = re.compile(
    r"(?i)(?<![\w])(?:" + "|".join(re.escape(a) for a in aliases) + r")(?![\w])"
)
```

with `_FALLBACK_STOPWORDS = {"rest", "node", "torch"}`.

**Design decisions.**

* The alternation is built from the vocabulary, not from a copy, so the extractor and the transducers always share one source of truth (contract section 3.2, rule 4).
* Aliases are sorted by **decreasing length**, so a longer alias (`javascript`) is tried before a shorter one that is its prefix (`java`).
* `¬W` on both sides forces **whole-word** matches.
* Aliases shorter than three characters (`js`, `ts`, `ml`, `tf`, `py`) and the ambiguous words `rest`, `node` and `torch` are ignored: in free text they produce too many false positives.
* The surface text is returned **exactly as it appears** in the résumé.

**Language.** `¬W (A1 | A2 | ... | An) ¬W`, where each `Ai` is one literal alias.

**Accepted:** `React.js` and `Git` in "I work with React.js and Git." (result `["React.js", "Git"]`).

**Rejected:** `JS`, `ML`, `TF` (too short), `Node`, `Torch`, `REST` (stopwords). For example "I use JS, ML, TF, REST, Node, Torch, Git, and React." produces `["Git", "React"]`.

**Limitations.** It cannot tell a technology from the same word used in ordinary prose, and the stopword list is chosen by hand. The fallback is used only when no skills section is found; a skills section takes precedence.

## 1.5 Implementation and stored output

`extract(text: str) -> ExtractionResult` validates the type of the input and calls one helper per information type: name, emails, phones, links, education, experience and skills. It builds a `Candidate` and an `ExtractionResult` (`src/resumelens/models.py`).

* Matches are returned **in order of appearance**.
* Emails, phones and links are stored as lists of strings; links lose trailing sentence punctuation.
* Experience is stored as `Experience(years: float, description: str)`.
* Education is stored as `Education(degree, institution, year)`, with empty strings for missing fields.
* `raw_skills` is stored as a list of strings, unmodified, which becomes the input of Stage 2.

The behavior is covered by `tests/test_extraction.py` (each pattern, English and Spanish variants, empty input, invalid types, determinism) and, together with Stage 2, by `tests/test_stage1_2.py` (the two résumés of the assignment and every file in `samples/`).

---

## 2. Finite-State Transducers — 7-Tuple (Stage 2 — Alejo)

*TODO: Document the 7-tuple $M = (Q, \Sigma, \Gamma, \delta, \omega, q_0, F)$ for canonical skill normalization.*

---

## 3. Finite Automata — 5-Tuple (Stage 3 — Diego)

*TODO: Document the 5-tuple $M = (Q, \Sigma, \delta, q_0, F)$ and the chosen automaton type (DFA / NFA / ε-NFA) for qualification pattern recognition.*

---

## 4. Context-Free Grammar (EBNF) — Stage 4 (Edwar)

### 4.1 Purpose and Formal Definition

Stage 4 represents the structured profile of a candidate using a Domain-Specific Language (DSL). The language is formally defined as a Context-Free Grammar (CFG) denoted by the 4-tuple:

$$G = (V, \Sigma, R, S)$$

Where:
- **$V$** is the finite set of non-terminal symbols (variables).
- **$\Sigma$** is the finite set of terminal symbols (alphabet).
- **$R$** is the finite set of production rules ($V \to (V \cup \Sigma)^*$).
- **$S \in V$** is the start symbol ($S = \text{CandidateModel}$).

### 4.2 Non-Terminal Symbols ($V$)

$$V = \{ \text{CandidateModel}, \text{ContactBlock}, \text{EducationBlock}, \text{ExperienceBlock}, \text{SkillsBlock}, \text{ClassificationBlock}, \text{ProfileClassification} \}$$

| Non-Terminal | Semantic Role |
|---|---|
| `CandidateModel` | Root symbol representing the entire candidate profile document. |
| `ContactBlock` | Block enclosing optional communication channels (email, phone, link). |
| `EducationBlock` | Single academic qualification record (degree, institution, graduation year). |
| `ExperienceBlock` | Single professional experience record (duration in years, description). |
| `SkillsBlock` | Block enclosing the sequence of normalized canonical skill tokens. |
| `ClassificationBlock` | Block mapping each configured profile to its binary verdict. |
| `ProfileClassification` | Association between a profile identifier and its qualification verdict. |

### 4.3 Terminal Symbols ($\Sigma$)

The terminal alphabet consists of reserved keywords, structural delimiters, and lexical token categories:

1. **Keywords and structural delimiters:**
   $$\Sigma_{\text{lit}} = \{ \texttt{candidate}, \texttt{contact}, \texttt{education}, \texttt{experience}, \texttt{skills}, \texttt{classification}, \texttt{email}, \texttt{phone}, \texttt{link}, \texttt{degree}, \texttt{institution}, \texttt{year}, \texttt{years}, \texttt{description}, \texttt{\{}, \texttt{\}}, \texttt{:} \}$$

2. **Lexical tokens:**
   - **`STRING`**: A double-quoted literal string matching `"[^"\\]*(?:\\.[^"\\]*)*"`. Used for candidate names, contact values, academic degrees, institutions, years, and job descriptions.
   - **`NUMBER`**: A non-negative numeric literal matching `[0-9]+(?:\.[0-9]+)?`. Used for years of experience.
   - **`SkillToken`**: An uppercase token matching regular expression `[A-Z][A-Z_]*`. Represents a canonical token from output alphabet $\Gamma$ of Stage 2.
   - **`ProfileId`**: An identifier matching regular expression `[A-Z][A-Z_]*`. Represents a configured professional profile.
   - **`Verdict`**: Binary evaluation result, matching exactly $\texttt{ACCEPTED} \mid \texttt{REJECTED}$.

$$\Sigma = \Sigma_{\text{lit}} \cup \{ \texttt{STRING}, \texttt{NUMBER}, \texttt{SkillToken}, \texttt{ProfileId}, \texttt{Verdict} \}$$

### 4.4 Production Rules ($R$) in ISO/IEC 14977 EBNF

In the standard notation, `,` denotes concatenation, `|` denotes alternation, `[ ... ]` denotes optionality (0 or 1), and `{ ... }` denotes repetition (0 or more times):

```ebnf
CandidateModel = "candidate" , STRING , "{" ,
                 [ ContactBlock ] ,
                 { EducationBlock } ,
                 { ExperienceBlock } ,
                 [ SkillsBlock ] ,
                 ClassificationBlock ,
                 "}" ;

ContactBlock   = "contact" , "{" ,
                 { ( "email" , STRING )
                 | ( "phone" , STRING )
                 | ( "link"  , STRING ) } ,
                 "}" ;

EducationBlock = "education" , "{" ,
                 [ "degree" , STRING ] ,
                 [ "institution" , STRING ] ,
                 [ "year" , STRING ] ,
                 "}" ;

ExperienceBlock = "experience" , "{" ,
                  [ "years" , NUMBER ] ,
                  [ "description" , STRING ] ,
                  "}" ;

SkillsBlock    = "skills" , "{" ,
                 { SkillToken } ,
                 "}" ;

ClassificationBlock = "classification" , "{" ,
                      ProfileClassification ,
                      { ProfileClassification } ,
                      "}" ;

ProfileClassification = ProfileId , ":" , Verdict ;

Verdict        = "ACCEPTED" | "REJECTED" ;
```

### 4.5 Mapping to the textX Metamodel (`candidate.tx`)

The formal EBNF productions map directly to the textX grammar implementation in `src/resumelens/candidate.tx`:

| EBNF Production | textX Syntax in `candidate.tx` | Python Object Attribute |
|---|---|---|
| `CandidateModel` | `'candidate' name=STRING '{' ... '}'` | `model.name`, `model.contact`, etc. |
| `ContactBlock` | `('email' emails+=STRING \| 'phone' phones+=STRING \| 'link' links+=STRING)*` | `model.contact.emails`, `phones`, `links` (`list[str]`) |
| `EducationBlock` | `education*=EducationBlock` | `model.education` (`list[EducationBlock]`) |
| `ExperienceBlock` | `experience*=ExperienceBlock` | `model.experience` (`list[ExperienceBlock]`) |
| `SkillsBlock` | `skills*=SkillToken` | `model.skills.skills` (`list[str]`) |
| `ClassificationBlock` | `entries+=ProfileClassification` | `model.classification.entries` (`list`) |
| `ProfileClassification` | `profile_id=ProfileId ':' verdict=Verdict` | `entry.profile_id`, `entry.verdict` |

### 4.6 Theoretical Justification

1. **Need for a Context-Free Language (Chomsky Type-2):**
   A candidate profile contains hierarchical recursive structures: balanced block delimiters (`{ ... }`), arbitrarily repeated entries (multiple educations, multiple jobs), and optional nested elements. The language of balanced nested delimiters and structured nested records cannot be modeled by regular languages (Chomsky Type-3) due to the pumping lemma for regular languages. A CFG provides the exact expressiveness required while remaining efficient to parse.

2. **Unambiguity and Determinism:**
   Each block begins with an unambiguous keyword (`candidate`, `contact`, `education`, `experience`, `skills`, `classification`). No two non-terminals share initial terminal prefixes, eliminating shift-reduce or reduce-reduce ambiguities. The grammar is $LL(1)$ and Parsing Expression Grammar (PEG) compatible, enabling linear-time deterministic parsing without backtracking.

3. **Separation of Syntax and Semantics:**
   The grammar enforces lexical correctness (valid token casing, quote escaping, valid verdict literals) and syntactic structure (required blocks and balanced braces). Semantic constraints—such as ensuring that tokens in `skills` belong to `vocabulary.json` and profiles in `classification` match the active profile registry—are decoupled from parser execution and validated in the application layer.
