"""
CV section parser.

Takes raw extracted text and identifies sections like
education, experience, skills, projects, and contact info.
"""
import re


# Section header patterns — these match common CV section headings
SECTION_PATTERNS = {
    "summary": r"(?i)^(summary|profile|about\s*me|objective|personal\s*statement|career\s*summary|professional\s*summary)\s*:?\s*$",
    "experience": r"(?i)^(experience|employment|work\s*history|professional\s*experience|career\s*history|work\s*experience)\s*:?\s*$",
    "education": r"(?i)^(education|academic|qualifications?|degrees?|certifications?)\s*:?\s*$",
    "skills": r"(?i)^(skills|technical\s*skills|core\s*competencies|core\s*skills|key\s*skills)\s*:?\s*$",
    "projects": r"(?i)^(projects?|personal\s*projects?|key\s*projects?|academic\s*projects?|remarkable\s*projects?)\s*:?\s*$",
    "achievements": r"(?i)^(key\s*achievements?|achievements?|accomplishments?)\s*:?\s*$",
    "languages": r"(?i)^(language\s*proficiency|languages?|language\s*skills?)\s*:?\s*$",
    "other": r"(?i)^(hobbies|interests|references|additional\s*information|extracurricular|volunteer|awards?)\s*:?\s*$",
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
    """Parse experience section into structured entries.
    
    Handles multiple CV formats:
    - Format A: Company → Title → Date (title before date)
    - Format B: Company → Date → Title (title after date)
    - Format C: Title — Company — Date (all on one line)
    """
    entries = []
    if not text:
        return entries

    lines = text.split("\n")
    non_empty_lines = []
    for line in lines:
        if line.strip():
            non_empty_lines.append(line.strip())

    current_entry = None
    used_lines = set()

    date_pattern = r"(?i)(\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*[\s,]*\d{2,4}|\d{1,2}/\d{4}|\d{4})\s*[-–—to]+\s*(\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*[\s,]*\d{2,4}|\d{1,2}/\d{4}|\d{4}|present|current)"

    def _looks_like_company(line):
        """Check if a line looks like a company name."""
        if not line or len(line) > 60:
            return False
        if line.startswith(("•", "-", "*", "·")):
            return False
        has_org_marker = any(m in line for m in [" Ltd", " LTD", " Inc", " Corp", " LLC", " Company", " Technologies", " Solutions", " Group", " Pvt", " Soft.", " Labs"])
        has_location = "," in line and len(line.split(",")[-1].strip()) < 20
        return line[0].isupper() and (has_org_marker or has_location)

    def _looks_like_title(line):
        """Check if a line looks like a job title."""
        if not line or len(line) > 80:
            return False
        if line.startswith(("•", "-", "*", "·")):
            return False
        title_keywords = ["engineer", "developer", "manager", "analyst", "designer", "intern", "lead", "architect", "consultant", "officer", "director", "specialist", "coordinator"]
        return any(kw in line.lower() for kw in title_keywords)

    for i, stripped in enumerate(non_empty_lines):
        # Strip parentheses for date matching
        clean_line = stripped.strip("()")
        date_match = re.search(date_pattern, clean_line)

        if date_match:
            if current_entry:
                entries.append(current_entry)

            title_part = re.sub(date_pattern, "", clean_line).strip(" -–—|,()")
            company_part = None

            # Look BACK for company and/or title
            if i > 0 and i - 1 not in used_lines:
                prev = non_empty_lines[i - 1]
                if not prev.startswith(("•", "-", "*", "·")):
                    if _looks_like_company(prev):
                        company_part = prev
                        used_lines.add(i - 1)
                        # Title might be further back or forward
                        if not title_part and i > 1 and i - 2 not in used_lines:
                            prev2 = non_empty_lines[i - 2]
                            if _looks_like_title(prev2):
                                title_part = prev2
                                used_lines.add(i - 2)
                    elif _looks_like_title(prev):
                        title_part = prev
                        used_lines.add(i - 1)
                        # Company might be further back
                        if i > 1 and i - 2 not in used_lines:
                            prev2 = non_empty_lines[i - 2]
                            if _looks_like_company(prev2):
                                company_part = prev2
                                used_lines.add(i - 2)
                    elif not title_part:
                        title_part = prev
                        used_lines.add(i - 1)

            # Look FORWARD for title if not found yet
            if not title_part and i + 1 < len(non_empty_lines):
                next_line = non_empty_lines[i + 1]
                if _looks_like_title(next_line) and not next_line.startswith(("•", "-", "*", "·")):
                    title_part = next_line
                    used_lines.add(i + 1)

            # Inherit company from previous entry if not found
            if not company_part and entries:
                company_part = entries[-1].get("company")

            current_entry = {
                "job_title": title_part if title_part else None,
                "company": company_part,
                "start_date": date_match.group(1).strip(),
                "end_date": date_match.group(2).strip(),
                "duration_months": None,
                "description": "",
            }
            used_lines.add(i)
        elif current_entry and i not in used_lines:
            if stripped.startswith(("•", "-", "*", "·")):
                desc_line = stripped.lstrip("•-*·  ")
                if desc_line:
                    current_entry["description"] += desc_line + " "
            else:
                current_entry["description"] += stripped + " "

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
    """Parse projects section into structured entries.
    
    Handles multiple formats:
    - "• Project Name: Description..." (bullet + colon)
    - "Project Name - Subtitle | (Date)" followed by tech and description lines
    - "Project Name" on its own line followed by description
    - "Technologies: React, Node.js" on separate line
    - Comma-separated tech list without "Technologies:" prefix
    """
    entries = []
    if not text:
        return entries

    lines = text.split("\n")
    current_entry = None

    date_pattern = r"(?i)\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*[\s,]*\d{2,4}\s*[-–—]+\s*(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|\d{2,4}|present|current)"

    def _is_tech_list(line):
        """Check if a line is a comma-separated list of technologies."""
        stripped = line.strip()
        # Never treat bullet points as tech lists
        if stripped.startswith(("•", "*", "·", "-")):
            return False
        # Explicit tech prefix
        if re.match(r"(?i)^\s*(?:technologies|tech\s*stack|tools|built\s*with|stack|using)\s*:", stripped):
            return True
        # Comma-separated short items (at least 3 items, most under 20 chars)
        parts = [p.strip().rstrip(".") for p in stripped.split(",") if p.strip()]
        if len(parts) >= 3 and all(len(p) < 25 for p in parts):
            # Check if items look like tech names — not common English words
            non_tech_words = ["and", "the", "for", "with", "etc", "etc.", "admin", "teacher", "student",
                              "guardian", "buyer", "seller", "agent", "user", "ensuring", "including",
                              "scalable", "secure", "maintainable"]
            tech_count = 0
            for p in parts:
                clean = p.strip().lower().rstrip(".)}")
                if clean and clean not in non_tech_words and len(clean) > 1:
                    # Looks like a tech name if it starts with uppercase or is a known pattern
                    if p.strip()[0].isupper() or re.match(r"^[A-Za-z]+\.?[jJ][sS]$", p.strip()):
                        tech_count += 1
            # At least 60% of items should look like tech names
            if tech_count / len(parts) >= 0.6:
                return True
        return False

    def _extract_techs(line):
        """Extract technology names from a tech line."""
        # Remove prefix if present
        tech_text = re.sub(r"(?i)^\s*(?:technologies|tech\s*stack|tools|built\s*with|stack|using)\s*:\s*", "", line)
        return [t.strip().rstrip(".") for t in tech_text.split(",") if t.strip() and len(t.strip()) < 30]

    def _is_project_title(line):
        """Check if a line looks like a project title."""
        stripped = line.strip()
        # Not a bullet description
        if stripped.startswith(("•", "*", "·")):
            # But could be "• Project Name: description" format
            bullet_match = re.match(r"^[•*·]\s*(.+?):\s*(.+)", stripped)
            if bullet_match:
                return True
            return False
        # Not a description line starting with a verb
        description_starters = ["developed", "built", "created", "implemented", "designed", "managed",
                                "collaborated", "contributed", "worked", "applied", "gained", "used",
                                "integrated", "maintained", "optimized", "ensured", "provided", "performed",
                                "engineered", "a web", "a platform", "an app", "complete", "web-based"]
        if any(stripped.lower().startswith(v) for v in description_starters):
            return False
        # Not a tech list
        if _is_tech_list(stripped):
            return False
        # Not a date-only line
        clean = stripped.strip("()")
        if re.match(date_pattern, clean) and len(re.sub(date_pattern, "", clean).strip(" -–—|,()")) < 5:
            return False
        # Should be reasonably short and not a plain sentence
        if len(stripped) > 120:
            return False
        # Too short to be a project title (single words like "GitHub")
        if len(stripped) < 8 and " " not in stripped:
            return False
        # Title indicators: contains separators, has title-case words, or is short
        has_separator = any(sep in stripped for sep in [" - ", " – ", " — ", " | "])
        is_short_nonsentence = len(stripped) < 60 and not stripped.endswith(".")
        starts_upper = stripped[0].isupper() if stripped else False

        return starts_upper and (has_separator or is_short_nonsentence)

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Check for "• Project Name: Description" format
        bullet_title_match = re.match(r"^[•\-*·]\s*(.+?):\s*(.+)", stripped)

        # Check if this is a technology line
        if _is_tech_list(stripped) and current_entry:
            current_entry["technologies"] = _extract_techs(stripped)
            continue

        # Check for date-only lines (skip them, but store if needed)
        clean_line = stripped.strip("()")
        date_match = re.search(date_pattern, clean_line)
        if date_match and len(re.sub(date_pattern, "", clean_line).strip(" -–—|,()")) < 5:
            continue

        # Check for bullet with title:description pattern
        if bullet_title_match:
            if current_entry:
                entries.append(current_entry)
            current_entry = {
                "title": bullet_title_match.group(1).strip(),
                "technologies": [],
                "description": bullet_title_match.group(2).strip(),
            }
            continue

        # Check if this is a new project title
        if _is_project_title(stripped):
            if current_entry:
                entries.append(current_entry)
            # Clean the title — remove dates, pipes, links
            title = stripped
            title = re.sub(date_pattern, "", title)  # remove dates
            title = re.sub(r"\|\s*GitHub.*$", "", title, flags=re.IGNORECASE)  # remove GitHub links
            title = re.sub(r"\|\s*\(?\s*$", "", title)  # remove trailing pipes
            title = title.strip(" -–—|,()")
            current_entry = {
                "title": title if title else stripped,
                "technologies": [],
                "description": "",
            }
            continue

        # Otherwise it's a description line
        if current_entry:
            desc_line = stripped.lstrip("•-*·  ")
            if desc_line:
                if current_entry["description"]:
                    current_entry["description"] += " " + desc_line
                else:
                    current_entry["description"] = desc_line

    if current_entry:
        entries.append(current_entry)

    # Clean up
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
