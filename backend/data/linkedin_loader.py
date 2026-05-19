from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional
import random

import pandas as pd

DATA_FILE = Path(__file__).resolve().parents[2] / "linkedin_job_posts_insights.xlsx"

# ============================================================================
# DIFFICULTY MAPPINGS
# ============================================================================

SENIORITY_DIFFICULTY = {
    "internship": -0.4,
    "entry level": -0.3,
    "associate": -0.1,
    "mid-senior level": 0.2,
    "mid level": 0.2,
    "senior": 0.4,
    "lead": 0.5,
    "staff": 0.6,
    "principal": 0.7,
    "director": 0.7,
    "vice president": 0.8,
    "executive": 0.9,
    "c-level": 0.9,
}

FUNCTION_DIFFICULTY = {
    # Basic/Support roles
    "administrative": -0.1,
    "customer service": -0.1,
    "human resources": 0.0,
    
    # Business roles
    "sales": 0.1,
    "marketing": 0.1,
    "business development": 0.2,
    "consulting": 0.3,
    
    # Technical roles
    "information technology": 0.2,
    "engineering and information technology": 0.25,
    "software engineering": 0.4,
    "engineering": 0.3,
    
    # Specialized technical
    "data science": 0.5,
    "machine learning": 0.6,
    "artificial intelligence": 0.6,
    "research": 0.5,
    "product management": 0.4,
    
    # Leadership/Strategy
    "operations": 0.3,
    "program and project management": 0.4,
    "strategy": 0.5,
}

# Title keywords that boost difficulty
TITLE_KEYWORDS = {
    # Seniority levels
    "senior": 0.25,
    "sr.": 0.25,
    "sr ": 0.25,
    "lead": 0.35,
    "principal": 0.55,
    "staff": 0.45,
    "chief": 0.7,
    "director": 0.6,
    "head of": 0.6,
    "vp": 0.7,
    "vice president": 0.7,
    
    # Technical specializations
    "data scientist": 0.4,
    "data science": 0.4,
    "machine learning": 0.55,
    "ml engineer": 0.55,
    "ai engineer": 0.55,
    "deep learning": 0.6,
    "nlp": 0.5,
    "computer vision": 0.5,
    
    # Development roles
    "full stack": 0.3,
    "fullstack": 0.3,
    "backend": 0.3,
    "back-end": 0.3,
    "frontend": 0.25,
    "front-end": 0.25,
    
    # Infrastructure/DevOps
    "devops": 0.4,
    "site reliability": 0.5,
    "sre": 0.5,
    "cloud engineer": 0.4,
    "cloud architect": 0.5,
    "platform engineer": 0.4,
    
    # Specialized skills
    "distributed systems": 0.55,
    "scalability": 0.5,
    "kubernetes": 0.5,
    "docker": 0.3,
    "aws": 0.3,
    "azure": 0.3,
    "gcp": 0.3,
}

