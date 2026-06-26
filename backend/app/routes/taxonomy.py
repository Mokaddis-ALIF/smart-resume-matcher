"""
Skill taxonomy management API endpoints.

GET    /api/taxonomy              → List all skills grouped by category
POST   /api/taxonomy              → Add a new skill
PUT    /api/taxonomy/<id>         → Update a skill
DELETE /api/taxonomy/<id>         → Delete a skill
GET    /api/taxonomy/categories   → List all skill categories
"""
from flask import Blueprint, request, jsonify
from app import db
from app.services.skill_taxonomy import (
    get_all_skills, add_skill, update_skill, delete_skill,
    SKILL_CATEGORIES, reload_cache
)

taxonomy_bp = Blueprint("taxonomy", __name__)


@taxonomy_bp.route("/api/taxonomy", methods=["GET"])
def list_skills():
    """List all skills, optionally filtered by category."""
    category = request.args.get("category")
    skills = get_all_skills(db)

    if category:
        skills = [s for s in skills if s["category"] == category]

    # Group by category
    grouped = {}
    for skill in skills:
        cat = skill["category"]
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append(skill)

    return jsonify({"skills": skills, "grouped": grouped, "total": len(skills)})


@taxonomy_bp.route("/api/taxonomy", methods=["POST"])
def create_skill():
    """Add a new skill to the taxonomy."""
    data = request.get_json()
    name = data.get("name", "")
    category = data.get("category", "tool")
    aliases = data.get("aliases", [])

    if not name:
        return jsonify({"error": "Skill name is required"}), 400
    if category not in SKILL_CATEGORIES:
        return jsonify({"error": f"Invalid category. Must be one of: {', '.join(SKILL_CATEGORIES)}"}), 400

    success, message = add_skill(db, name, category, aliases)
    if success:
        return jsonify({"message": message}), 201
    return jsonify({"error": message}), 400


@taxonomy_bp.route("/api/taxonomy/<skill_id>", methods=["PUT"])
def edit_skill(skill_id):
    """Update an existing skill."""
    data = request.get_json()
    name = data.get("name", "")
    category = data.get("category", "")
    aliases = data.get("aliases", [])

    if not name or not category:
        return jsonify({"error": "Name and category are required"}), 400

    success, message = update_skill(db, skill_id, name, category, aliases)
    if success:
        return jsonify({"message": message})
    return jsonify({"error": message}), 400


@taxonomy_bp.route("/api/taxonomy/<skill_id>", methods=["DELETE"])
def remove_skill(skill_id):
    """Delete a skill from the taxonomy."""
    success, message = delete_skill(db, skill_id)
    if success:
        return jsonify({"message": message})
    return jsonify({"error": message}), 404


@taxonomy_bp.route("/api/taxonomy/categories", methods=["GET"])
def list_categories():
    """List all available skill categories."""
    return jsonify({"categories": SKILL_CATEGORIES})
