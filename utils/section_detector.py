import re


def normalize_line(line: str) -> str:
    """Normalize whitespace while preserving the text."""

    return re.sub(r"\s+", " ", line).strip()


def heading_score(
    line: str,
    previous_line: str | None = None,
    next_line: str | None = None,
) -> int:
    """
    Calculate how likely a line is to be a section heading.

    This intentionally uses multiple signals rather than
    relying on capitalization alone.
    """

    line = normalize_line(line)

    if not line:
        return 0

    word_count = len(line.split())

    # Very long lines are unlikely to be headings.
    if len(line) > 120:
        return 0

    score = 0

    # Short lines are more likely to be headings.
    if len(line) <= 80:
        score += 1

    if word_count <= 10:
        score += 1

    # Numbered headings:
    # 1. Introduction
    # 2. Rules
    # 2.1 Eligibility
    # 3) Benefits
    if re.match(r"^\d+(?:\.\d+)*[\.)]?\s+\S+", line):
        score += 3

    # Roman numeral headings:
    # I. Introduction
    # II. Rules
    if re.match(r"^[IVXLCDM]+[\.)]\s+\S+", line, re.IGNORECASE):
        score += 2

    # ALL CAPS headings.
    if line.isupper() and word_count <= 10:
        score += 2

    # Title Case headings.
    if (
        word_count <= 8
        and line == line.title()
        and len(line) <= 80
    ):
        score += 2

    # Headings usually don't end like normal sentences.
    if line[-1] not in ".!?;:":
        score += 1
    else:
        score -= 1

    # Surrounding whitespace is a useful signal.
    if previous_line is not None and not previous_line.strip():
        score += 1

    if next_line is not None and not next_line.strip():
        score += 1

    return score


def is_heading(
    line: str,
    previous_line: str | None = None,
    next_line: str | None = None,
) -> bool:
    """
    Determine whether a line is likely to be a section heading.
    """

    return heading_score(
        line,
        previous_line,
        next_line,
    ) >= 4


def split_into_sections(
    text: str,
    current_section: str | None = None,
) -> tuple[list[tuple[str, str | None]], str | None]:
    """
    Split text into logical sections.

    Each returned tuple contains:

        (section_text, section_name)

    current_section is preserved so a section can continue
    across PDF pages.
    """

    raw_lines = text.splitlines()

    sections: list[tuple[str, str | None]] = []

    current_lines: list[str] = []

    for index, raw_line in enumerate(raw_lines):
        line = normalize_line(raw_line)

        if not line:
            continue

        previous_line = (
            raw_lines[index - 1]
            if index > 0
            else None
        )

        next_line = (
            raw_lines[index + 1]
            if index + 1 < len(raw_lines)
            else None
        )

        if is_heading(
            line,
            previous_line,
            next_line,
        ):
            # Save content belonging to the previous section.
            if current_lines:
                sections.append(
                    (
                        "\n".join(current_lines),
                        current_section,
                    )
                )
                current_lines = []

            # The heading becomes the new section.
            current_section = line

        else:
            current_lines.append(line)

    # Save remaining content.
    if current_lines:
        sections.append(
            (
                "\n".join(current_lines),
                current_section,
            )
        )

    return sections, current_section