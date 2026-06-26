"""
Soft skills management service.

Maintains a predefined list of common IT/tech soft skills
stored in MongoDB. Users can add new ones through the UI.
"""

# Default soft skills seeded on first use
DEFAULT_SOFT_SKILLS = [
    "Communication",
    "Teamwork",
    "Problem Solving",
    "Critical Thinking",
    "Time Management",
    "Leadership",
    "Adaptability",
    "Attention to Detail",
    "Collaboration",
    "Creativity",
    "Decision Making",
    "Conflict Resolution",
    "Mentoring",
    "Presentation Skills",
    "Project Management",
    "Analytical Thinking",
    "Self Motivation",
    "Work Ethic",
    "Emotional Intelligence",
    "Negotiation",
    "Stakeholder Management",
    "Agile Mindset",
    "Cross-functional Collaboration",
    "Technical Writing",
    "Client Communication",
    "Code Review",
    "Debugging",
    "Responsive Design",
]


def seed_soft_skills(db):
    """Seed the soft_skills collection with defaults if empty."""
    if db.soft_skills.count_documents({}) == 0:
        for skill in DEFAULT_SOFT_SKILLS:
            db.soft_skills.insert_one({"name": skill})


def get_all_soft_skills(db):
    """Get all soft skills from the database."""
    seed_soft_skills(db)
    return [doc["name"] for doc in db.soft_skills.find({}, {"name": 1}).sort("name", 1)]


def add_soft_skill(db, name):
    """Add a new soft skill if it doesn't already exist."""
    name = name.strip()
    if not name:
        return False, "Skill name cannot be empty"

    existing = db.soft_skills.find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})
    if existing:
        return False, f"'{name}' already exists"

    db.soft_skills.insert_one({"name": name})
    return True, f"'{name}' added"
