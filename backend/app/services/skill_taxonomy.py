"""
Database-driven skill taxonomy.

Skills are stored in MongoDB and cached in memory for fast lookups.
The cache refreshes when skills are added, edited, or deleted.
On first run, the collection is seeded with default skills.
"""
import re
from difflib import SequenceMatcher

# In-memory cache — loaded from MongoDB
_taxonomy = {}
_alias_lookup = {}
_cache_loaded = False


# ─── Default skills (seeded on first run) ───

DEFAULT_SKILLS = {
    # Programming Languages
    "Python": {"category": "language", "aliases": ["python", "python3", "py"]},
    "JavaScript": {"category": "language", "aliases": ["javascript", "js", "es6", "es2015", "ecmascript"]},
    "TypeScript": {"category": "language", "aliases": ["typescript", "ts"]},
    "Java": {"category": "language", "aliases": ["java", "j2ee", "jee"]},
    "C#": {"category": "language", "aliases": ["c#", "csharp", "c sharp"]},
    "C++": {"category": "language", "aliases": ["c++", "cpp"]},
    "C": {"category": "language", "aliases": ["c language", "ansi c"]},
    "Go": {"category": "language", "aliases": ["go", "golang"]},
    "Rust": {"category": "language", "aliases": ["rust", "rust-lang"]},
    "Ruby": {"category": "language", "aliases": ["ruby"]},
    "PHP": {"category": "language", "aliases": ["php", "php7", "php8"]},
    "Swift": {"category": "language", "aliases": ["swift"]},
    "Kotlin": {"category": "language", "aliases": ["kotlin"]},
    "Dart": {"category": "language", "aliases": ["dart"]},
    "Scala": {"category": "language", "aliases": ["scala"]},
    "R": {"category": "language", "aliases": ["r language", "r programming"]},
    "SQL": {"category": "language", "aliases": ["sql", "structured query language"]},
    "HTML": {"category": "language", "aliases": ["html", "html5"]},
    "CSS": {"category": "language", "aliases": ["css", "css3"]},
    "Bash": {"category": "language", "aliases": ["bash", "shell", "shell scripting", "sh"]},
    "Lua": {"category": "language", "aliases": ["lua"]},
    "Perl": {"category": "language", "aliases": ["perl"]},
    "Elixir": {"category": "language", "aliases": ["elixir"]},
    "Haskell": {"category": "language", "aliases": ["haskell"]},
    "MATLAB": {"category": "language", "aliases": ["matlab"]},

    # Frontend Frameworks
    "React": {"category": "framework", "aliases": ["react", "reactjs", "react.js", "react js"]},
    "Angular": {"category": "framework", "aliases": ["angular", "angularjs", "angular.js"]},
    "Vue.js": {"category": "framework", "aliases": ["vue", "vuejs", "vue.js", "vue js", "vue 3"]},
    "Next.js": {"category": "framework", "aliases": ["next", "nextjs", "next.js"]},
    "Nuxt.js": {"category": "framework", "aliases": ["nuxt", "nuxtjs", "nuxt.js"]},
    "Svelte": {"category": "framework", "aliases": ["svelte", "sveltekit"]},
    "jQuery": {"category": "framework", "aliases": ["jquery"]},
    "Redux": {"category": "framework", "aliases": ["redux", "redux toolkit", "rtk"]},
    "Tailwind CSS": {"category": "framework", "aliases": ["tailwind", "tailwindcss", "tailwind css"]},
    "Bootstrap": {"category": "framework", "aliases": ["bootstrap", "bootstrap 5"]},
    "Material UI": {"category": "framework", "aliases": ["material ui", "mui", "material-ui"]},
    "Sass": {"category": "framework", "aliases": ["sass", "scss"]},

    # Backend Frameworks
    "Node.js": {"category": "framework", "aliases": ["node", "nodejs", "node.js"]},
    "Express.js": {"category": "framework", "aliases": ["express", "expressjs", "express.js"]},
    "Django": {"category": "framework", "aliases": ["django"]},
    "Flask": {"category": "framework", "aliases": ["flask"]},
    "FastAPI": {"category": "framework", "aliases": ["fastapi", "fast api"]},
    "Spring": {"category": "framework", "aliases": ["spring", "spring boot", "springboot"]},
    "ASP.NET": {"category": "framework", "aliases": ["asp.net", "aspnet", ".net", "dotnet", ".net core"]},
    "Ruby on Rails": {"category": "framework", "aliases": ["rails", "ruby on rails", "ror"]},
    "Laravel": {"category": "framework", "aliases": ["laravel"]},
    "NestJS": {"category": "framework", "aliases": ["nestjs", "nest.js"]},
    "GraphQL": {"category": "framework", "aliases": ["graphql"]},
    "REST": {"category": "framework", "aliases": ["rest", "restful", "rest api", "restful api", "restapi", "rest-api", "restful apis"]},

    # Databases
    "MongoDB": {"category": "database", "aliases": ["mongodb", "mongo"]},
    "PostgreSQL": {"category": "database", "aliases": ["postgresql", "postgres", "psql", "pgsql"]},
    "MySQL": {"category": "database", "aliases": ["mysql"]},
    "SQLite": {"category": "database", "aliases": ["sqlite", "sqlite3"]},
    "Redis": {"category": "database", "aliases": ["redis"]},
    "Elasticsearch": {"category": "database", "aliases": ["elasticsearch", "elastic search", "elastic"]},
    "DynamoDB": {"category": "database", "aliases": ["dynamodb", "dynamo db"]},
    "Firebase": {"category": "database", "aliases": ["firebase", "firestore"]},
    "Cassandra": {"category": "database", "aliases": ["cassandra"]},
    "Oracle": {"category": "database", "aliases": ["oracle", "oracle db"]},
    "SQL Server": {"category": "database", "aliases": ["sql server", "mssql", "microsoft sql server"]},
    "Supabase": {"category": "database", "aliases": ["supabase"]},

    # Cloud
    "AWS": {"category": "cloud", "aliases": ["aws", "amazon web services"]},
    "Azure": {"category": "cloud", "aliases": ["azure", "microsoft azure"]},
    "GCP": {"category": "cloud", "aliases": ["gcp", "google cloud", "google cloud platform"]},
    "Cloud Computing": {"category": "cloud", "aliases": ["cloud", "cloud computing", "cloud services"]},
    "Heroku": {"category": "cloud", "aliases": ["heroku"]},
    "Vercel": {"category": "cloud", "aliases": ["vercel"]},
    "Netlify": {"category": "cloud", "aliases": ["netlify"]},
    "DigitalOcean": {"category": "cloud", "aliases": ["digitalocean", "digital ocean"]},

    # DevOps
    "Docker": {"category": "devops", "aliases": ["docker", "dockerfile", "docker-compose"]},
    "Kubernetes": {"category": "devops", "aliases": ["kubernetes", "k8s"]},
    "Jenkins": {"category": "devops", "aliases": ["jenkins"]},
    "GitHub Actions": {"category": "devops", "aliases": ["github actions"]},
    "GitLab CI": {"category": "devops", "aliases": ["gitlab ci", "gitlab ci/cd"]},
    "Terraform": {"category": "devops", "aliases": ["terraform"]},
    "Ansible": {"category": "devops", "aliases": ["ansible"]},
    "Nginx": {"category": "devops", "aliases": ["nginx"]},
    "Linux": {"category": "devops", "aliases": ["linux", "ubuntu", "centos", "debian"]},
    "CI/CD": {"category": "devops", "aliases": ["ci/cd", "ci cd", "continuous integration", "continuous deployment"]},

    # Tools
    "Git": {"category": "tool", "aliases": ["git"]},
    "GitHub": {"category": "tool", "aliases": ["github"]},
    "GitLab": {"category": "tool", "aliases": ["gitlab"]},
    "Bitbucket": {"category": "tool", "aliases": ["bitbucket"]},
    "Jira": {"category": "tool", "aliases": ["jira"]},
    "Confluence": {"category": "tool", "aliases": ["confluence"]},
    "Slack": {"category": "tool", "aliases": ["slack"]},
    "VS Code": {"category": "tool", "aliases": ["vs code", "vscode", "visual studio code"]},
    "Postman": {"category": "tool", "aliases": ["postman"]},
    "Figma": {"category": "tool", "aliases": ["figma"]},
    "Webpack": {"category": "tool", "aliases": ["webpack"]},
    "Vite": {"category": "tool", "aliases": ["vite"]},
    "npm": {"category": "tool", "aliases": ["npm"]},
    "Yarn": {"category": "tool", "aliases": ["yarn"]},
    "Asana": {"category": "tool", "aliases": ["asana"]},
    "Trello": {"category": "tool", "aliases": ["trello"]},

    # Data Science & ML
    "TensorFlow": {"category": "ml", "aliases": ["tensorflow", "tf"]},
    "PyTorch": {"category": "ml", "aliases": ["pytorch"]},
    "scikit-learn": {"category": "ml", "aliases": ["scikit-learn", "sklearn", "scikit learn"]},
    "Pandas": {"category": "ml", "aliases": ["pandas"]},
    "NumPy": {"category": "ml", "aliases": ["numpy"]},
    "Keras": {"category": "ml", "aliases": ["keras"]},
    "spaCy": {"category": "ml", "aliases": ["spacy"]},
    "NLTK": {"category": "ml", "aliases": ["nltk"]},
    "OpenCV": {"category": "ml", "aliases": ["opencv"]},
    "Matplotlib": {"category": "ml", "aliases": ["matplotlib"]},
    "Jupyter": {"category": "ml", "aliases": ["jupyter", "jupyter notebook"]},
    "Hugging Face": {"category": "ml", "aliases": ["hugging face", "huggingface", "transformers"]},
    "Apache Spark": {"category": "ml", "aliases": ["spark", "apache spark", "pyspark"]},
    "Tableau": {"category": "ml", "aliases": ["tableau"]},
    "Power BI": {"category": "ml", "aliases": ["power bi", "powerbi"]},

    # Mobile
    "React Native": {"category": "mobile", "aliases": ["react native"]},
    "Flutter": {"category": "mobile", "aliases": ["flutter"]},
    "Android": {"category": "mobile", "aliases": ["android", "android sdk"]},
    "iOS": {"category": "mobile", "aliases": ["ios", "ios development"]},
    "Xcode": {"category": "mobile", "aliases": ["xcode"]},

    # Testing
    "Jest": {"category": "testing", "aliases": ["jest"]},
    "Cypress": {"category": "testing", "aliases": ["cypress"]},
    "Selenium": {"category": "testing", "aliases": ["selenium"]},
    "pytest": {"category": "testing", "aliases": ["pytest"]},
    "Mocha": {"category": "testing", "aliases": ["mocha"]},
    "JUnit": {"category": "testing", "aliases": ["junit"]},

    # Messaging
    "RabbitMQ": {"category": "messaging", "aliases": ["rabbitmq"]},
    "Kafka": {"category": "messaging", "aliases": ["kafka", "apache kafka"]},
    "WebSocket": {"category": "messaging", "aliases": ["websocket", "websockets", "socket.io", "socketio", "ws"]},
    "gRPC": {"category": "messaging", "aliases": ["grpc"]},

    # Methodologies
    "Agile": {"category": "methodology", "aliases": ["agile", "agile methodology"]},
    "Scrum": {"category": "methodology", "aliases": ["scrum"]},
    "Kanban": {"category": "methodology", "aliases": ["kanban"]},
    "TDD": {"category": "methodology", "aliases": ["tdd", "test driven development"]},
    "Microservices": {"category": "methodology", "aliases": ["microservices", "microservice architecture"]},
    "OOP": {"category": "methodology", "aliases": ["oop", "object oriented programming"]},
    "Design Patterns": {"category": "methodology", "aliases": ["design patterns"]},
}


