"""
CV section parser.

Takes raw extracted text and identifies sections like
education, experience, skills, projects, and contact info.
"""
import re


# Section header patterns — simple keyword matching
# The is_section_heading() gatekeeper ensures these only match actual headings
SECTION_PATTERNS = {
    "summary": r"(?i)\b(summary|profile|about\s*me|objective)\b",
    # "experience": r"(?i)\b(experience|employment)\b",
    "experience": r"(?i)\b(experience|employment|work\s*history)\b",
    "education": r"(?i)\b(education|qualification|degree)\b",
    "skills": r"(?i)\b(skills?|competenc|technologies|tech\s*stack)\b",
    "projects": r"(?i)\bprojects?\b",
    "achievements": r"(?i)\b(achievements?|accomplishments?)\b",
    "languages": r"(?i)\blanguages?\b",
    "other": r"(?i)\b(hobbies|interests|references|volunteer|awards?|certifications?)\b",
}

# Bullet characters — all Unicode variants used in CVs
BULLETS = ("\u2022", "-", "*", "\u00b7", "\u2013", "\u25cf", "\u25cb")

# Patterns for extracting contact information
EMAIL_PATTERN = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
PHONE_PATTERN = r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}"


def is_section_heading(line):
    """Check if a line is a section heading."""
    stripped = line.strip()

    # Strip zero-width spaces and invisible Unicode characters
    stripped = re.sub(r"[\u200b\u200c\u200d\ufeff\u00a0]", "", stripped)
    # Strip trailing decorative characters
    cleaned = re.sub(r"[_\-=.\u2022\u00b7~\u25cf]+\s*$", "", stripped).strip()
    # Strip leading decorative characters
    cleaned = re.sub(r"^[_\-=.\u2022\u00b7~\u25cf]+\s*", "", cleaned).strip()

    if not cleaned:
        return None
    if cleaned.startswith(BULLETS):
        return None
    if len(cleaned) > 40:
        return None
    if ":" in cleaned and len(cleaned.split(":")[0]) > 3:
        if len(cleaned.split(":")[1].strip()) > 10:
            return None

    for section_name, pattern in SECTION_PATTERNS.items():
        if re.search(pattern, cleaned):
            return section_name

    return None


def extract_contact_info(text):
    """Extract email from CV text."""
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
            if not re.search(EMAIL_PATTERN, clean) and not re.search(PHONE_PATTERN, clean):
                if "linkedin" not in clean.lower() and "github" not in clean.lower():
                    contact["name"] = clean
                    break

    # Email — priority: 1) email in first 10 lines, 2) labelled email, 3) any email
    top_lines = "\n".join(lines[:10])
    top_email = re.search(EMAIL_PATTERN, top_lines)
    if top_email:
        contact["email"] = top_email.group()
    else:
        labelled_email = re.search(r"(?i)(?:e[\-\s]?mail|email)\s*[:\s|]\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", text)
        if labelled_email:
            contact["email"] = labelled_email.group(1)
        else:
            email_match = re.search(EMAIL_PATTERN, text)
            if email_match:
                contact["email"] = email_match.group()

    # Phone
    phone_match = re.search(PHONE_PATTERN, text)
    if phone_match:
        contact["phone"] = phone_match.group()

    # Location
    top_text = "\n".join(lines[:10])
    location_patterns = [
        r"(?i)(?:location|address|based in|city)[:\s]*(.+)",
        r"([A-Z][a-z]+(?:\s[A-Z][a-z]+)*,\s*[A-Z]{2,})",
        r"([A-Z][a-z]+,\s*[A-Z][a-z]+(?:\s[A-Z][a-z]+)*)",
    ]
    for pattern in location_patterns:
        match = re.search(pattern, top_text)
        if match:
            contact["location"] = match.group(1).strip() if match.lastindex else match.group().strip()
            break

    return contact


