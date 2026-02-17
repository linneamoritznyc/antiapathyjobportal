"""
Sophisticated CV Assembly Logic
Builds tailored CVs by intelligently selecting experience variants based on industry
"""

from typing import List, Dict, Optional
import anthropic
import os

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


class CVAssembler:
    """Assembles CVs dynamically based on target industry and job requirements"""

    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None

    async def assemble_cv_for_industry(
        self,
        user_id: str,
        industry: str,
        max_experiences: int = 10,
        include_less_relevant: bool = True
    ) -> Dict:
        """
        Assembles a CV tailored for a specific industry

        Args:
            user_id: User's UUID
            industry: Target industry (e.g., 'restaurant', 'tech', 'retail')
            max_experiences: Maximum number of experiences to include
            include_less_relevant: Whether to include experiences with relevance < 4

        Returns:
            Dict with assembled CV sections
        """

        # Get experiences sorted by relevance using our SQL function
        query = f"""
            SELECT * FROM get_experiences_for_industry(
                '{user_id}'::UUID,
                '{industry}',
                {max_experiences}
            )
        """

        result = await self.supabase.rpc('execute_sql', {'query': query}).execute()
        experiences = result.data

        # Filter out low-relevance if requested
        if not include_less_relevant:
            experiences = [exp for exp in experiences if exp['relevance_score'] >= 4]

        # Get other CV sections
        profile = await self._get_profile(user_id)
        education = await self._get_education(user_id)
        skills = await self._get_skills(user_id, industry)
        certifications = await self._get_certifications(user_id, industry)

        return {
            'profile': profile,
            'experiences': experiences,
            'education': education,
            'skills': skills,
            'certifications': certifications,
            'industry': industry,
            'assembled_at': 'now()'
        }

    async def assemble_cv_for_job(
        self,
        user_id: str,
        job_description: str,
        job_title: str,
        industry_hint: Optional[str] = None
    ) -> Dict:
        """
        Assembles a CV tailored for a specific job posting
        Uses AI to analyze job requirements and select best experiences

        Args:
            user_id: User's UUID
            job_description: Full job description text
            job_title: Job title
            industry_hint: Optional industry hint

        Returns:
            Dict with assembled CV optimized for this specific job
        """

        # Use AI to detect industry and key requirements
        if not industry_hint:
            industry_hint = await self._detect_industry_from_job(job_description, job_title)

        # Get all experiences
        all_experiences = await self._get_all_experiences(user_id)

        # Use AI to rank experiences for this specific job
        ranked_experiences = await self._rank_experiences_for_job(
            all_experiences,
            job_description,
            job_title,
            industry_hint
        )

        # Select top experiences with appropriate descriptions
        selected_experiences = []
        for exp in ranked_experiences[:10]:
            # Get the best description for this job
            description = await self._get_tailored_description(
                exp,
                job_description,
                industry_hint
            )

            selected_experiences.append({
                **exp,
                'description': description,
                'match_score': exp.get('ai_match_score', 0)
            })

        # Get other sections
        profile = await self._get_profile(user_id)
        education = await self._get_education(user_id)
        skills = await self._get_skills_for_job(user_id, job_description, industry_hint)

        return {
            'profile': profile,
            'experiences': selected_experiences,
            'education': education,
            'skills': skills,
            'job_title': job_title,
            'industry': industry_hint,
            'customized': True,
            'assembled_at': 'now()'
        }

    async def _get_tailored_description(
        self,
        experience: Dict,
        job_description: str,
        industry: str
    ) -> str:
        """
        Gets or generates the most appropriate description for an experience
        based on job requirements
        """

        # Check if we have an industry-specific variant
        variants = experience.get('description_variants', {})
        if variants and industry in variants:
            return variants[industry]

        # Use relevance score to pick long vs short
        relevance = experience.get('relevance_score', 0)

        if relevance >= 7:
            # Highly relevant: use long description
            return experience.get('description_long') or experience.get('description')
        elif relevance >= 4:
            # Moderately relevant: could use AI to tailor
            if self.anthropic_client and job_description:
                return await self._ai_tailor_description(
                    experience,
                    job_description,
                    industry
                )
            return experience.get('description') or experience.get('description_short')
        else:
            # Low relevance: use short
            return experience.get('description_short') or experience.get('description')

    async def _ai_tailor_description(
        self,
        experience: Dict,
        job_description: str,
        industry: str
    ) -> str:
        """
        Uses AI to generate a tailored description emphasizing relevant aspects
        """

        if not self.anthropic_client:
            return experience.get('description', '')

        prompt = f"""Given this work experience and job description, create a tailored description that emphasizes the most relevant aspects.

WORK EXPERIENCE:
Company: {experience['company']}
Title: {experience['title']}
Original description: {experience.get('description_long') or experience.get('description')}

JOB DESCRIPTION:
{job_description[:1000]}

TARGET INDUSTRY: {industry}

Create a 75-100 word description that:
1. Highlights skills/experiences most relevant to the job
2. Uses keywords from the job description where accurate
3. Maintains factual accuracy
4. Sounds natural in Swedish

Return ONLY the tailored description, nothing else."""

        message = self.anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )

        return message.content[0].text.strip()

    async def _detect_industry_from_job(self, job_description: str, job_title: str) -> str:
        """Uses AI to detect industry from job description"""

        if not self.anthropic_client:
            # Fallback: simple keyword matching
            keywords = {
                'restaurant': ['restaurang', 'café', 'servitör', 'kock', 'barista'],
                'retail': ['butik', 'försäljning', 'kassa', 'säljare'],
                'tech': ['utvecklare', 'IT', 'data', 'programmering'],
                'healthcare': ['vård', 'omsorg', 'sjukvård'],
                'office': ['kontor', 'administration', 'koordinator']
            }

            text = (job_title + ' ' + job_description).lower()
            for industry, kw_list in keywords.items():
                if any(kw in text for kw in kw_list):
                    return industry

            return 'office'  # default

        prompt = f"""Analyze this Swedish job posting and determine the industry category.

JOB TITLE: {job_title}
JOB DESCRIPTION: {job_description[:500]}

Return ONLY one of these industry codes (nothing else):
- restaurant
- retail
- tech
- healthcare
- office
- customerservice
- industry
- content

Choose the BEST match."""

        message = self.anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=50,
            messages=[{"role": "user", "content": prompt}]
        )

        return message.content[0].text.strip().lower()

    async def _rank_experiences_for_job(
        self,
        experiences: List[Dict],
        job_description: str,
        job_title: str,
        industry: str
    ) -> List[Dict]:
        """Uses AI to rank experiences by relevance to specific job"""

        # Simple fallback: sort by relevance_scores for industry
        experiences_sorted = sorted(
            experiences,
            key=lambda x: x.get('relevance_scores', {}).get(industry, 0),
            reverse=True
        )

        if not self.anthropic_client:
            return experiences_sorted

        # TODO: Implement AI ranking for more sophisticated matching
        return experiences_sorted

    async def _get_all_experiences(self, user_id: str) -> List[Dict]:
        """Get all experiences for user"""
        result = await self.supabase.table('user_experiences').select('*').eq('user_id', user_id).execute()
        return result.data

    async def _get_profile(self, user_id: str) -> Dict:
        """Get user profile"""
        result = await self.supabase.table('user_profiles').select('*').eq('user_id', user_id).single().execute()
        return result.data

    async def _get_education(self, user_id: str) -> List[Dict]:
        """Get education entries"""
        result = await self.supabase.table('user_education').select('*').eq('user_id', user_id).order('sort_order').execute()
        return result.data

    async def _get_skills(self, user_id: str, industry: str) -> List[Dict]:
        """Get skills relevant to industry"""
        result = await self.supabase.table('user_skills').select('*').eq('user_id', user_id).in_('category', [industry, 'all']).execute()
        return result.data

    async def _get_skills_for_job(self, user_id: str, job_description: str, industry: str) -> List[Dict]:
        """Get skills most relevant to job"""
        # Start with industry skills
        return await self._get_skills(user_id, industry)

    async def _get_certifications(self, user_id: str, industry: str) -> List[Dict]:
        """Get relevant certifications"""
        # Get both work and tech certifications
        work_certs = await self.supabase.table('user_certifications').select('*').eq('user_id', user_id).execute()
        tech_certs = await self.supabase.table('tech_certifications').select('*').eq('user_id', user_id).execute()

        return {
            'work': work_certs.data,
            'tech': tech_certs.data
        }


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

"""
from cv_assembly import CVAssembler

# Initialize
assembler = CVAssembler(supabase_client)

# Get CV for restaurant industry
restaurant_cv = await assembler.assemble_cv_for_industry(
    user_id='da8ed517-3b67-4456-8831-6ed3cb7114ad',
    industry='restaurant',
    max_experiences=10
)

# Get CV tailored for specific job
job_cv = await assembler.assemble_cv_for_job(
    user_id='da8ed517-3b67-4456-8831-6ed3cb7114ad',
    job_description='Vi söker en servitör med erfarenhet av fine dining...',
    job_title='Servitör',
    industry_hint='restaurant'
)
"""