# ─── Database Operations ───

def seed_taxonomy(db):
    """Seed the skill_taxonomy collection with defaults if empty."""
    if db.skill_taxonomy.count_documents({}) == 0:
        for name, info in DEFAULT_SKILLS.items():
            db.skill_taxonomy.insert_one({
                "name": name,
                "category": info["category"],
                "aliases": info["aliases"],
            })
    reload_cache(db)


def reload_cache(db):
    """Reload the in-memory cache from MongoDB."""
    global _taxonomy, _alias_lookup, _cache_loaded

    _taxonomy = {}
    _alias_lookup = {}

    for doc in db.skill_taxonomy.find():
        name = doc["name"]
        _taxonomy[name] = {
            "category": doc["category"],
            "aliases": doc.get("aliases", []),
        }
        _alias_lookup[name.lower()] = name
        for alias in doc.get("aliases", []):
            _alias_lookup[alias.lower()] = name

    _cache_loaded = True


def _ensure_cache(db=None):
    """Make sure the cache is loaded."""
    global _cache_loaded
    if not _cache_loaded and db:
        seed_taxonomy(db)


def get_all_skills(db):
    """Get all skills from the database grouped by category."""
    _ensure_cache(db)
    skills = []
    for doc in db.skill_taxonomy.find().sort("name", 1):
        skills.append({
            "id": str(doc["_id"]),
            "name": doc["name"],
            "category": doc["category"],
            "aliases": doc.get("aliases", []),
        })
    return skills


