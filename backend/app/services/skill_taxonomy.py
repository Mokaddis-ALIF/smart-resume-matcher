"""
Tech skill taxonomy for software engineering roles.

A curated dictionary of skills grouped by category. Used to:
1. Match extracted text against known skills
2. Normalise skill names (e.g., "JS" → "JavaScript")
3. Categorise skills (language, framework, tool, etc.)
"""

# Each entry: "canonical_name": {"category": "...", "aliases": [...]}
SKILL_TAXONOMY = {
    # Programming Languages
    "Python": {"category": "language", "aliases": ["python", "python3", "py"]},
    "JavaScript": {"category": "language", "aliases": ["javascript", "js", "es6", "es2015", "ecmascript"]},
    "TypeScript": {"category": "language", "aliases": ["typescript", "ts"]},
    "Java": {"category": "language", "aliases": ["java", "j2ee", "jee"]},
    "C#": {"category": "language", "aliases": ["c#", "csharp", "c sharp", ".net c#"]},
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

    # Frontend Frameworks & Libraries
    "React": {"category": "framework", "aliases": ["react", "reactjs", "react.js", "react js"]},
    "Angular": {"category": "framework", "aliases": ["angular", "angularjs", "angular.js", "angular 2"]},
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
    "REST": {"category": "framework", "aliases": ["rest", "restful", "rest api", "restful api"]},

    # Databases
    "MongoDB": {"category": "database", "aliases": ["mongodb", "mongo"]},
    "PostgreSQL": {"category": "database", "aliases": ["postgresql", "postgres", "psql"]},
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

    # Cloud & DevOps
    "AWS": {"category": "cloud", "aliases": ["aws", "amazon web services"]},
    "Azure": {"category": "cloud", "aliases": ["azure", "microsoft azure"]},
    "GCP": {"category": "cloud", "aliases": ["gcp", "google cloud", "google cloud platform"]},
    "Docker": {"category": "devops", "aliases": ["docker"]},
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
    "Netlify": {"category": "tool", "aliases": ["netlify"]},
    "Vercel": {"category": "tool", "aliases": ["vercel"]},
    "Heroku": {"category": "tool", "aliases": ["heroku"]},

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

    # Messaging & APIs
    "RabbitMQ": {"category": "messaging", "aliases": ["rabbitmq"]},
    "Kafka": {"category": "messaging", "aliases": ["kafka", "apache kafka"]},
    "WebSocket": {"category": "messaging", "aliases": ["websocket", "websockets", "socket.io"]},
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

# Build a reverse lookup: alias → canonical name (case-insensitive)
_ALIAS_LOOKUP = {}
for canonical, info in SKILL_TAXONOMY.items():
    _ALIAS_LOOKUP[canonical.lower()] = canonical
    for alias in info["aliases"]:
        _ALIAS_LOOKUP[alias.lower()] = canonical


def normalise_skill(skill_text):
    """Look up a skill string and return its canonical name, or None if not found."""
    return _ALIAS_LOOKUP.get(skill_text.lower().strip())


def get_skill_category(canonical_name):
    """Get the category for a canonical skill name."""
    info = SKILL_TAXONOMY.get(canonical_name)
    return info["category"] if info else "unknown"


def match_skills_in_text(text):
    """Scan text for any skills from the taxonomy.

    Returns list of {"skill": canonical, "category": cat, "source": "taxonomy"}
    sorted by position in text (first occurrence).
    """
    text_lower = text.lower()
    found = {}

    for canonical, info in SKILL_TAXONOMY.items():
        all_names = [canonical] + info["aliases"]
        for name in all_names:
            # Use word boundary matching to avoid partial matches
            # e.g., "R" shouldn't match inside "React"
            pattern = r"(?<![a-zA-Z])" + re.escape(name) + r"(?![a-zA-Z])"
            match = re.search(pattern, text_lower if name == name.lower() else text)
            if match and canonical not in found:
                found[canonical] = {
                    "skill": canonical,
                    "category": info["category"],
                    "source": "taxonomy",
                    "position": match.start(),
                }

    # Sort by position in text
    return sorted(found.values(), key=lambda x: x["position"])


import re  # needed for match_skills_in_text
