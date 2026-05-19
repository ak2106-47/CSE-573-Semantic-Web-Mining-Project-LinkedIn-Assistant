from typing import List, Dict, Any, Optional
import math


def logistic(x: float) -> float:
	return 1.0 / (1.0 + math.exp(-x))


def estimate_person_ability(skill_signals: List[float]) -> float:
	"""
	Estimate θ (ability) from observed binary/graded signals.
	Here we accept a list of per-skill evidence in [-1, 1] and average it.
	"""
	if not skill_signals:
		return 0.0
	return max(-3.0, min(3.0, sum(skill_signals) / len(skill_signals)))


def rasch_probability(theta: float, difficulty_b: float) -> float:
	return logistic(theta - difficulty_b)


def score_items(theta: float, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
	scored = []
	for it in items:
		b = it.get("difficulty", 0.0) if it.get("difficulty") is not None else 0.0
		p = rasch_probability(theta, b)
		scored.append({**it, "probability": p})
	return scored


