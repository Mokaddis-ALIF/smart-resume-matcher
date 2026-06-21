"""
Matching engine — scores and ranks CVs against a job posting.

Scoring breakdown:
  - Skills match      (default 40% weight)
  - Experience match   (default 30% weight)
  - Education match    (default 15% weight)
  - Projects match     (default 15% weight)

Each category scores 0–100, then gets multiplied by its weight.
The overall score is the sum of weighted scores.
"""
import re
from app.services.skill_taxonomy import normalise_skill
from app.services.embedding import generate_embedding, compute_similarity


def score_skills(resume_nlp_data, resume_parsed, job_requirements):
    """Score how well a candidate's skills match the job requirements.

    Returns:
        dict with score, matched, missing, extra, preferred_matched
    """
    required = set()
    for skill in job_requirements.get("required_skills", []):
        canonical = normalise_skill(skill)
        required.add(canonical if canonical else skill)

    preferred = set()
    for skill in job_requirements.get("preferred_skills", []):
        canonical = normalise_skill(skill)
        preferred.add(canonical if canonical else skill)

    # Get candidate's skills from NLP extraction (canonical names)
    candidate_skills = set()
    for s in resume_nlp_data.get("extracted_skills", []):
        candidate_skills.add(s["skill"])
    # Also add from parsed skills section
    for s in resume_parsed.get("skills", []):
        canonical = normalise_skill(s)
        if canonical:
            candidate_skills.add(canonical)
        else:
            candidate_skills.add(s)

    # Calculate matches
    matched = required & candidate_skills
    missing = required - candidate_skills
    extra = candidate_skills - required - preferred
    preferred_matched = preferred & candidate_skills

    # Score: percentage of required skills matched + bonus for preferred
    if len(required) == 0:
        base_score = 100.0
    else:
        base_score = (len(matched) / len(required)) * 100

    # Bonus for preferred skills (up to 10 extra points)
    if len(preferred) > 0:
        preferred_bonus = (len(preferred_matched) / len(preferred)) * 10
    else:
        preferred_bonus = 0

    score = min(base_score + preferred_bonus, 100.0)

    return {
        "score": round(score, 1),
        "matched": sorted(list(matched)),
        "missing": sorted(list(missing)),
        "extra": sorted(list(extra)),
        "preferred_matched": sorted(list(preferred_matched)),
        "required_count": len(required),
        "matched_count": len(matched),
    }


def score_experience(resume_parsed, job_requirements):
    """Score how well a candidate's experience matches the job requirements.

    Considers:
    - Total years of experience vs minimum required
    - Semantic relevance of experience descriptions (via BERT)
    """
    min_years = job_requirements.get("min_experience_years", 0)

    # Calculate total experience from parsed data
    total_months = 0
    for exp in resume_parsed.get("experience", []):
        duration = exp.get("duration_months")
        if duration:
            total_months += duration
        else:
            # Estimate from start/end dates
            start = exp.get("start_date", "")
            end = exp.get("end_date", "")
            months = _estimate_months(start, end)
            total_months += months

    candidate_years = total_months / 12

    # Score based on years
    if min_years == 0:
        years_score = 100.0
    elif candidate_years >= min_years:
        # Met or exceeded — full marks with slight bonus for extra years
        years_score = min(100.0, 80.0 + (candidate_years / min_years) * 20)
    else:
        # Below minimum — partial credit
        years_score = (candidate_years / min_years) * 70

    # Collect relevant role titles
    relevant_roles = [exp.get("job_title", "") for exp in resume_parsed.get("experience", []) if exp.get("job_title")]

    return {
        "score": round(years_score, 1),
        "required_years": min_years,
        "candidate_years": round(candidate_years, 1),
        "relevant_roles": relevant_roles,
    }


def _estimate_months(start_str, end_str):
    """Estimate duration in months from date strings like '01/2024' or '2024'."""
    def parse_date(date_str):
        date_str = date_str.strip().lower()
        if date_str in ("present", "current"):
            from datetime import datetime
            now = datetime.now()
            return now.year, now.month

        # Try MM/YYYY format
        match = re.match(r"(\d{1,2})/(\d{4})", date_str)
        if match:
            return int(match.group(2)), int(match.group(1))

        # Try Month YYYY format
        month_map = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
                     "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}
        match = re.match(r"(\w{3})\w*\s*(\d{4})", date_str)
        if match:
            month = month_map.get(match.group(1).lower(), 1)
            return int(match.group(2)), month

        # Try YYYY only
        match = re.match(r"(\d{4})", date_str)
        if match:
            return int(match.group(1)), 6  # Assume mid-year

        return None, None

    start_year, start_month = parse_date(start_str)
    end_year, end_month = parse_date(end_str)

    if start_year and end_year:
        months = (end_year - start_year) * 12 + (end_month - start_month)
        return max(months, 0)
    return 0


