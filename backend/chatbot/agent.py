from typing import List, Optional, Dict, Any
import os
from dataclasses import dataclass

from ..models import ChatMessage, ChatResponse, UserProfile, Job
from ..matching.matcher import suggest_jobs_for_profile


JOB_INTENT_KEYWORDS = ("job", "role", "position", "opening", "apply", "recommend")
RESUME_INTENT_KEYWORDS = ("resume", "cv", "bullet", "ats", "experience", "summary")
NETWORK_INTENT_KEYWORDS = ("network", "linkedin", "reach", "message", "connect", "intro")
UPSKILL_INTENT_KEYWORDS = ("skill", "upskill", "learn", "course", "cert", "improve", "grow")


def default_system_prompt() -> str:
	return """You are the LinkedIn Assistant: a transparent career copilot.

Core principles:
- Always ground advice in the parsed resume, dataset jobs, or Rasch probabilities.
- Explain why recommendations make sense (θ vs. difficulty b, missing skills, or profile evidence).
- Offer tactical guidance the user can act on immediately (bullets, scripts, next steps).
- When data is missing (no resume or no dataset jobs), say so and describe how to fix it.
- Keep a confident but warm tone; no filler or repeated canned text."""


def default_user_guidance_prompt() -> str:
	return """Assistant guidance:
- Start with a concise profile snapshot.
- Shape the rest of your answer around the user’s actual question (jobs, resume polish, networking, or upskilling).
- Cite Rasch/Guttman signals for job matches: title, company, and requirement-level probabilities.
- Offer actionable resume bullets, outreach templates, or skill plans when the user asks for them.
- End with two or three clear next steps that reflect what the user requested."""


def _detect_intents(user_text: str) -> Dict[str, bool]:
	"""Return a map describing which high-level intent (jobs/resume/network/upskill) appears in the user text."""
	lower = user_text.lower()
	return {
		"jobs": any(keyword in lower for keyword in JOB_INTENT_KEYWORDS),
		"resume": any(keyword in lower for keyword in RESUME_INTENT_KEYWORDS),
		"network": any(keyword in lower for keyword in NETWORK_INTENT_KEYWORDS),
		"upskill": any(keyword in lower for keyword in UPSKILL_INTENT_KEYWORDS),
	}


def _profile_snapshot(profile: UserProfile) -> str:
	"""Summarize key fields from the parsed resume so replies always start with context."""
	skills = ", ".join(s.name for s in profile.skills) or "n/a"
	return f"**Profile snapshot**: {profile.full_name or 'Candidate'} · Skills: {skills} · Experience entries: {len(profile.experiences)} · Education entries: {len(profile.educations)}"


def _missing_skills(profile: UserProfile, recommendations: List[Any], limit: int = 3) -> List[str]:
	"""Derive top skill gaps between the resume and current job recommendations."""
	owned = {s.name.lower() for s in profile.skills if s.name}
	missing: List[str] = []
	seen = set()
	for rec in recommendations:
		for item in rec.item_scores:
			if (item.get("kind") or "").lower() != "skill":
				continue
			value = (item.get("value") or "").strip()
			if not value:
				continue
			value_lower = value.lower()
			if value_lower not in owned and value_lower not in seen:
				missing.append(value)
				seen.add(value_lower)
			if len(missing) >= limit:
				return missing
	return missing


def _top_companies(recommendations: List[Any], limit: int = 2) -> List[str]:
	"""Capture the first few distinct companies from the ranked list."""
	companies = []
	for rec in recommendations:
		company = (rec.job.company or "").strip()
		if company and company not in companies:
			companies.append(company)
		if len(companies) >= limit:
			break
	return companies


