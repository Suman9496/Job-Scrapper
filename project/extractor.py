# -*- coding: utf-8 -*-
"""
Information Extraction Engine.
Uses semantic boundaries and dictionary matching to extract tech stacks, skills,
responsibilities, and benefits from plain-text descriptions.
"""

import re

# Dictionary of target technologies to extract
TECH_STACK_DICTIONARY = [
    "Python", "Django", "Flask", "FastAPI", "React", "Angular", "Vue", "Node.js", "Express",
    "Java", "Spring Boot", "Kotlin", "Swift", "Flutter", "React Native", "Go", "Golang",
    "Rust", "Ruby on Rails", "C++", "C#", "TypeScript", "JavaScript", "AWS", "Azure", "GCP",
    "Docker", "Kubernetes", "DevOps", "CI/CD", "PostgreSQL", "MySQL", "MongoDB", "Redis",
    "TensorFlow", "PyTorch", "Spark", "Hadoop", "SQL", "Selenium", "Cypress", "Terraform"
]

class InfoExtractor:
    @staticmethod
    def extract_tech_stack(text):
        """Matches dictionary items against description text to yield a unique tech stack list."""
        if not text:
            return []
        found_tech = []
        for tech in TECH_STACK_DICTIONARY:
            # Word boundary regex to avoid partial substring matches (e.g., 'Go' in 'Good')
            pattern = rf"\b{re.escape(tech)}\b"
            if re.search(pattern, text, re.IGNORECASE):
                found_tech.append(tech)
        return found_tech

    @staticmethod
    def extract_skills(text):
        """Extracts general soft and technical skills from the text."""
        skills = []
        common_skills = [
            "REST APIs", "GraphQL", "Agile", "Scrum", "Microservices", "Git", "Unit Testing",
            "System Design", "Cloud Architecture", "NoSQL", "CI/CD Pipelines", "Automation"
        ]
        for skill in common_skills:
            if re.search(rf"\b{re.escape(skill)}\b", text, re.IGNORECASE):
                skills.append(skill)
        return skills

    @staticmethod
    def split_description_sections(description):
        """
        Splits job description into structural fields: Summary, Responsibilities, Requirements, and Benefits.
        Uses heading heuristics.
        """
        sections = {
            "summary": "Full job description provided below.",
            "responsibilities": [],
            "requirements": [],
            "benefits": []
        }
        
        if not description:
            return sections
            
        lines = description.split("\n")
        current_section = "summary"
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue
                
            # Sniff section headings
            line_lower = line_stripped.lower()
            if any(h in line_lower for h in ["responsibility", "what you will do", "role details", "key duties"]):
                current_section = "responsibilities"
                continue
            elif any(h in line_lower for h in ["requirement", "qualification", "what you need", "skills required", "must have"]):
                current_section = "requirements"
                continue
            elif any(h in line_lower for h in ["benefit", "what we offer", "perks", "compensation"]):
                current_section = "benefits"
                continue
                
            # Append line to active section
            if current_section == "summary":
                # Keep summary under 300 chars
                if len(sections["summary"]) < 300:
                    sections["summary"] += " " + line_stripped
            else:
                # Add to lists
                sections[current_section].append(line_stripped)
                
        # Clean lists to text strings
        sections["responsibilities"] = "\n".join(sections["responsibilities"][:10]) if sections["responsibilities"] else "Standard IT development and collaboration duties."
        sections["requirements"] = "\n".join(sections["requirements"][:10]) if sections["requirements"] else "Relevant software experience and degree in CS/IT."
        sections["benefits"] = ", ".join(sections["benefits"][:5]) if sections["benefits"] else "Standard medical benefits and competitive salary."
        
        return sections

    @classmethod
    def populate_extraction_fields(cls, job):
        """Enriches job dictionary with extracted fields in-place."""
        desc = job.get("description", "")
        
        # 1. Tech stack & Skills
        tech_list = cls.extract_tech_stack(desc)
        job["tech_stack"] = ", ".join(tech_list) if tech_list else "Software Engineering Stack"
        job["skills_required"] = ", ".join(cls.extract_skills(desc) + tech_list[:3])
        
        # 2. Description splitting
        sections = cls.split_description_sections(desc)
        job["summary"] = sections["summary"][:200] + "..." if len(sections["summary"]) > 200 else sections["summary"]
        job["responsibilities"] = sections["responsibilities"]
        job["requirements"] = sections["requirements"]
        job["benefits"] = sections["benefits"]
        
        return job