def score_education(resume_parsed, job_requirements):
    """Score how well a candidate's education matches the job requirements."""
    required_level = job_requirements.get("education_level", "none")
    required_field = job_requirements.get("education_field", "")

    if required_level == "none" or not required_level:
        return {"score": 100.0, "required_level": "none", "candidate_level": "n/a", "field_match": True}

    # Education level hierarchy
    level_ranks = {
        "none": 0,
        "diploma": 1,
        "associate": 2,
        "bachelors": 3,
        "masters": 4,
        "phd": 5,
    }

    # Normalise degree names from parsed data
    degree_map = {
        "bachelor": "bachelors", "bsc": "bachelors", "ba": "bachelors", "bs": "bachelors", "b.tech": "bachelors",
        "master": "masters", "msc": "masters", "mba": "masters", "m.tech": "masters",
        "ph.d": "phd", "phd": "phd", "doctorate": "phd",
        "diploma": "diploma",
        "associate": "associate", "a.s": "associate", "a.a": "associate",
        "higher secondary": "diploma", "secondary school": "none",
    }

    # Find candidate's highest education level
    candidate_level = "none"
    candidate_field = ""
    highest_rank = 0

    for edu in resume_parsed.get("education", []):
        degree = edu.get("degree", "").lower().strip()
        normalised = degree_map.get(degree, "none")
        rank = level_ranks.get(normalised, 0)

        if rank > highest_rank:
            highest_rank = rank
            candidate_level = normalised
            candidate_field = edu.get("field", "") or ""

    required_rank = level_ranks.get(required_level, 0)

    # Score based on level
    if highest_rank >= required_rank:
        level_score = 100.0
    elif highest_rank == required_rank - 1:
        level_score = 70.0  # One level below
    else:
        level_score = 40.0  # Two or more levels below

    # Field match bonus/penalty
    field_match = False
    if required_field and candidate_field:
        req_words = set(required_field.lower().split())
        cand_words = set(candidate_field.lower().split())
        # Check for overlap in field keywords
        if req_words & cand_words or required_field.lower() in candidate_field.lower():
            field_match = True
            level_score = min(level_score + 5, 100.0)

    return {
        "score": round(level_score, 1),
        "required_level": required_level,
        "candidate_level": candidate_level,
        "field_match": field_match,
    }


def score_projects(resume_parsed, resume_nlp_data, job_requirements):
    """Score how relevant a candidate's projects are to the job.

    Uses skill overlap between project technologies and required skills.
    """
    required_skills = set()
    for skill in job_requirements.get("required_skills", []):
        canonical = normalise_skill(skill)
        required_skills.add(canonical if canonical else skill)

    projects = resume_parsed.get("projects", [])
    if not projects:
        return {"score": 30.0, "relevant_projects": [], "tech_overlap": []}

    all_tech_overlap = set()
    relevant_projects = []

    for proj in projects:
        proj_skills = set()
        for tech in proj.get("technologies", []):
            canonical = normalise_skill(tech)
            proj_skills.add(canonical if canonical else tech)

        overlap = proj_skills & required_skills
        if overlap:
            relevant_projects.append(proj.get("title", "Untitled"))
            all_tech_overlap.update(overlap)

    if len(required_skills) == 0:
        score = 70.0 if projects else 30.0
    else:
        # Score based on how many required skills appear in projects
        overlap_ratio = len(all_tech_overlap) / len(required_skills)
        score = min(overlap_ratio * 100, 100.0)

        # Bonus for having multiple relevant projects
        if len(relevant_projects) > 1:
            score = min(score + 10, 100.0)

    return {
        "score": round(score, 1),
        "relevant_projects": relevant_projects,
        "tech_overlap": sorted(list(all_tech_overlap)),
    }


