from dataclasses import dataclass
from typing import Optional, List

from ..models import UserProfile, Job, ChatMessage, ChatResponse
from ..parsers.resume_parser import parse_resume_file
from ..parsers.job_parser import parse_job_payload
from ..matching.matcher import suggest_jobs_for_profile
from ..retrieval.tfidf import rank_jobs_tfidf


@dataclass
class ParserAgent:
	def parse_resume(self, data: bytes, filename: str, content_type: str) -> UserProfile:
		return parse_resume_file(data, filename, content_type)

	def parse_job(self, payload: dict) -> dict:
		return parse_job_payload(payload)


@dataclass
class RecommenderAgent:
	def suggest(self, profile: UserProfile, jobs: List[Job]):
		return suggest_jobs_for_profile(profile, jobs)

	def baseline_rank(self, query: str, jobs: List[Job]):
		return rank_jobs_tfidf(query, jobs)


@dataclass
class CriticAgent:
	def critique(self, messages: List[ChatMessage]) -> Optional[str]:
		# Placeholder: ensure responses are factual, cite sources when possible
		return None


@dataclass
class Orchestrator:
	parser: ParserAgent
	recommender: RecommenderAgent
	critic: CriticAgent

	def run_chat(self, messages: List[ChatMessage]) -> Optional[ChatResponse]:
		# Placeholder: integrate agents lifecycle if needed
		return None


