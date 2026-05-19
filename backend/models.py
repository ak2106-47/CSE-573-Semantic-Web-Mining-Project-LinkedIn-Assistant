from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class Education(BaseModel):
	id: Optional[int] = None
	institution: Optional[str] = None
	degree: Optional[str] = None
	field_of_study: Optional[str] = None
	start_year: Optional[int] = None
	end_year: Optional[int] = None


class Experience(BaseModel):
	id: Optional[int] = None
	title: Optional[str] = None
	company: Optional[str] = None
	location: Optional[str] = None
	start_year: Optional[int] = None
	end_year: Optional[int] = None
	description: Optional[str] = None


class Skill(BaseModel):
	id: Optional[int] = None
	name: str
	level: Optional[str] = None  # e.g., "beginner"|"intermediate"|"advanced"


class UserProfile(BaseModel):
	id: Optional[int] = None
	full_name: Optional[str] = None
	email: Optional[str] = None
	summary: Optional[str] = None
	educations: List[Education] = Field(default_factory=list)
	experiences: List[Experience] = Field(default_factory=list)
	skills: List[Skill] = Field(default_factory=list)

	def to_out(self) -> "ProfileOut":
		return ProfileOut(
			id=self.id,
			full_name=self.full_name,
			email=self.email,
			summary=self.summary,
			educations=[EducationOut(**e.dict()) for e in self.educations],
			experiences=[ExperienceOut(**e.dict()) for e in self.experiences],
			skills=[SkillOut(**s.dict()) for s in self.skills],
		)


class JobRequirement(BaseModel):
	id: Optional[int] = None
	job_id: Optional[int] = None
	kind: str  # "skill"|"experience"|"education"|"other"
	value: str
	difficulty: Optional[float] = None  # Rasch b parameter
	probability: Optional[float] = None
	evidence: Optional[float] = None


class Job(BaseModel):
	id: Optional[int] = None
	title: Optional[str] = None
	company: Optional[str] = None
	location: Optional[str] = None
	description: Optional[str] = None
	requirements: List[JobRequirement] = Field(default_factory=list)

	@staticmethod
	def from_struct(struct: Dict[str, Any]) -> "Job":
		reqs = [
			JobRequirement(kind=r["kind"], value=r["value"], difficulty=r.get("difficulty"))
			for r in struct.get("requirements", [])
		]
		return Job(
			title=struct.get("title"),
			company=struct.get("company"),
			location=struct.get("location"),
			description=struct.get("description"),
			requirements=reqs,
		)

	def to_out(self) -> "JobOut":
		return JobOut(
			id=self.id,
			title=self.title,
			company=self.company,
			location=self.location,
			description=self.description,
			requirements=[JobRequirementOut(**r.dict()) for r in self.requirements],
		)


class EducationOut(BaseModel):
	id: Optional[int] = None
	institution: Optional[str] = None
	degree: Optional[str] = None
	field_of_study: Optional[str] = None
	start_year: Optional[int] = None
	end_year: Optional[int] = None


class ExperienceOut(BaseModel):
	id: Optional[int] = None
	title: Optional[str] = None
	company: Optional[str] = None
	location: Optional[str] = None
	start_year: Optional[int] = None
	end_year: Optional[int] = None
	description: Optional[str] = None


class SkillOut(BaseModel):
	id: Optional[int] = None
	name: str
	level: Optional[str] = None


class ProfileOut(BaseModel):
	id: Optional[int] = None
	full_name: Optional[str] = None
	email: Optional[str] = None
	summary: Optional[str] = None
	educations: List[EducationOut] = Field(default_factory=list)
	experiences: List[ExperienceOut] = Field(default_factory=list)
	skills: List[SkillOut] = Field(default_factory=list)


class JobRequirementOut(BaseModel):
	id: Optional[int] = None
	job_id: Optional[int] = None
	kind: str
	value: str
	difficulty: Optional[float] = None
	probability: Optional[float] = None
	evidence: Optional[float] = None


class JobOut(BaseModel):
	id: Optional[int] = None
	title: Optional[str] = None
	company: Optional[str] = None
	location: Optional[str] = None
	description: Optional[str] = None
	requirements: List[JobRequirementOut] = Field(default_factory=list)


class RankedJob(BaseModel):
	job: JobOut
	score: float
	item_scores: List[Dict[str, Any]]


class SuggestionOut(BaseModel):
	profile: Optional[ProfileOut] = None
	recommendations: List[RankedJob] = Field(default_factory=list)
	explanation: Optional[str] = None


class ChatMessage(BaseModel):
	role: str  # "user"|"assistant"|"system"
	content: str


class ChatResponse(BaseModel):
	answer: str
	context_sources: List[Dict[str, Any]] = Field(default_factory=list)