# Industry complexity modifiers
INDUSTRY_MODIFIERS = {
    "financial services": 0.15,
    "banking": 0.15,
    "healthcare": 0.15,
    "pharmaceuticals": 0.15,
    "consulting": 0.1,
    "research": 0.1,
    "defense": 0.2,
    "aerospace": 0.2,
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _clean(value: Optional[str]) -> Optional[str]:
    """Clean and normalize string values."""
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    value = str(value).strip()
    return value if value else None


def _extract_title_difficulty_boost(title: str) -> float:
    """
    Extract difficulty boost from job title based on keywords.
    Returns the highest matching difficulty boost.
    """
    if not title:
        return 0.0
    
    title_lower = title.lower()
    max_boost = 0.0
    
    for keyword, boost in TITLE_KEYWORDS.items():
        if keyword in title_lower:
            max_boost = max(max_boost, boost)
    
    return max_boost


def _get_industry_modifier(industry: Optional[str]) -> float:
    """Get difficulty modifier based on industry complexity."""
    if not industry:
        return 0.0
    
    industry_lower = industry.lower()
    
    for industry_key, modifier in INDUSTRY_MODIFIERS.items():
        if industry_key in industry_lower:
            return modifier
    
    return 0.0


def _estimate_difficulty(
    kind: str, 
    value: str, 
    context: Optional[Dict] = None
) -> float:
    """
    Estimate difficulty for a job requirement.
    
    Args:
        kind: "skill", "experience", or "other"
        value: The requirement value/name
        context: Optional context dict with:
            - seniority: Seniority level
            - title: Job title
            - industry: Industry name
            - company: Company name
    
    Returns:
        Difficulty score (b) in range [-0.5, 1.0]
    """
    value_lower = value.lower().strip()
    base_difficulty = 0.0
    
    # -----------------------------
    # SKILL DIFFICULTY
    # -----------------------------
    if kind == "skill":
        # Get base difficulty from function mapping
        for func_key, func_diff in FUNCTION_DIFFICULTY.items():
            if func_key in value_lower:
                base_difficulty = func_diff
                break
        else:
            # Default for unmapped skills
            base_difficulty = 0.2
        
        # Add title-based boost
        if context and context.get("title"):
            title_boost = _extract_title_difficulty_boost(context["title"])
            base_difficulty += title_boost
        
        # Add industry complexity modifier
        if context and context.get("industry"):
            industry_mod = _get_industry_modifier(context["industry"])
            base_difficulty += industry_mod
        
        # Add seniority adjustment for skills
        if context and context.get("seniority"):
            seniority = context["seniority"].lower()
            if "senior" in seniority or "lead" in seniority:
                base_difficulty += 0.15
            elif "principal" in seniority or "staff" in seniority:
                base_difficulty += 0.25
            elif "director" in seniority or "executive" in seniority:
                base_difficulty += 0.3
            elif "mid" in seniority:
                base_difficulty += 0.05
            elif "entry" in seniority or "junior" in seniority:
                base_difficulty -= 0.05
    
    # -----------------------------
    # EXPERIENCE DIFFICULTY
    # -----------------------------
    elif kind == "experience":
        # Map seniority to difficulty
        for seniority_key, seniority_diff in SENIORITY_DIFFICULTY.items():
            if seniority_key in value_lower:
                base_difficulty = seniority_diff
                break
        else:
            # Default for unmapped experience levels
            base_difficulty = 0.1
    
    # -----------------------------
    # OTHER REQUIREMENTS
    # -----------------------------
    elif kind == "other":
        base_difficulty = 0.0
    
    # Clamp to reasonable range
    return max(-0.5, min(1.0, base_difficulty))


# ============================================================================
# MAIN LOADER FUNCTION
# ============================================================================

def load_linkedin_records(limit: Optional[int] = None) -> List[Dict]:
    """
    Load LinkedIn job records from Excel file with difficulty-scored requirements.
    
    Args:
        limit: Optional maximum number of records to load
    
    Returns:
        List of job dictionaries with title, company, location, description, 
        and requirements (with difficulty scores)
    """
    if not DATA_FILE.exists():
        return []

    df = pd.read_excel(DATA_FILE)
    records: List[Dict] = []

    for idx, row in df.iterrows():
        if limit is not None and len(records) >= limit:
            break

        # Extract and clean basic fields
        title = _clean(row.get("job_title"))
        company = _clean(row.get("company_name"))
        location = _clean(row.get("location"))
        job_function = _clean(row.get("job_function"))
        employment_type = _clean(row.get("employment_type"))
        industry = _clean(row.get("industry"))
        hiring_status = _clean(row.get("hiring_status"))
        seniority_level = _clean(row.get("seniority_level"))
        
        # Parse date
        date_val = row.get("date")
        date_str = None
        if pd.notna(date_val):
            try:
                date_str = pd.to_datetime(date_val).strftime("%Y-%m-%d")
            except Exception:
                date_str = str(date_val)

        # Build description from available fields
        desc_parts = []
        if job_function:
            desc_parts.append(f"Function: {job_function}")
        if industry:
            desc_parts.append(f"Industry: {industry}")
        if employment_type:
            desc_parts.append(f"Type: {employment_type}")
        if hiring_status:
            desc_parts.append(f"Status: {hiring_status}")
        if seniority_level:
            desc_parts.append(f"Level: {seniority_level}")
        if date_str:
            desc_parts.append(f"Posted: {date_str}")

        # Create context for difficulty estimation
        context = {
            "title": title,
            "seniority": seniority_level,
            "industry": industry,
            "company": company
        }

        # Build requirements with difficulty scores
        requirements = []
        
        # Add job function as skill requirement
        if job_function:
            requirements.append({
                "kind": "skill",
                "value": job_function,
                "difficulty": _estimate_difficulty("skill", job_function, context)
            })
        
        # Add seniority level as experience requirement
        if seniority_level:
            requirements.append({
                "kind": "experience",
                "value": seniority_level,
                "difficulty": _estimate_difficulty("experience", seniority_level, context)
            })
        
        # Add employment type as other requirement
        if employment_type:
            emp_value = f"Employment: {employment_type}"
            requirements.append({
                "kind": "other",
                "value": emp_value,
                "difficulty": 0.0
            })
        
        # Add industry as other requirement
        if industry:
            ind_value = f"Industry: {industry}"
            requirements.append({
                "kind": "other",
                "value": ind_value,
                "difficulty": 0.0
            })
        
        # Add hiring status as other requirement
        if hiring_status:
            status_value = f"Hiring: {hiring_status}"
            requirements.append({
                "kind": "other",
                "value": status_value,
                "difficulty": 0.0
            })

        # Create final record
        records.append({
            "title": title or "Untitled",
            "company": company,
            "location": location,
            "description": " • ".join(desc_parts) if desc_parts else None,
            "requirements": requirements,
        })

    return records
