"""
NLP extraction service using spaCy and skill taxonomy.

Layers on top of the regex-based section parser to provide:
1. Named Entity Recognition (people, organisations, locations, dates)
2. Skill extraction via taxonomy matching with confidence scores
3. Entity-level extraction from the full CV text
"""
import spacy
from app.services.skill_taxonomy import match_skills_in_text, normalise_skill, get_skill_category

# Load spaCy model once at module level
nlp = spacy.load("en_core_web_sm")


def extract_entities(text):
    """Run spaCy NER on text and return structured entities.

    Extracts: PERSON, ORG, GPE (locations), DATE, NORP (nationalities/groups)
    """
    doc = nlp(text)

    entities = []
    seen = set()

    for ent in doc.ents:
        # Skip duplicates and very short entities
        if ent.text.strip() in seen or len(ent.text.strip()) < 2:
            continue

        # Only keep useful entity types for CV analysis
        if ent.label_ in ("PERSON", "ORG", "GPE", "DATE", "NORP", "FAC", "PRODUCT", "EVENT"):
            entities.append({
                "text": ent.text.strip(),
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
            })
            seen.add(ent.text.strip())

    return entities


def extract_skills_with_confidence(text, parsed_skills):
    """Extract skills using both taxonomy matching and parsed skills list.

    Combines:
    1. Skills already extracted by the regex parser (from the Skills section)
    2. Skills found by scanning the full text against the taxonomy

    Returns deduplicated list with confidence scores.
    """
    extracted = {}

    # Source 1: Skills from the parsed Skills section (high confidence)
    for skill_text in parsed_skills:
        canonical = normalise_skill(skill_text)
        if canonical:
            extracted[canonical] = {
                "skill": canonical,
                "category": get_skill_category(canonical),
                "confidence": 0.95,
                "source": "skills_section",
            }
        else:
            # Skill not in taxonomy — still include it but with lower confidence
            extracted[skill_text] = {
                "skill": skill_text,
                "category": "unknown",
                "confidence": 0.70,
                "source": "skills_section",
            }

    # Source 2: Taxonomy scan across the full CV text
    text_matches = match_skills_in_text(text)
    for match in text_matches:
        skill = match["skill"]
        if skill not in extracted:
            # Found in text but not in the Skills section
            extracted[skill] = {
                "skill": skill,
                "category": match["category"],
                "confidence": 0.80,
                "source": "text_body",
            }
        else:
            # Already found in Skills section — boost confidence slightly
            if extracted[skill]["confidence"] < 0.98:
                extracted[skill]["confidence"] = min(extracted[skill]["confidence"] + 0.03, 0.98)

    # Sort by confidence descending
    return sorted(extracted.values(), key=lambda x: x["confidence"], reverse=True)


def run_nlp_pipeline(raw_text, parsed_data):
    """Run the full NLP pipeline on a resume.

    Args:
        raw_text: The full extracted text from the CV
        parsed_data: The structured data from the section parser

    Returns:
        nlp_data dict matching the resume schema:
        {
            "extracted_skills": [...],
            "entities": [...],
            "embedding": [384-dim vector],
            "experience_embeddings": [{role, embedding}, ...]
        }
    """
    from app.services.embedding import generate_embedding, generate_embeddings_batch

    # Step 1: Extract named entities with spaCy
    entities = extract_entities(raw_text)

    # Step 2: Extract and normalise skills
    parsed_skills = parsed_data.get("skills", [])
    extracted_skills = extract_skills_with_confidence(raw_text, parsed_skills)

    # Step 3: Generate BERT embeddings
    # 3a: Overall CV embedding — captures the candidate's general profile
    summary_text = parsed_data.get("summary") or ""
    skills_text = ", ".join(parsed_skills)
    profile_text = f"{summary_text} Skills: {skills_text}"
    profile_embedding = generate_embedding(profile_text)

    # 3b: Per-experience embeddings — captures what they did in each role
    experience_embeddings = []
    experience_texts = []
    for exp in parsed_data.get("experience", []):
        role_text = f"{exp.get('job_title', '')} at {exp.get('company', '')}. {exp.get('description', '')}"
        experience_texts.append(role_text)

    if experience_texts:
        exp_vectors = generate_embeddings_batch(experience_texts)
        for i, exp in enumerate(parsed_data.get("experience", [])):
            experience_embeddings.append({
                "role": exp.get("job_title", "Unknown"),
                "company": exp.get("company", "Unknown"),
                "embedding": exp_vectors[i],
            })

    return {
        "extracted_skills": extracted_skills,
        "entities": entities,
        "embedding": profile_embedding,
        "experience_embeddings": experience_embeddings,
    }
