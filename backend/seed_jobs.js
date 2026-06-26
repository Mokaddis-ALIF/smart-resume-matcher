// Run with: mongosh < seed_jobs.js

use("smart_resume_matcher");

// Clear existing jobs
db.jobs.deleteMany({});
db.resumes.deleteMany({});
db.match_results.deleteMany({});

// Insert all jobs with reference numbers
const jobs = [
  {
    reference: "JOB-001",
    title: "Frontend Developer",
    description: "Develop and maintain scalable, high-performance frontend solutions using Vue.js and React. Collaborate with UI/UX designers to translate wireframes and visual designs into elegant, responsive web interfaces. Implement reusable components and front-end libraries for future use. Optimize applications for speed, scalability, and cross-browser compatibility. Participate in code reviews, share best practices, and mentor teammates where appropriate. Work closely with backend engineers to integrate APIs and deliver cohesive product experiences.",
    requirements: {
      required_skills: ["JavaScript", "Vue.js", "React", "CSS", "Sass", "Webpack", "Git"],
      preferred_skills: ["Node.js", "Express.js", "MongoDB"],
      min_experience_years: 1,
      education_level: "bachelors",
      education_field: ""
    },
    soft_skills: [],
    weights: { skills: 0.40, experience: 0.30, education: 0.15, projects: 0.15 },
    matched_count: 0,
    status: "active",
    created_at: new Date().toISOString()
  },
  {
    reference: "JOB-002",
    title: "Frontend Developer (React)",
    description: "Design, develop, and maintain responsive web applications using React.js and modern JavaScript. Collaborate closely with UI/UX designers, backend engineers, and product managers to deliver high-quality features. Translate wireframes and visual designs into interactive and accessible interfaces. Ensure cross-browser compatibility and optimize applications for speed and scalability. Write clean, reusable, and well-documented code following best practices.\nContribute to code reviews, provide constructive feedback, and mentor junior developers.\nStay updated with emerging frontend trends and advocate for continuous improvement within the team.",
    requirements: {
      required_skills: ["React", "JavaScript", "REST", "HTML", "CSS"],
      preferred_skills: ["Vue.js", "Angular"],
      min_experience_years: 2,
      education_level: "masters",
      education_field: ""
    },
    soft_skills: [],
    weights: { skills: 0.40, experience: 0.30, education: 0.15, projects: 0.15 },
    matched_count: 0,
    status: "active",
    created_at: new Date().toISOString()
  },
  {
    reference: "JOB-003",
    title: "Typescript Engineer",
    description: "Full-stack development across a live commerce platform. Contribute to the design, development and maintenance of front-end applications and back-end services (APIs, databases, microservices). Monitor system metrics, investigate issues, and resolve production bugs as they arise. Work with business stakeholders to understand user and seller experience improvements and translate them into technical solutions. Document existing and newly developed features. Support migration of users and functionality from a legacy platform to a new system. Work within an agile team to propose technical solutions, maintain code quality, and support delivery of migration work.\nCollaborate with other engineering teams to implement platform-specific requirements during migration",
    requirements: {
      required_skills: ["SQL", "GCP", "TypeScript", "React", "GraphQL"],
      preferred_skills: ["GitHub", "Python"],
      min_experience_years: 3,
      education_level: "none",
      education_field: ""
    },
    soft_skills: [],
    weights: { skills: 0.40, experience: 0.30, education: 0.15, projects: 0.15 },
    matched_count: 0,
    status: "active",
    created_at: new Date().toISOString()
  },
  {
    reference: "JOB-004",
    title: "Full Stack React Developer",
    description: "This is a full-time hybrid role for a Full Stack React Developer based in Liverpool, with flexibility to work from home part of the time. The developer will be responsible for building and maintaining modern, responsive user interfaces using React, as well as focusing on comprehensive back-end and full-stack development. Day-to-day tasks will include developing and optimizing software, collaborating with cross-functional teams, ensuring seamless front-end and back-end integration, and maintaining coding standards and documentation. The role requires problem-solving and the ability to adapt to new technologies while contributing to the company's development projects.",
    requirements: {
      required_skills: ["React", "CSS", "Python", "SQL", "Django"],
      preferred_skills: ["AWS", "Git"],
      min_experience_years: 2,
      education_level: "bachelors",
      education_field: "computer science"
    },
    soft_skills: [],
    weights: { skills: 0.40, experience: 0.30, education: 0.15, projects: 0.15 },
    matched_count: 0,
    status: "active",
    created_at: new Date().toISOString()
  },
  {
    reference: "JOB-005",
    title: "Software Engineer",
    description: "Develop, and maintain web applications and managed products. Co-ownership of core framework architecture.\nCollaborate with stakeholders to gather and understand requirements, providing technical expertise and guidance.\nWrite clean, maintainable, and efficient code. Develop front-end user interfaces and back-end services. Ensure the performance, quality, and responsiveness of applications. Troubleshoot and debug applications. Collaborate with other team members and stakeholders to achieve project goals. Provide constructive feedback to peers.\nStay up-to-date with emerging trends and technologies in software development.",
    requirements: {
      required_skills: ["TypeScript", "Next.js", "Git", "React", "JavaScript"],
      preferred_skills: ["Supabase", "Cloud Computing", "AWS"],
      min_experience_years: 5,
      education_level: "bachelors",
      education_field: ""
    },
    soft_skills: [],
    weights: { skills: 0.40, experience: 0.30, education: 0.15, projects: 0.15 },
    matched_count: 0,
    status: "active",
    created_at: new Date().toISOString()
  },
  {
    reference: "JOB-006",
    title: "Mid Level Full Stack Developer",
    description: "At UK Biobank, we're developing new technologies that will help researchers safely access and use some of the world's richest biomedical datasets.\n\nThis role sits within a team building what is believed to be the world's first automated output checking system for trusted research environments using AI and cloud-native technologies to help ensure researchers can only export files regarded as safe.\n\nIt's a rare opportunity to work on something genuinely new, technically challenging, and mission-driven.\nYou'll join a growing engineering team focused on developing and integrating the Automated Output Checking System across UK Biobank's internal and external research platforms.\n\nWorking across backend services, frontend applications, APIs, and cloud infrastructure, you'll help build secure and scalable integrations between access management systems, research analysis platforms, trusted research environments, and supplier-built services.\n\nThis role combines full-stack engineering, cloud technologies, and emerging AI-driven approaches, giving you exposure to modern system design while contributing to technology that supports global research.",
    requirements: {
      required_skills: ["Python", "TypeScript", "React", "FastAPI", "Flask", "SQL"],
      preferred_skills: ["AWS", "Redis"],
      min_experience_years: 3,
      education_level: "bachelors",
      education_field: "computer science"
    },
    soft_skills: [],
    weights: { skills: 0.40, experience: 0.30, education: 0.15, projects: 0.15 },
    matched_count: 0,
    status: "active",
    created_at: new Date().toISOString()
  }
];

db.jobs.insertMany(jobs);

print(`\nInserted ${jobs.length} jobs successfully:`);
jobs.forEach(j => print(`  ${j.reference}: ${j.title}`));