def add_skill(db, name, category, aliases):
    """Add a new skill to the taxonomy."""
    name = name.strip()
    if not name:
        return False, "Skill name cannot be empty"

    existing = db.skill_taxonomy.find_one({"name": {"$regex": f"^{re.escape(name)}$", "$options": "i"}})
    if existing:
        return False, f"'{name}' already exists in the taxonomy"

    clean_aliases = [a.strip().lower() for a in aliases if a.strip()]
    # Always include the lowercase version of the name
    if name.lower() not in clean_aliases:
        clean_aliases.insert(0, name.lower())

    db.skill_taxonomy.insert_one({
        "name": name,
        "category": category,
        "aliases": clean_aliases,
    })
    reload_cache(db)
    return True, f"'{name}' added to taxonomy"


def update_skill(db, skill_id, name, category, aliases):
    """Update an existing skill."""
    from bson import ObjectId
    clean_aliases = [a.strip().lower() for a in aliases if a.strip()]
    if name.lower() not in clean_aliases:
        clean_aliases.insert(0, name.lower())

    db.skill_taxonomy.update_one(
        {"_id": ObjectId(skill_id)},
        {"$set": {"name": name, "category": category, "aliases": clean_aliases}}
    )
    reload_cache(db)
    return True, f"'{name}' updated"


