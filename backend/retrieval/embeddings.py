from typing import List, Tuple, Optional
import numpy as np

try:
	from sentence_transformers import SentenceTransformer
except Exception:
	SentenceTransformer = None

try:
	import faiss  # type: ignore
except Exception:
	faiss = None

from ..models import Job


class EmbeddingIndex:
	def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
		self.model_name = model_name
		self.model = SentenceTransformer(model_name) if SentenceTransformer else None
		self.jobs: List[Job] = []
		self.vecs: Optional[np.ndarray] = None
		self.index = None

	def _job_text(self, job: Job) -> str:
		parts = [job.title or "", job.company or "", job.location or "", job.description or ""]
		reqs = [r.value for r in job.requirements]
		return "\n".join(parts + reqs)

	def rebuild(self, jobs: List[Job]) -> None:
		self.jobs = jobs
		if not self.model or not jobs:
			self.vecs = None
			self.index = None
			return
		texts = [self._job_text(j) for j in jobs]
		vecs = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
		self.vecs = vecs.astype("float32")
		if faiss is None:
			self.index = None
			return
		d = self.vecs.shape[1]
		self.index = faiss.IndexFlatIP(d)
		self.index.add(self.vecs)

	def rank(self, query: str, top_k: int = 20) -> List[Tuple[Job, float]]:
		if not self.model or not self.jobs:
			return []
		q = self.model.encode([query], convert_to_numpy=True, normalize_embeddings=True).astype("float32")
		if self.index is not None:
			D, I = self.index.search(q, min(top_k, len(self.jobs)))
			return [(self.jobs[int(i)], float(D[0][k])) for k, i in enumerate(I[0])]
		# fallback: pure numpy cosine with precomputed vecs
		if self.vecs is None:
			return []
		scores = (self.vecs @ q[0]).ravel()
		idx_scores = sorted(list(enumerate(scores)), key=lambda x: x[1], reverse=True)[:top_k]
		return [(self.jobs[i], float(s)) for i, s in idx_scores]


