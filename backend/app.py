from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from itertools import count
from typing import List, Optional

from rapidfuzz import fuzz

from .chatbot.agent import ChatAgent, default_system_prompt, default_user_guidance_prompt
from .data.linkedin_loader import load_linkedin_records
from .matching.matcher import suggest_jobs_for_profile
from .models import (
	ChatMessage,
	ChatResponse,
	Job,
	JobOut,
	JobRequirement,
	ProfileOut,
	SuggestionOut,
	UserProfile,
)
from .parsers.job_parser import parse_job_payload
from .parsers.resume_parser import parse_resume_file
from .retrieval.embeddings import EmbeddingIndex
from .retrieval.tfidf import rank_jobs_tfidf

app = FastAPI(title="CSE573 Job Search Agent - Backend", version="0.1.0")

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=False,
	allow_methods=["*"],
	allow_headers=["*"],
)


# In-memory state (single user prototype)
profile_state: Optional[UserProfile] = None
jobs_state: List[Job] = []
dataset_jobs: List[Job] = []
job_id_sequence = count(1)
dataset_id_sequence = count(1_000_000)
requirement_id_sequence = count(1)
profile_child_sequence = count(1)
embed_index = EmbeddingIndex()


def _hydrate_dataset_jobs() -> None:
	global dataset_jobs
	records = load_linkedin_records()
	hydrated: List[Job] = []
	for record in records:
		job_id = next(dataset_id_sequence)
		reqs = []
		for req in record.get("requirements", []):
			reqs.append(
				JobRequirement(
					id=next(requirement_id_sequence),
					job_id=job_id,
					kind=req.get("kind", "other"),
					value=req.get("value", ""),
					difficulty=req.get("difficulty"),
				)
			)
		hydrated.append(
			Job(
				id=job_id,
				title=record.get("title"),
				company=record.get("company"),
				location=record.get("location"),
				description=record.get("description"),
				requirements=reqs,
			)
		)
	dataset_jobs = hydrated


@app.on_event("startup")
def _startup() -> None:
	try:
		_hydrate_dataset_jobs()
	except Exception:
		dataset_jobs.clear()


@app.post("/api/profile/resume", response_model=ProfileOut)
async def upload_resume(file: UploadFile = File(...)) -> ProfileOut:
	global profile_state
	if file.content_type not in {"application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"}:
		raise HTTPException(status_code=400, detail="Unsupported file type")
	profile = parse_resume_file(await file.read(), filename=file.filename, content_type=file.content_type)
	profile.id = 1
	for item in profile.educations:
		item.id = next(profile_child_sequence)
	for item in profile.experiences:
		item.id = next(profile_child_sequence)
	for item in profile.skills:
		item.id = next(profile_child_sequence)
	profile_state = profile
	return profile.to_out()


@app.get("/api/profile", response_model=Optional[ProfileOut])
def get_profile() -> Optional[ProfileOut]:
	return profile_state.to_out() if profile_state else None


@app.post("/api/jobs", response_model=JobOut)
async def add_job(
	title: Optional[str] = Form(None),
	company: Optional[str] = Form(None),
	location: Optional[str] = Form(None),
	description: Optional[str] = Form(None),
	raw_text: Optional[str] = Form(None),
) -> JobOut:
	global jobs_state
	job_struct = parse_job_payload(
		{
			"title": title,
			"company": company,
			"location": location,
			"description": description,
			"raw_text": raw_text,
		}
	)
	job = Job.from_struct(job_struct)
	job.id = next(job_id_sequence)
	for req in job.requirements:
		req.id = next(requirement_id_sequence)
		req.job_id = job.id
	jobs_state.append(job)
	return job.to_out()


@app.get("/api/jobs", response_model=List[JobOut])
def list_jobs(q: Optional[str] = None) -> List[JobOut]:
	jobs = jobs_state
	if not q:
		return [j.to_out() for j in jobs]
	q_lower = q.lower()
	filtered = [j for j in jobs if q_lower in (j.title or "").lower() or q_lower in (j.company or "").lower() or q_lower in (j.description or "").lower()]
	return [j.to_out() for j in filtered]


@app.get("/api/suggest", response_model=SuggestionOut)
def suggest() -> SuggestionOut:
	if not profile_state:
		raise HTTPException(status_code=400, detail="Profile not found. Upload a resume first.")
	if not jobs_state:
		return SuggestionOut(profile=profile_state.to_out(), recommendations=[], explanation="Add jobs to see ranked matches.")
	return suggest_jobs_for_profile(profile_state, jobs_state)


@app.post("/api/chat", response_model=ChatResponse)
def chat(messages: List[ChatMessage]) -> ChatResponse:
	agent = ChatAgent(system_prompt=default_system_prompt(), user_guidance_prompt=default_user_guidance_prompt())
	return agent.respond(messages=messages, profile=profile_state, jobs=jobs_state)


@app.get("/api/rank/baseline")
def baseline_rank(q: str, top_k: int = 20):
	results = rank_jobs_tfidf(q, jobs_state, top_k=top_k)
	return [{"job": j.to_out(), "score": round(s, 4)} for j, s in results]


@app.get("/api/rank/semantic")
def semantic_rank(q: str, top_k: int = 20):
	embed_index.rebuild(jobs_state)
	results = embed_index.rank(q, top_k=top_k)
	return [{"job": j.to_out(), "score": round(float(s), 4)} for j, s in results]


def _search_dataset(query: str, limit: int = 20) -> List[Job]:
	if not query.strip():
		return []
	q = query.strip().lower()
	scored = []
	for job in dataset_jobs:
		parts = " ".join(
			filter(
				None,
				[
					(job.title or ""),
					(job.company or ""),
					(job.location or ""),
					(job.description or ""),
				],
			)
		).lower()
		if not parts:
			continue
		score = fuzz.partial_ratio(q, parts)
		if q in parts:
			score += 25
		if score > 0:
			scored.append((score, job))
	scored.sort(key=lambda pair: pair[0], reverse=True)
	return [job for _, job in scored[:limit]]


@app.get("/api/jobs/search", response_model=List[JobOut])
def search_dataset_jobs(q: str, limit: int = 20) -> List[JobOut]:
	if not q.strip():
		raise HTTPException(status_code=400, detail="Provide a search query.")
	if not dataset_jobs:
		raise HTTPException(status_code=503, detail="Job dataset is not available.")
	results = _search_dataset(q, limit=limit)
	if results:
		global jobs_state
		# copy references so manual list reflects dataset selection
		jobs_state = [job for job in results]
	return [job.to_out() for job in results]


