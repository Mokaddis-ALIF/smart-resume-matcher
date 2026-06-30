"""
Extract skills from resume_data.csv and add new ones to the skill taxonomy.
Checks each skill against the existing database before adding.

Usage: python seed_skills_from_resume_data.py
Place resume_data.csv in the backend/data/ folder first.
"""
import pandas as pd
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["smart_resume_matcher"]

CSV_PATH = "data/resume_data.csv"

# Default category mapping — common keywords to guess the category
CATEGORY_HINTS = {
    "language": ["python", "java", "javascript", "typescript", "php", "ruby", "go", "rust", "c++", "c#", "swift", "kotlin", "dart", "scala", "r", "sql", "html", "css", "bash", "perl", "lua", "elixir", "haskell", "matlab"],
    "framework": ["react", "angular", "vue", "django", "flask", "fastapi", "spring", "laravel", "express", "next", "nuxt", "svelte", "bootstrap", "tailwind", "redux", "jquery", "nest", "rails", "graphql", "rest"],
    "database": ["mongodb", "mysql", "postgresql", "postgres", "redis", "sqlite", "oracle", "dynamodb", "cassandra", "firebase", "supabase", "elasticsearch", "sql server", "mssql", "mariadb", "neo4j", "couchdb", "influxdb", "snowflake"],
    "cloud": ["aws", "azure", "gcp", "google cloud", "heroku", "vercel", "netlify", "digitalocean", "cloudflare", "lambda", "ec2", "s3", "sagemaker"],
    "devops": ["docker", "kubernetes", "jenkins", "terraform", "ansible", "nginx", "linux", "ci/cd", "github actions", "gitlab ci", "puppet", "chef", "vagrant", "airflow"],
    "tool": ["git", "github", "gitlab", "bitbucket", "jira", "confluence", "postman", "figma", "vscode", "webpack", "vite", "npm", "yarn", "slack"],
    "ml": ["tensorflow", "pytorch", "keras", "scikit-learn", "sklearn", "pandas", "numpy", "matplotlib", "seaborn", "opencv", "spacy", "nltk", "hugging face", "spark", "tableau", "power bi", "jupyter", "xgboost", "lightgbm", "catboost", "mlflow", "databricks", "plotly", "statsmodels", "scipy", "nlp", "deep learning", "machine learning", "computer vision", "neural"],
    "mobile": ["react native", "flutter", "android", "ios", "swift", "kotlin", "xcode"],
    "testing": ["jest", "cypress", "selenium", "pytest", "mocha", "junit", "playwright"],
    "messaging": ["rabbitmq", "kafka", "websocket", "socket.io", "grpc"],
    "methodology": ["agile", "scrum", "kanban", "tdd", "microservices", "oop", "design patterns", "devops"],
}


def guess_category(skill_name):
    """Guess the category based on keyword matching."""
    lower = skill_name.lower()
    for category, keywords in CATEGORY_HINTS.items():
        for keyword in keywords:
            if keyword in lower or lower in keyword:
                return category
    return "tool"


def main():
    # Read the dataset
    try:
        df = pd.read_csv(CSV_PATH)
    except FileNotFoundError:
        print(f"ERROR: {CSV_PATH} not found. Place the file in backend/data/ folder.")
        return

    print(f"Dataset: {len(df)} rows")
    print(f"Columns: {list(df.columns)}")

    # Find the skills column (case-insensitive)
    skills_col = None
    for col in df.columns:
        if col.lower().strip() == "skills":
            skills_col = col
            break

    if not skills_col:
        print(f"ERROR: No 'skills' column found. Available columns: {list(df.columns)}")
        return

    print(f"Using column: '{skills_col}'")

    # Extract all unique skills
    all_skills = set()
    for skills_str in df[skills_col].dropna():
        for skill in str(skills_str).split(","):
            s = skill.strip()
            if s and len(s) > 1 and len(s) < 40:
                all_skills.add(s)

    print(f"Unique skills found in dataset: {len(all_skills)}")

    # Check which skills already exist in the taxonomy
    existing = set()
    for doc in db.skill_taxonomy.find({}, {"name": 1, "aliases": 1}):
        existing.add(doc["name"].lower())
        for alias in doc.get("aliases", []):
            existing.add(alias.lower())

    print(f"Skills already in taxonomy: {db.skill_taxonomy.count_documents({})}")

    # Find new skills
    new_skills = []
    already_exists = []
    for skill in sorted(all_skills):
        if skill.lower() in existing:
            already_exists.append(skill)
        else:
            new_skills.append(skill)

    print(f"Already in taxonomy: {len(already_exists)}")
    print(f"New skills to add: {len(new_skills)}")

    if not new_skills:
        print("\nNo new skills to add. Taxonomy is up to date.")
        return

    # Add new skills to the taxonomy
    added = 0
    for skill in new_skills:
        category = guess_category(skill)
        doc = {
            "name": skill,
            "category": category,
            "aliases": [skill.lower()],
        }
        db.skill_taxonomy.insert_one(doc)
        added += 1
        print(f"  + {skill} ({category})")

    print(f"\nDone! Added {added} new skills to the taxonomy.")
    print(f"Total skills in taxonomy: {db.skill_taxonomy.count_documents({})}")


if __name__ == "__main__":
    main()
