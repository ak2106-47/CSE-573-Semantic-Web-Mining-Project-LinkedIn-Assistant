from typing import List, Dict, Any
from collections import defaultdict
from rapidfuzz import fuzz

from ..models import UserProfile, Job, JobOut, RankedJob, SuggestionOut
from .rasch import estimate_person_ability, score_items


def _normalize(s: str) -> str:
	return (s or "").strip().lower()


def _skill_evidence(profile: UserProfile) -> Dict[str, float]:
	evidence = {}
	for s in profile.skills:
		name = _normalize(s.name)
		if not name:
			continue
		level = (s.level or "").lower()
		if "beginner" in level:
			evidence[name] = 0.2
		elif "intermediate" in level:
			evidence[name] = 0.5
		elif "advanced" in level or "expert" in level:
			evidence[name] = 0.8
		else:
			evidence[name] = 0.4
	# Add inferred evidence from experiences keywords
	for e in profile.experiences:
		for token in (e.title or "").lower().split():
			if token.isalpha():
				evidence.setdefault(token, 0.2)
	return evidence


def _match_skill_value(skill: str, evidence: Dict[str, float]) -> float:
	if skill in evidence:
		return evidence[skill]
	# fuzzy match
	best = 0.0
	for k in evidence.keys():
		score = fuzz.partial_ratio(skill, k) / 100.0
		if score > best:
			best = score * evidence[k]
	return best


def _profile_theta(profile: UserProfile) -> float:
	ev = _skill_evidence(profile)
	return estimate_person_ability(list(ev.values()))


def _score_job(profile: UserProfile, job: Job) -> RankedJob:
	ev = _skill_evidence(profile)
	theta = _profile_theta(profile)
	items: List[Dict[str, Any]] = []
	for r in job.requirements:
		if r.kind == "skill":
			feat = _match_skill_value(r.value.lower(), ev)
		elif r.kind == "experience":
			feat = 0.5  # neutral evidence
		elif r.kind == "education":
			feat = 0.5
		else:
			feat = 0.4
		items.append({"kind": r.kind, "value": r.value, "difficulty": r.difficulty if r.difficulty is not None else 0.0, "evidence": feat})
	scored = score_items(theta, items)
	# aggregate score as average probability
	if scored:
		avg = sum(it["probability"] for it in scored) / len(scored)
	else:
		avg = 0.0
	return RankedJob(
		job=job.to_out(),
		score=round(avg, 4),
		item_scores=[{k: (round(v, 4) if isinstance(v, float) else v) for k, v in it.items()} for it in scored],
	)


def suggest_jobs_for_profile(profile: UserProfile, jobs: List[Job]) -> SuggestionOut:
	ranked = [_score_job(profile, j) for j in jobs]
	ranked.sort(key=lambda r: r.score, reverse=True)
	explanation = (
		"Scores are computed with a Rasch-style model: P = logistic(θ - b) per requirement.\n"
		"θ is estimated from your skills and experience; b is the difficulty per job item."
	)
	return SuggestionOut(profile=profile.to_out(), recommendations=ranked, explanation=explanation)


