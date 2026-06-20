"""
CV section parser.

Takes raw extracted text and identifies sections like
education, experience, skills, projects, and contact info.
"""
import re


# Section header patterns — these match common CV section headings
SECTION_PATTERNS = {
    "summary": r"(?i)^(summary|profile|about\s*me|objective|personal\s*statement|career\s*summary|professional\s*summary)\s*$",
    "experience": r"(?i)^(experience|employment|work\s*history|professional\s*experience|career\s*history|work\s*experience)\s*$",
    "education": r"(?i)^(education|academic|qualifications?|degrees?|certifications?)\s*$",
    "skills": r"(?i)^(skills|technical\s*skills|core\s*competencies|key\s*skills)\s*$",
    "projects": r"(?i)^(projects?|personal\s*projects?|key\s*projects?|academic\s*projects?)\s*$",
    "achievements": r"(?i)^(key\s*achievements?|achievements?|accomplishments?)\s*$",
    "languages": r"(?i)^(language\s*proficiency|languages?|language\s*skills?)\s*$",
    "other": r"(?i)^(hobbies|interests|references|additional\s*information|extracurricular|volunteer|awards?)\s*$",
}

# Patterns for extracting contact information
EMAIL_PATTERN = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
PHONE_PATTERN = r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}"


def is_section_heading(line):
    """Check if a line is a section heading.
    
    A section heading must be:
    - Short (under 40 chars)
    - Matches a known pattern exactly (not embedded in other text)
    - Not a bullet point or part of a description
    """
    stripped = line.strip()

    # Skip empty lines, bullet points, and long lines
    if not stripped or len(stripped) > 40:
        return None
    if stripped.startswith(("•", "-", "*", "·", "–")):
        return None
    # Skip lines with colons mid-text (like "Technologies: React, Flask")
    if ":" in stripped and len(stripped.split(":")[0]) > 3:
        words_before_colon = stripped.split(":")[0].strip()
        # Allow "Skills:" but not "Technologies: React, Flask"
        if len(stripped.split(":")[1].strip()) > 10:
            return None

    for section_name, pattern in SECTION_PATTERNS.items():
        if re.search(pattern, stripped):
            return section_name

    return None


def extract_contact_info(text):
    """Extract name, email, phone, and location from CV text."""
    lines = text.strip().split("\n")
    contact = {
        "name": None,
        "email": None,
        "phone": None,
        "location": None,
    }

    # Name is typically the first non-empty line
    for line in lines:
        clean = line.strip()
        if clean and len(clean) > 1:
            # Skip lines that look like contact info or links
            if not re.search(EMAIL_PATTERN, clean) and not re.search(PHONE_PATTERN, clean):
                if "linkedin" not in clean.lower() and "github" not in clean.lower():
                    contact["name"] = clean
                    break

    # Email
    email_match = re.search(EMAIL_PATTERN, text)
    if email_match:
        contact["email"] = email_match.group()

    # Phone
    phone_match = re.search(PHONE_PATTERN, text)
    if phone_match:
        contact["phone"] = phone_match.group()

    # Location — look for common patterns near the top of the CV
    top_text = "\n".join(lines[:10])
    location_patterns = [
        r"(?i)(?:location|address|based in|city)[:\s]*(.+)",
        r"([A-Z][a-z]+(?:\s[A-Z][a-z]+)*,\s*[A-Z]{2,})",  # City, STATE/Country
        r"([A-Z][a-z]+,\s*[A-Z][a-z]+(?:\s[A-Z][a-z]+)*)",  # City, Country
    ]
    for pattern in location_patterns:
        match = re.search(pattern, top_text)
        if match:
            contact["location"] = match.group(1).strip() if match.lastindex else match.group().strip()
            break

    return contact


def split_into_sections(text):
    """Split CV text into labelled sections based on heading detection.
    
    Returns a dict with section names as keys and their text content as values.
    Only the first occurrence of each section is kept (prevents overwriting).
    """
    lines = text.split("\n")
    sections = {}
    current_section = "header"
    current_content = []
    seen_sections = set()

    for line in lines:
        stripped = line.strip()
        if not stripped:
            current_content.append("")
            continue

        # Check if this line is a section heading
        detected = is_section_heading(stripped)

        # Only treat it as a new section if we haven't seen this section before
        if detected and detected not in seen_sections:
            # Save the previous section
            content_text = "\n".join(current_content).strip()
            if content_text and current_section not in sections:
                sections[current_section] = content_text
            
            current_section = detected
            seen_sections.add(detected)
            current_content = []
        else:
            current_content.append(line)

    # Save the last section
    content_text = "\n".join(current_content).strip()
    if content_text and current_section not in sections:
        sections[current_section] = content_text

    return sections


def parse_experience(text):
    """Parse experience section into structured entries."""
    entries = []
    if not text:
        return entries

    lines = text.split("\n")
    non_empty_lines = []
    for line in lines:
        if line.strip():
            non_empty_lines.append(line.strip())

    current_entry = None
    company_name = None

    date_pattern = r"(?i)(\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*[\s,]*\d{2,4}|\d{1,2}/\d{4}|\d{4})\s*[-–—to]+\s*(\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*[\s,]*\d{2,4}|\d{1,2}/\d{4}|\d{4}|present|current)"

    for i, stripped in enumerate(non_empty_lines):
        # Check if this line contains a date range
        date_match = re.search(date_pattern, stripped)

        if date_match:
            # Save previous entry
            if current_entry:
                entries.append(current_entry)

            # Get the title — could be on this line or the previous line
            title_part = re.sub(date_pattern, "", stripped).strip(" -–—|,")

            # If the date was on its own line, the title is the previous line
            if not title_part and i > 0:
                prev = non_empty_lines[i - 1]
                # Only use previous line if it's not a bullet point or a company we already captured
                if not prev.startswith(("•", "-", "*", "·")):
                    title_part = prev

            current_entry = {
                "job_title": title_part if title_part else None,
                "company": company_name,
                "start_date": date_match.group(1).strip(),
                "end_date": date_match.group(2).strip(),
                "duration_months": None,
                "description": "",
            }
        elif current_entry:
            # If line starts with a bullet, it's a description point
            if stripped.startswith(("•", "-", "*", "·")):
                desc_line = stripped.lstrip("•-*·  ")
                if desc_line:
                    current_entry["description"] += desc_line + " "
            else:
                # Could be a continuation of description
                current_entry["description"] += stripped + " "
        else:
            # Lines before the first date — first one is usually the company name
            if not company_name and len(stripped) < 60 and not stripped.startswith(("•", "-", "*", "·")):
                company_name = stripped

    # Save last entry
    if current_entry:
        entries.append(current_entry)

    # Clean up descriptions
    for entry in entries:
        entry["description"] = entry["description"].strip()

    return entries


