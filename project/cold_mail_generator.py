# -*- coding: utf-8 -*-
"""
Cold Email and Recruiter Strategy Generator.
Automatically crafts custom, highly specific emails and engagement pathways for each job.
"""

from .config import (
    SENDER_NAME, SENDER_BACKGROUND, YEARS_OF_EXPERIENCE,
    PORTFOLIO_URL, GITHUB_URL, LINKEDIN_URL, RESUME_URL
)

class ColdEmailGenerator:
    @staticmethod
    def generate_email_subject(title, company, job_id=None):
        """Crafts a professional, click-friendly email subject line."""
        ref_suffix = f" — Ref {job_id}" if job_id and "gen-" not in str(job_id) else ""
        return f"Application for {title} at {company}{ref_suffix}"

    @staticmethod
    def generate_local_fallback_email(job):
        """
        Generates a custom cold email based on specific job fields.
        Used as a high-fidelity rule-based fallback if LLM is unavailable.
        """
        title = job.get("title", "Software Engineer")
        company = job.get("company", "Your Company")
        job_id = job.get("id", "N/A")
        tech_stack = job.get("tech_stack", "relevant technologies")
        skills = job.get("skills_required", "software development")
        requirements = job.get("requirements", "strong software development practices")
        benefits = job.get("benefits", "creative environment")
        
        greeting = "Hello Hiring Team,"
        
        # Structure a natural intro
        intro = (
            f"I recently noticed your opening for a {title} at {company} (Job ID: {job_id}) "
            f"and felt compelled to reach out. With my technical skills in {tech_stack}, I am "
            f"confident in my ability to immediately add value to your team."
        )
        
        # Relevance argument
        relevance = (
            f"In my previous work, I have extensively utilized technologies like {skills} to solve complex engineering "
            f"challenges. Your requirement for someone skilled in \"{requirements[:100]}\" aligns perfectly with my "
            f"competencies in designing scalable, clean-code web architectures."
        )
        
        # Cultural/Product connection
        interest = (
            f"I have been following {company}'s growth and admire your innovative engineering culture. "
            f"The opportunity to work alongside your team on major technical initiatives, supported by perks like "
            f"\"{benefits[:100]}\", makes this role a perfect next step for my career."
        )
        
        # Construct full body
        body = (
            f"{greeting}\n\n"
            f"{intro}\n\n"
            f"{relevance}\n\n"
            f"{interest}\n\n"
            f"I have attached my resume below, and would love the chance to connect for a quick conversation "
            f"about how I can help drive development at {company}.\n\n"
            f"Best regards,\n"
            f"{SENDER_NAME}\n"
            f"Background: {SENDER_BACKGROUND}\n"
            f"Experience: {YEARS_OF_EXPERIENCE}\n\n"
            f"Links:\n"
            f"• Portfolio: {PORTFOLIO_URL}\n"
            f"• GitHub: {GITHUB_URL}\n"
            f"• LinkedIn: {LINKEDIN_URL}\n"
            f"• Resume: {RESUME_URL}"
        )
        
        return body

    @staticmethod
    def get_recruiter_strategy(job):
        """Generates a customized recruiter contact strategy based on source & company size."""
        company = job.get("company", "Company")
        source = job.get("source_platform", "Career Page")
        url = job.get("url", "")
        
        strategy = (
            f"1. Navigate to LinkedIn and search for \"Technical Recruiter {company}\" or \"Talent Acquisition {company}\".\n"
            f"2. Send a connection request with the following note:\n"
            f"   \"Hi [Name], saw the {job.get('title')} role on {source}. Sent an email, but wanted to connect here "
            f"to introduce myself! I specialize in {job.get('tech_stack', 'Software Engineering')}. Cheers!\"\n"
            f"3. Submit your application directly on the official page: {url}\n"
            f"4. Follow up via email in 4 business days if you receive no response."
        )
        return strategy

    @classmethod
    def generate_all(cls, job, gemini_client=None):
        """
        Generates custom cold email subject, body, and recruiter strategy.
        Utilizes Gemini LLM if API is initialized, otherwise falls back to the high-fidelity rule writer.
        """
        title = job.get("title", "")
        company = job.get("company", "")
        job_id = job.get("id", "")
        
        # Subject
        job["cold_email_subject"] = cls.generate_email_subject(title, company, job_id)
        
        # Strategy
        job["recruiter_contact_strategy"] = cls.get_recruiter_strategy(job)
        
        # Body (AI vs Fallback)
        if gemini_client:
            try:
                # Prompt design following exact user guidelines
                prompt = (
                    f"Write a highly personalized, natural, human-sounding cold email for this job posting.\n"
                    f"Job Title: {title}\n"
                    f"Company: {company}\n"
                    f"Job ID: {job_id}\n"
                    f"Tech Stack: {job.get('tech_stack')}\n"
                    f"Requirements: {job.get('requirements')}\n"
                    f"Responsibilities: {job.get('responsibilities')}\n\n"
                    f"Format guidelines:\n"
                    f"- Greeting: Hello Hiring Team,\n"
                    f"- Natural intro mentioning specific role and tech stack.\n"
                    f"- Short section highlighting skills matched to requirements.\n"
                    f"- 1-2 personalized sentences expressing genuine interest in {company}'s tech/product.\n"
                    f"- Close with professional placeholders for [Your Name], [Portfolio], [GitHub], [LinkedIn], [Resume].\n"
                    f"- Keep it concise, professional, role-specific, and free of generic spam buzzwords."
                )
                
                # Gemini client generates
                response = gemini_client.models.generateContent(
                    model="gemini-3.5-flash",
                    contents=prompt
                )
                job["custom_cold_email"] = response.text
                return job
            except Exception:
                pass # Fallback to local
                
        # Rule fallback
        job["custom_cold_email"] = cls.generate_local_fallback_email(job)
        return job
