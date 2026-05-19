from typing import Dict, Any, List
import re

# Skill difficulty tiers
SKILL_TIERS = {
    # Easy/Common (b = -0.2 to 0.0)
    "excel": -0.2, "microsoft office": -0.2, "email": -0.2,
    "communication": -0.1, "teamwork": -0.1,
    
    # Standard tech (b = 0.0 to 0.3)
    "python": 0.1, "java": 0.1, "javascript": 0.1, "sql": 0.1,
    "react": 0.2, "node": 0.2, "django": 0.2, "flask": 0.2,
    "aws": 0.25, "azure": 0.25, "docker": 0.25,
    "pandas": 0.15, "numpy": 0.15,
    
    # Advanced (b = 0.4 to 0.7)
    "machine learning": 0.4, "deep learning": 0.5,
    "nlp": 0.45, "computer vision": 0.45,
    "kubernetes": 0.5, "distributed systems": 0.6,
    "tensorflow": 0.4, "pytorch": 0.4,
    "system design": 0.6, "scalability": 0.55,
    
    # Expert/Rare (b = 0.7+)
    "compiler design": 0.8, "blockchain": 0.7,
    "quantum computing": 0.9, "kernel development": 0.85,
}

# Seniority level mapping
SENIORITY_DIFFICULTY = {
    "intern": -0.4,
    "entry level": -0.2,
    "entry": -0.2,
    "junior": -0.2,
    "associate": 0.0,
    "mid-level": 0.2,
    "mid level": 0.2,
    "mid": 0.2,
    "senior": 0.4,
    "mid-senior": 0.3,
    "mid senior": 0.3,
    "lead": 0.5,
    "staff": 0.6,
    "principal": 0.7,
    "director": 0.8,
    "executive": 0.9,
}

DEFAULT_SKILL_DIFFICULTY = 0.2  # Increased from 0.0
DEFAULT_EDU_DIFFICULTY = -0.25
DEFAULT_EXP_DIFFICULTY = 0.25
DEFAULT_OTHER_DIFFICULTY = 0.0


def _estimate_skill_difficulty(skill_name: str) -> float:
    """
    Estimate difficulty for a skill based on rarity/complexity.
    """
    skill_lower = skill_name.lower().strip()
    
    # Check exact matches first
    if skill_lower in SKILL_TIERS:
        return SKILL_TIERS[skill_lower]
    
    # Check partial matches
    for skill_key, difficulty in SKILL_TIERS.items():
        if skill_key in skill_lower:
            return difficulty
    
    # Default for unknown skills
    return DEFAULT_SKILL_DIFFICULTY


def _extract_requirements_from_text(text: str) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    lower = text.lower()

    # 1. Extract Skills with varying difficulty
    found_skills = set()
    for skill in SKILL_TIERS.keys():
        if skill in lower and skill not in found_skills:
            found_skills.add(skill)
            items.append({
                "kind": "skill",
                "value": skill.title(),
                "difficulty": _estimate_skill_difficulty(skill)
            })

    # 2. Extract Seniority Level (NEW!)
    for seniority, difficulty in SENIORITY_DIFFICULTY.items():
        pattern = rf"\b{re.escape(seniority)}\s*(level|engineer|developer|position)?\b"
        if re.search(pattern, lower):
            items.append({
                "kind": "experience",
                "value": f"{seniority.title()} level",
                "difficulty": difficulty
            })
            break  # Only capture the most specific seniority

    # 3. Extract Education
    edu_match = re.search(
        r"\b(bachelor'?s?|bs|ba|master'?s?|ms|ma|phd|doctorate|doctoral)\b",
        lower
    )
    if edu_match:
        edu = edu_match.group(1)
        # Adjust difficulty by degree level
        edu_difficulty = DEFAULT_EDU_DIFFICULTY
        if "master" in edu or "ms" in edu or "ma" in edu:
            edu_difficulty = 0.0  # Master's is neutral
        elif "phd" in edu or "doctor" in edu:
            edu_difficulty = 0.2  # PhD is harder to have
        
        items.append({
            "kind": "education",
            "value": edu.title(),
            "difficulty": edu_difficulty
        })

    # 4. Extract Years of Experience (with better scaling)
    yrs_match = re.findall(r"(\d+)\+?\s*years?\s+(?:of\s+)?experience", lower)
    if yrs_match:
        max_yrs = max(int(y) for y in yrs_match)
        # Scale difficulty: 1-2 years = 0.1, 5 years = 0.4, 10+ years = 0.7
        years_difficulty = DEFAULT_EXP_DIFFICULTY + (max_yrs - 2) * 0.1
        years_difficulty = max(0.0, min(0.8, years_difficulty))  # Clamp to [0, 0.8]
        
        items.append({
            "kind": "experience",
            "value": f"{max_yrs}+ years",
            "difficulty": years_difficulty
        })

    # 5. Other requirements (but filter out noise)
    for line in text.splitlines():
        if re.match(r"^\s*[-*•]\s+", line):
            val = re.sub(r"^\s*[-*•]\s+", "", line).strip()
            # Only add meaningful "other" items (skip if too short or already captured)
            if len(val) > 15 and len(val) < 200:
                # Try to categorize as skill or experience first
                if not any(skill in val.lower() for skill in found_skills):
                    items.append({
                        "kind": "other",
                        "value": val[:100],  # Truncate long descriptions
                        "difficulty": DEFAULT_OTHER_DIFFICULTY
                    })

    return items


def parse_job_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    title = (payload.get("title") or "").strip() or None
    company = (payload.get("company") or "").strip() or None
    location = (payload.get("location") or "").strip() or None
    description = (payload.get("description") or "").strip() or None
    raw_text = (payload.get("raw_text") or "").strip()

    text = "\n".join([t for t in [title, company, location, description, raw_text] if t])
    requirements = _extract_requirements_from_text(text)
    
    return {
        "title": title,
        "company": company,
        "location": location,
        "description": description or raw_text or None,
        "requirements": requirements,
    }