def generate_explanation(candidate_name, overall_score, category, breakdown):
    """Generate a human-readable explanation of why a candidate scored the way they did."""
    skills = breakdown["skills"]
    experience = breakdown["experience"]
    education = breakdown["education"]
    projects = breakdown["projects"]

    parts = []

    # Overall assessment
    if category == "highly_qualified":
        parts.append(f"{candidate_name} is a strong match for this role.")
    elif category == "qualified":
        parts.append(f"{candidate_name} meets many of the requirements for this role.")
    else:
        parts.append(f"{candidate_name} does not meet the core requirements for this role.")

    # Skills
    if skills["matched_count"] == skills["required_count"]:
        parts.append(f"Has all {skills['required_count']} required skills.")
    elif skills["matched_count"] > 0:
        parts.append(f"Has {skills['matched_count']} of {skills['required_count']} required skills. Missing: {', '.join(skills['missing'])}.")
    else:
        parts.append(f"Missing all required skills: {', '.join(skills['missing'])}.")

    # Experience
    if experience["candidate_years"] >= experience["required_years"]:
        parts.append(f"Has {experience['candidate_years']} years of experience (requires {experience['required_years']}).")
    else:
        parts.append(f"Has {experience['candidate_years']} years of experience, below the {experience['required_years']} year requirement.")

    # Education
    if education["score"] == 100:
        parts.append(f"Education requirement met ({education['candidate_level']}).")
    else:
        parts.append(f"Education: has {education['candidate_level']}, requires {education['required_level']}.")

    # Projects
    if projects["relevant_projects"]:
        parts.append(f"Relevant projects: {', '.join(projects['relevant_projects'])}.")

    return " ".join(parts)


def match_resume_to_job(resume, job):
    """Main matching function — scores a single resume against a job.

    Args:
        resume: Full resume document from MongoDB
        job: Full job document from MongoDB

    Returns:
        dict with overall_score, category, score_breakdown, explanation
    """
    parsed = resume.get("parsed_data", {})
    nlp_data = resume.get("nlp_data", {})
    requirements = job.get("requirements", {})
    weights = job.get("weights", {
        "skills": 0.40,
        "experience": 0.30,
        "education": 0.15,
        "projects": 0.15,
    })

    # Score each category
    skills_result = score_skills(nlp_data, parsed, requirements)
    experience_result = score_experience(parsed, requirements)
    education_result = score_education(parsed, requirements)
    projects_result = score_projects(parsed, nlp_data, requirements)

    # Calculate weighted overall score
    overall_score = (
        skills_result["score"] * weights.get("skills", 0.40)
        + experience_result["score"] * weights.get("experience", 0.30)
        + education_result["score"] * weights.get("education", 0.15)
        + projects_result["score"] * weights.get("projects", 0.15)
    )

    # Add semantic similarity bonus (up to 5 extra points)
    job_embedding = generate_embedding(job.get("description", ""))
    resume_embedding = nlp_data.get("embedding", [])
    if job_embedding and resume_embedding:
        similarity = compute_similarity(job_embedding, resume_embedding)
        semantic_bonus = similarity * 5  # 0 to 5 points
        overall_score = min(overall_score + semantic_bonus, 100.0)

    overall_score = round(overall_score, 2)

    # Determine category
    from app.models.match_result import get_category
    category = get_category(overall_score)

    # Build score breakdown with weights
    breakdown = {
        "skills": {
            **skills_result,
            "weight": weights.get("skills", 0.40),
            "weighted_score": round(skills_result["score"] * weights.get("skills", 0.40), 1),
        },
        "experience": {
            **experience_result,
            "weight": weights.get("experience", 0.30),
            "weighted_score": round(experience_result["score"] * weights.get("experience", 0.30), 1),
        },
        "education": {
            **education_result,
            "weight": weights.get("education", 0.15),
            "weighted_score": round(education_result["score"] * weights.get("education", 0.15), 1),
        },
        "projects": {
            **projects_result,
            "weight": weights.get("projects", 0.15),
            "weighted_score": round(projects_result["score"] * weights.get("projects", 0.15), 1),
        },
    }

    # Generate explanation
    candidate_name = parsed.get("name", "Candidate")
    explanation = generate_explanation(candidate_name, overall_score, category, breakdown)

    # ML classification — if classifiers are trained, predict resume category
    ml_predictions = {}
    try:
        from app.services.classifier import classify_resume
        raw_text = resume.get("raw_text", "")
        if raw_text and len(raw_text) > 50:
            ml_predictions = classify_resume(raw_text)
    except Exception:
        pass  # Models not trained yet — skip

    return {
        "overall_score": overall_score,
        "category": category,
        "score_breakdown": breakdown,
        "explanation": explanation,
        "ml_predictions": ml_predictions,
    }