@dataclass
class ChatAgent:
	system_prompt: str
	user_guidance_prompt: str

	def respond(self, messages: List[ChatMessage], profile: Optional[UserProfile], jobs: List[Job]) -> ChatResponse:
		"""Return a conversational answer that reflects the parsed profile, dataset jobs, and user intent."""
		last_user = next((m.content for m in reversed(messages) if m.role == "user"), "")
		if not last_user:
			return ChatResponse(
				answer="Hi! Upload your resume or ask for recommendations, resume tips, or networking ideas.",
				context_sources=[],
			)

		if not profile:
			return ChatResponse(
				answer="I’d love to personalize this, but I don’t have your resume yet. Upload it so I can analyze your skills, estimate θ, and recommend roles.",
				context_sources=[],
			)

		response_lines = [_profile_snapshot(profile)]
		intents = _detect_intents(last_user)
		intent_requested = any(intents.values())

		if not jobs:
			response_lines.append(
				"\nI don’t have any jobs loaded yet. Run a dataset search in Step 2 so I can score real postings for you."
			)
			return ChatResponse(answer="\n".join(response_lines), context_sources=[{"type": "profile"}])

		suggestions = suggest_jobs_for_profile(profile, jobs)
		recommendations = suggestions.recommendations if suggestions else []

		# Job insights
		if recommendations:
			if intents["jobs"] or not intent_requested:
				response_lines.append("\n**Job matches based on your request**")
				for rec in recommendations[:3]:
					reasons = rec.item_scores[:2]
					reason_text = "; ".join(
						f"{(item.get('kind') or 'item').upper()}: {item.get('value', 'n/a')} (P={float(item.get('probability', 0.0)):.2f})"
						for item in reasons
					)
					response_lines.append(
						f"- {rec.job.title or 'Untitled'} @ {rec.job.company or 'Unknown'} — fit {(rec.score*100):.0f}% · {reason_text or 'Evidence unavailable.'}"
					)
		else:
			if intents["jobs"] or not intent_requested:
				response_lines.append(
					"\nI couldn’t find any dataset matches yet. Re-run Step 2 with a different keyword (e.g., location + title) so I can rerank real postings."
				)

		# Resume guidance
		if intents["resume"]:
			response_lines.append("\n**Resume tuning ideas tailored to your request**")
			if profile.experiences:
				exp = profile.experiences[0]
				response_lines.append(
					f"- Reframe **{exp.title or 'your role'} at {exp.company or 'your company'}** with a quantified win (e.g., “Led {exp.title or 'key project'} that improved {exp.company or 'team'} KPIs by 15%”)."
				)
			response_lines.append("- Mirror the top skills from target postings (see matches above) in both the summary and the first bullet of each role.")
			response_lines.append("- Keep bullets in ACTION + METRIC + RESULT format so ATS scoring aligns with Rasch item evidence.")

		# Networking advice
		if intents["network"]:
			companies = _top_companies(recommendations)
			target = companies[0] if companies else "your target company"
			response_lines.append("\n**Networking & outreach**")
			response_lines.append(
				f"- Message a leader at {target} referencing a shared theme: “Hi {{Name}}, I noticed your work on {target}’s data platform. I’m exploring similar problems around {profile.skills[0].name if profile.skills else 'data enablement'}—would you be open to a quick chat?”"
			)
			response_lines.append("- Join two relevant communities/events this week and ask one question tied directly to your goal (e.g., Rasch transparency, resume tailoring).")

		# Upskilling recommendations
		if intents["upskill"]:
			gaps = _missing_skills(profile, recommendations)
			response_lines.append("\n**Upskilling focus**")
			if gaps:
				response_lines.append(f"- Target these recurring skills from current matches: {', '.join(gaps)}.")
			else:
				response_lines.append("- Your profile covers most listed skills; deepen expertise by creating a mini case study aligned with the top requirement in each role.")
			response_lines.append("- Schedule a weekly review where you map new learning back to θ vs. b to keep progress measurable.")

		# Default guidance if no specific intent
		if not intent_requested:
			response_lines.append("\n**Resume polish**")
			response_lines.append("- Highlight quantified wins (e.g., “Improved NPS by 15%”) and align keywords with the dataset roles above.")
			response_lines.append("- Mirror requirements that have the highest Rasch probability gap.")

			response_lines.append("\n**Networking & outreach**")
			response_lines.append("- Reach out to peers at companies listed above with a note tying your work to their current initiatives.")

		response_lines.append("\n**Next steps**")
		next_steps = []
		if recommendations:
			next_steps.append("Apply: shortlist the top 2 roles above and tailor bullets to their highest-b requirements.")
		else:
			next_steps.append("Apply: rerun Step 2 with refreshed keywords so I can produce new Rasch matches.")
		if intents["network"]:
			next_steps.append("Network: send two outreach messages this week referencing the insight you just asked about.")
		else:
			next_steps.append("Network: connect with alumni or team leads at your target companies using a concrete hook from your resume.")
		if intents["upskill"]:
			next_steps.append("Upskill: block 2 hours to practice the missing skills listed above and jot down measurable outcomes.")
		else:
			next_steps.append("Upskill: pick one recurrent skill from the dataset roles and showcase it via a quick project or blog post.")
		for step in next_steps:
			response_lines.append(f"- {step}")

		context_sources: List[Dict[str, Any]] = []
		if profile:
			context_sources.append({"type": "profile", "skills": [s.name for s in profile.skills]})
		if jobs:
			context_sources.append({"type": "jobs", "count": len(jobs)})
		return ChatResponse(answer="\n".join(response_lines), context_sources=context_sources)


