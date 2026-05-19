from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ..models import Job


def _job_text(job: Job) -> str:
	parts = [job.title or "", job.company or "", job.location or "", job.description or ""]
	reqs = [r.value for r in job.requirements]
	return "\n".join(parts + reqs)


def rank_jobs_tfidf(query: str, jobs: List[Job], top_k: int = 20) -> List[Tuple[Job, float]]:
	if not jobs:
		return []
	corpus = [_job_text(j) for j in jobs]
	vectorizer = TfidfVectorizer(min_df=1, max_df=0.95, ngram_range=(1, 2))
	X = vectorizer.fit_transform(corpus + [query])
	job_mat = X[:-1]
	q_vec = X[-1]
	scores = cosine_similarity(job_mat, q_vec).ravel()
	idx_scores = sorted(list(enumerate(scores)), key=lambda x: x[1], reverse=True)[:top_k]
	return [(jobs[i], float(s)) for i, s in idx_scores]