def parse_education(text):
    """Parse education section into structured entries."""
    entries = []
    if not text:
        return entries

    lines = text.split("\n")
    current_entry = None

    degree_pattern = r"(?i)\b(ph\.?d|doctorate|master|msc|mba|bachelor|bsc|ba|bs|b\.?tech|m\.?tech|diploma|associate|a\.?s|a\.?a|higher\s*secondary|secondary\s*school)\b"
    year_pattern = r"\b(19|20)\d{2}\b"

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Check if this line mentions a degree
        degree_match = re.search(degree_pattern, stripped)

        if degree_match:
            if current_entry:
                entries.append(current_entry)

            # Extract year if present
            year_match = re.search(year_pattern, stripped)

            current_entry = {
                "degree": degree_match.group().strip(),
                "field": None,
                "institution": None,
                "year": int(year_match.group()) if year_match else None,
            }

            # Try to extract field — often follows "in" or "of" after the degree
            field_match = re.search(r"(?i)(?:in|of)\s+([A-Za-z\s&]+?)(?:\s*[,|\-–—(]|\s*$)", stripped)
            if field_match:
                current_entry["field"] = field_match.group(1).strip()

        elif current_entry and not current_entry["institution"]:
            # Next meaningful line after degree is likely the institution
            if not stripped.startswith(("•", "-", "*", "·")) and len(stripped) > 3:
                # Skip if it's just a city name or a short word
                if not re.match(r"^[A-Z][a-z]+$", stripped) or len(stripped) > 15:
                    current_entry["institution"] = stripped

    if current_entry:
        entries.append(current_entry)

    return entries


def parse_skills(text):
    """Parse skills section into a flat list of skills."""
    if not text:
        return []

    skills = []

    # Handle various formats:
    # "Python, Java, C++"
    # "• Python • Java • C++"
    # "- Python\n- Java"
    # "Python | Java | C++"
    # "Tools: Git | GitHub | Asana"

    # Process line by line to handle "Category: skill, skill" format
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue

        # Remove category prefixes like "Tools:" or "Languages:"
        if ":" in line:
            line = line.split(":", 1)[1]

        # Replace common separators with commas
        cleaned = line.replace("|", ",").replace("•", ",").replace("·", ",")
        cleaned = re.sub(r"^\s*[-*]\s*", ",", cleaned)

        # Split by commas
        raw_skills = re.split(r"[,]+", cleaned)

        for skill in raw_skills:
            s = skill.strip().strip("-•·* ")
            # Filter out empty strings and overly long strings (not a skill)
            if s and 1 < len(s) < 40:
                skills.append(s)

    return skills


def parse_projects(text):
    """Parse projects section into structured entries."""
    entries = []
    if not text:
        return entries

    lines = text.split("\n")
    current_entry = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Check if this is a "Technologies:" line
        tech_match = re.search(r"(?i)^\s*(?:technologies|tech\s*stack|tools|built\s*with|stack|using)\s*:\s*(.+)", stripped)
        if tech_match and current_entry:
            techs = [t.strip().rstrip(".") for t in tech_match.group(1).split(",") if t.strip()]
            current_entry["technologies"] = techs
            continue

        # Check if this line starts a new project (bullet point with a title-like pattern)
        # e.g. "• Food Order Website: Developed an efficient..."
        project_match = re.match(r"^[•\-*·]\s*(.+?):\s*(.+)", stripped)
        if project_match:
            if current_entry:
                entries.append(current_entry)
            current_entry = {
                "title": project_match.group(1).strip(),
                "technologies": [],
                "description": project_match.group(2).strip(),
            }
        elif current_entry:
            # Continuation of description
            desc_line = stripped.lstrip("•-*·  ")
            current_entry["description"] += " " + desc_line

    if current_entry:
        entries.append(current_entry)

    for entry in entries:
        entry["description"] = entry["description"].strip()

    return entries


def parse_cv(raw_text):
    """Main function — takes raw CV text and returns fully structured data.
    
    Args:
        raw_text: The full text extracted from the CV file
    
    Returns:
        Dict with structured parsed_data matching the resume schema
    """
    # Step 1: Extract contact info from the top of the CV
    contact = extract_contact_info(raw_text)

    # Step 2: Split into sections
    sections = split_into_sections(raw_text)

    # Step 3: Parse each section
    parsed_data = {
        "name": contact["name"],
        "email": contact["email"],
        "phone": contact["phone"],
        "location": contact["location"],
        "summary": sections.get("summary", None),
        "skills": parse_skills(sections.get("skills", "")),
        "experience": parse_experience(sections.get("experience", "")),
        "education": parse_education(sections.get("education", "")),
        "projects": parse_projects(sections.get("projects", "")),
    }

    return parsed_data
