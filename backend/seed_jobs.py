"""Seed the jobs collection with clean data."""
from pymongo import MongoClient
from datetime import datetime, timezone

client = MongoClient("mongodb://localhost:27017")
db = client["smart_resume_matcher"]

# Clear existing data
db.jobs.delete_many({})
db.resumes.delete_many({})
db.match_results.delete_many({})
print("Cleared existing data")

jobs = [
    {
        "reference": "JOB-001",
        "title": "Frontend Developer",
        "description": "Develop and maintain scalable, high-performance frontend solutions using Vue.js and React. Collaborate with UI/UX designers to translate wireframes and visual designs into elegant, responsive web interfaces. Implement reusable components and front-end libraries for future use. Optimize applications for speed, scalability, and cross-browser compatibility.",
        "requirements": {
            "required_skills": ["JavaScript", "Vue.js", "React", "CSS", "Sass", "Webpack", "Git"],
            "preferred_skills": ["Node.js", "Express.js", "MongoDB"],
            "min_experience_years": 1,
            "education_level": "bachelors",
            "education_field": "",
        },
        "soft_skills": [],
        "weights": {"skills": 0.40, "experience": 0.30, "education": 0.15, "projects": 0.15},
        "matched_count": 0,
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "reference": "JOB-002",
        "title": "Frontend Developer (React)",
        "description": "Design, develop, and maintain responsive web applications using React.js and modern JavaScript. Collaborate closely with UI/UX designers, backend engineers, and product managers to deliver high-quality features. Translate wireframes and visual designs into interactive and accessible interfaces.",
        "requirements": {
            "required_skills": ["React", "JavaScript", "REST", "HTML", "CSS"],
            "preferred_skills": ["Vue.js", "Angular"],
            "min_experience_years": 2,
            "education_level": "masters",
            "education_field": "",
        },
        "soft_skills": [],
        "weights": {"skills": 0.40, "experience": 0.30, "education": 0.15, "projects": 0.15},
        "matched_count": 0,
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "reference": "JOB-003",
        "title": "Typescript Engineer",
        "description": "Full-stack development across a live commerce platform. Contribute to the design, development and maintenance of front-end applications and back-end services (APIs, databases, microservices). Monitor system metrics, investigate issues, and resolve production bugs.",
        "requirements": {
            "required_skills": ["SQL", "GCP", "TypeScript", "React", "GraphQL"],
            "preferred_skills": ["GitHub", "Python"],
            "min_experience_years": 3,
            "education_level": "none",
            "education_field": "",
        },
        "soft_skills": [],
        "weights": {"skills": 0.40, "experience": 0.30, "education": 0.15, "projects": 0.15},
        "matched_count": 0,
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "reference": "JOB-004",
        "title": "Full Stack React Developer",
        "description": "Full-time hybrid role for a Full Stack React Developer. Building and maintaining modern, responsive user interfaces using React, as well as comprehensive back-end and full-stack development. Developing and optimizing software, collaborating with cross-functional teams, ensuring seamless front-end and back-end integration.",
        "requirements": {
            "required_skills": ["React", "CSS", "Python", "SQL", "Django"],
            "preferred_skills": ["AWS", "Git"],
            "min_experience_years": 2,
            "education_level": "bachelors",
            "education_field": "computer science",
        },
        "soft_skills": [],
        "weights": {"skills": 0.40, "experience": 0.30, "education": 0.15, "projects": 0.15},
        "matched_count": 0,
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "reference": "JOB-005",
        "title": "Software Engineer",
        "description": "Develop and maintain web applications and managed products. Co-ownership of core framework architecture. Collaborate with stakeholders to gather and understand requirements. Write clean, maintainable, and efficient code. Develop front-end user interfaces and back-end services.",
        "requirements": {
            "required_skills": ["TypeScript", "Next.js", "Git", "React", "JavaScript"],
            "preferred_skills": ["Supabase", "Cloud Computing", "AWS"],
            "min_experience_years": 5,
            "education_level": "bachelors",
            "education_field": "",
        },
        "soft_skills": [],
        "weights": {"skills": 0.40, "experience": 0.30, "education": 0.15, "projects": 0.15},
        "matched_count": 0,
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "reference": "JOB-006",
        "title": "Mid Level Full Stack Developer",
        "description": "Building the world's first automated output checking system for trusted research environments using AI and cloud-native technologies. Working across backend services, frontend applications, APIs, and cloud infrastructure to build secure and scalable integrations.",
        "requirements": {
            "required_skills": ["Python", "TypeScript", "React", "FastAPI", "Flask", "SQL"],
            "preferred_skills": ["AWS", "Redis"],
            "min_experience_years": 3,
            "education_level": "bachelors",
            "education_field": "computer science",
        },
        "soft_skills": [],
        "weights": {"skills": 0.40, "experience": 0.30, "education": 0.15, "projects": 0.15},
        "matched_count": 0,
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
]

db.jobs.insert_many(jobs)

print(f"\nInserted {len(jobs)} jobs:")
for j in jobs:
    print(f"  {j['reference']}: {j['title']}")

print("\nDone!")