def delete_skill(db, skill_id):
    """Delete a skill from the taxonomy."""
    from bson import ObjectId
    skill = db.skill_taxonomy.find_one({"_id": ObjectId(skill_id)})
    if not skill:
        return False, "Skill not found"

    db.skill_taxonomy.delete_one({"_id": ObjectId(skill_id)})
    reload_cache(db)
    return True, f"'{skill['name']}' deleted"


# ─── Lookup Functions ───

def normalise_skill(skill_text):
    """Look up a skill — exact match first, then fuzzy."""
    text = skill_text.lower().strip()
    if not text:
        return None

    exact = _alias_lookup.get(text)
    if exact:
        return exact

    fuzzy = fuzzy_match_skill(text)
    if fuzzy:
        return fuzzy

    return None


def fuzzy_match_skill(skill_text, threshold=0.80):
    """Find the closest matching skill using string similarity."""
    text = skill_text.lower().strip()
    if not text or len(text) < 2:
        return None

    best_match = None
    best_score = 0

    for alias, canonical in _alias_lookup.items():
        if abs(len(alias) - len(text)) > max(len(text) * 0.4, 3):
            continue
        score = SequenceMatcher(None, text, alias).ratio()
        if score > best_score and score >= threshold:
            best_score = score
            best_match = canonical

    return best_match


def get_skill_category(canonical_name):
    """Get the category for a canonical skill name."""
    info = _taxonomy.get(canonical_name)
    return info["category"] if info else "unknown"


def match_skills_in_text(text):
    """Scan text for any skills from the taxonomy."""
    text_lower = text.lower()
    found = {}

    for canonical, info in _taxonomy.items():
        all_names = [canonical] + info["aliases"]
        for name in all_names:
            pattern = r"(?<![a-zA-Z])" + re.escape(name) + r"(?![a-zA-Z])"
            match = re.search(pattern, text_lower if name == name.lower() else text)
            if match and canonical not in found:
                found[canonical] = {
                    "skill": canonical,
                    "category": info["category"],
                    "source": "taxonomy",
                    "position": match.start(),
                }

    return sorted(found.values(), key=lambda x: x["position"])


# ─── Category List ───

SKILL_CATEGORIES = [
    "language",
    "framework",
    "database",
    "cloud",
    "devops",
    "tool",
    "ml",
    "mobile",
    "testing",
    "messaging",
    "methodology",
]