def split_into_sections(text):
    """Split CV text into labelled sections based on heading detection."""
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

        detected = is_section_heading(stripped)

        if detected and detected not in seen_sections:
            content_text = "\n".join(current_content).strip()
            if content_text and current_section not in sections:
                sections[current_section] = content_text

            current_section = detected
            seen_sections.add(detected)
            current_content = []
        else:
            current_content.append(line)

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
    non_empty_lines = [line.strip() for line in lines if line.strip()]

    current_entry = None
    used_lines = set()

    date_pattern = r"(?i)(\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*[\s,]*\d{2,4}|\d{2,4}[\s,]*(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*|\d{1,2}/\d{4}|\d{4})\s*[-\u2013\u2014to]+\s*(\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*[\s,]*\d{2,4}|\d{2,4}[\s,]*(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*|\d{1,2}/\d{4}|\d{4}|present|current)"

    def _looks_like_company(line):
        if not line or len(line) > 60:
            return False
        if line.startswith(BULLETS):
            return False
        has_org_marker = any(m in line for m in [" Ltd", " LTD", " Inc", " Corp", " LLC", " Company", " Technologies", " Solutions", " Group", " Pvt", " Soft.", " Labs"])
        has_location = "," in line and len(line.split(",")[-1].strip()) < 20
        return line[0].isupper() and (has_org_marker or has_location)

    def _looks_like_title(line):
        if not line or len(line) > 80:
            return False
        if line.startswith(BULLETS):
            return False
        title_keywords = ["engineer", "developer", "manager", "analyst", "designer", "intern", "lead", "architect", "consultant", "officer", "director", "specialist", "coordinator", "executive"]
        return any(kw in line.lower() for kw in title_keywords)

    def _parse_pipe_line(line):
        parts = [p.strip() for p in line.split("|") if p.strip()]
        if len(parts) < 2:
            return None, None
        title = None
        company = None
        for part in parts:
            if _looks_like_title(part) and not title:
                title = part
            elif _looks_like_company(part) and not company:
                company = part
            elif not company and not _looks_like_title(part):
                company = part
        if not title and parts:
            title = parts[0]
        if not company and len(parts) > 1:
            company = parts[1]
        return title, company

    for i, stripped in enumerate(non_empty_lines):
        clean_line = stripped.strip("()")
        date_match = re.search(date_pattern, clean_line)

        if date_match:
            if current_entry:
                entries.append(current_entry)

            title_part = re.sub(date_pattern, "", clean_line).strip(" -\u2013\u2014|,()")
            company_part = None

            # Check if this line itself has pipes
            if "|" in title_part:
                pipe_title, pipe_company = _parse_pipe_line(title_part)
                if pipe_title:
                    title_part = pipe_title
                if pipe_company:
                    company_part = pipe_company

            # Look BACK for company and/or title
            if i > 0 and i - 1 not in used_lines:
                prev = non_empty_lines[i - 1]
                if not prev.startswith(BULLETS):
                    if "|" in prev:
                        pipe_title, pipe_company = _parse_pipe_line(prev)
                        if pipe_title:
                            title_part = pipe_title
                        if pipe_company:
                            company_part = pipe_company
                        used_lines.add(i - 1)
                    elif _looks_like_company(prev):
                        company_part = prev
                        used_lines.add(i - 1)
                        if not title_part and i > 1 and i - 2 not in used_lines:
                            prev2 = non_empty_lines[i - 2]
                            if _looks_like_title(prev2):
                                title_part = prev2
                                used_lines.add(i - 2)
                            elif "|" in prev2:
                                pipe_title, _ = _parse_pipe_line(prev2)
                                if pipe_title:
                                    title_part = pipe_title
                                used_lines.add(i - 2)
                    elif _looks_like_title(prev):
                        title_part = prev
                        used_lines.add(i - 1)
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
                if _looks_like_title(next_line) and not next_line.startswith(BULLETS):
                    title_part = next_line
                    used_lines.add(i + 1)

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
            if stripped.startswith(BULLETS):
                desc_line = re.sub(r"^[\u2022\-*\u00b7\u25cf\u2013\s]+", "", stripped)
                if desc_line:
                    current_entry["description"] += desc_line + " "
            else:
                current_entry["description"] += stripped + " "

    if current_entry:
        entries.append(current_entry)

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

    degree_pattern = r"(?i)\b(ph\.?d|doctorate|master|msc|m\.sc\.?|mba|bachelor|bsc|b\.sc\.?|ba|b\.a\.?|bs|b\.s\.?|b\.?tech|m\.?tech|b\.?eng?|m\.?eng?|diploma|associate|a\.?s|a\.?a|higher\s*secondary|secondary\s*school)\b"
    year_pattern = r"\b(19|20)\d{2}\b"

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        degree_match = re.search(degree_pattern, stripped)

        if degree_match:
            if current_entry:
                entries.append(current_entry)

            year_match = re.search(year_pattern, stripped)

            current_entry = {
                "degree": degree_match.group().strip(),
                "field": None,
                "institution": None,
                "year": int(year_match.group()) if year_match else None,
            }

            field_match = re.search(r"(?i)(?:in|of)\s+([A-Za-z\s&]+?)(?:\s*[,|\-\u2013\u2014(]|\s*$)", stripped)
            if field_match:
                current_entry["field"] = field_match.group(1).strip()

        elif current_entry and not current_entry["institution"]:
            if not stripped.startswith(BULLETS) and len(stripped) > 3:
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

    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue

        if ":" in line:
            line = line.split(":", 1)[1]

        cleaned = line.replace("|", ",")
        for b in BULLETS:
            cleaned = cleaned.replace(b, ",")
        cleaned = re.sub(r"^\s*[-*]\s*", ",", cleaned)

        raw_skills = re.split(r"[,]+", cleaned)

        for skill in raw_skills:
            s = skill.strip()
            for b in BULLETS:
                s = s.strip(b)
            s = s.strip(" ")
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

    date_pattern = r"(?i)\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*[\s,]*\d{2,4}\s*[-\u2013\u2014]+\s*(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|\d{2,4}|present|current)"

    def _is_tech_list(line):
        stripped = line.strip()
        if stripped.startswith(BULLETS):
            return False
        if re.match(r"(?i)^\s*(?:technologies|tech\s*stack|tools|built\s*with|stack|using)\s*:", stripped):
            return True
        parts = [p.strip().rstrip(".") for p in stripped.split(",") if p.strip()]
        if len(parts) >= 3 and all(len(p) < 25 for p in parts):
            non_tech_words = ["and", "the", "for", "with", "etc", "etc.", "admin", "teacher", "student",
                              "guardian", "buyer", "seller", "agent", "user", "ensuring", "including",
                              "scalable", "secure", "maintainable"]
            tech_count = 0
            for p in parts:
                clean = p.strip().lower().rstrip(".)}")
                if clean and clean not in non_tech_words and len(clean) > 1:
                    if p.strip()[0].isupper() or re.match(r"^[A-Za-z]+\.?[jJ][sS]$", p.strip()):
                        tech_count += 1
            if len(parts) > 0 and tech_count / len(parts) >= 0.6:
                return True
        return False

    def _extract_techs(line):
        tech_text = re.sub(r"(?i)^\s*(?:technologies|tech\s*stack|tools|built\s*with|stack|using)\s*:\s*", "", line)
        return [t.strip().rstrip(".") for t in tech_text.split(",") if t.strip() and len(t.strip()) < 30]

    def _is_project_title(line):
        stripped = line.strip()
        if stripped.startswith(BULLETS):
            bullet_match = re.match(r"^[\u2022*\u00b7\u25cf]\s*(.+?):\s*(.+)", stripped)
            if bullet_match:
                return True
            return False
        description_starters = ["developed", "built", "created", "implemented", "designed", "managed",
                                "collaborated", "contributed", "worked", "applied", "gained", "used",
                                "integrated", "maintained", "optimized", "ensured", "provided", "performed",
                                "engineered", "a web", "a platform", "an app", "complete", "web-based"]
        if any(stripped.lower().startswith(v) for v in description_starters):
            return False
        if _is_tech_list(stripped):
            return False
        clean = stripped.strip("()")
        if re.match(date_pattern, clean) and len(re.sub(date_pattern, "", clean).strip(" -\u2013\u2014|,()")) < 5:
            return False
        if len(stripped) > 120:
            return False
        if len(stripped) < 8 and " " not in stripped:
            return False
        has_separator = any(sep in stripped for sep in [" - ", " \u2013 ", " \u2014 ", " | "])
        is_short_nonsentence = len(stripped) < 60 and not stripped.endswith(".")
        starts_upper = stripped[0].isupper() if stripped else False
        return starts_upper and (has_separator or is_short_nonsentence)

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        bullet_title_match = re.match(r"^[\u2022\-*\u00b7\u25cf]\s*(.+?):\s*(.+)", stripped)

        if _is_tech_list(stripped) and current_entry:
            current_entry["technologies"] = _extract_techs(stripped)
            continue

        clean_line = stripped.strip("()")
        date_match = re.search(date_pattern, clean_line)
        if date_match and len(re.sub(date_pattern, "", clean_line).strip(" -\u2013\u2014|,()")) < 5:
            continue

        if bullet_title_match:
            if current_entry:
                entries.append(current_entry)
            current_entry = {
                "title": bullet_title_match.group(1).strip(),
                "technologies": [],
                "description": bullet_title_match.group(2).strip(),
            }
            continue

        if _is_project_title(stripped):
            if current_entry:
                entries.append(current_entry)
            title = stripped
            title = re.sub(date_pattern, "", title)
            title = re.sub(r"\|\s*GitHub.*$", "", title, flags=re.IGNORECASE)
            title = re.sub(r"\|\s*\(?\s*$", "", title)
            title = title.strip(" -\u2013\u2014|,()")
            current_entry = {
                "title": title if title else stripped,
                "technologies": [],
                "description": "",
            }
            continue

        if current_entry:
            desc_line = re.sub(r"^[\u2022\-*\u00b7\u25cf\u2013\s]+", "", stripped)
            if desc_line:
                if current_entry["description"]:
                    current_entry["description"] += " " + desc_line
                else:
                    current_entry["description"] = desc_line

    if current_entry:
        entries.append(current_entry)

    for entry in entries:
        entry["description"] = entry["description"].strip()

    return entries


def parse_cv(raw_text):
    """Main function - takes raw CV text and returns fully structured data."""
    contact = extract_contact_info(raw_text)
    sections = split_into_sections(raw_text)

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
