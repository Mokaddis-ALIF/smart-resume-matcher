from app.services.parser import extract_text
from app.services.section_parser import parse_cv
from app.services.nlp_extractor import run_nlp_pipeline
from app.services.skill_taxonomy import normalise_skill, match_skills_in_text
from app.services.embedding import generate_embedding, compute_similarity
