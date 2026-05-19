from typing import List, Optional
from io import BytesIO
from dataclasses import dataclass
import re

from ..models import UserProfile, Education, Experience, Skill

try:
	import PyPDF2
except Exception:
	PyPDF2 = None

try:
	import spacy
	_nlp = None
except Exception:
	spacy = None
	_nlp = None


def _nlp_model():
	global _nlp
	if _nlp is not None:
		return _nlp
	if spacy is None:
		return None
	try:
		_nlp = spacy.load("en_core_web_sm")
	except Exception:
		_nlp = None
	return _nlp


def _extract_text_from_pdf(data: bytes) -> str:
	if PyPDF2 is None:
		return ""
	try:
		reader = PyPDF2.PdfReader(BytesIO(data))
		text = []
		for page in reader.pages:
			text.append(page.extract_text() or "")
		return "\n".join(text)
	except Exception:
		return ""


def _extract_text_from_docx(data: bytes) -> str:
	# Avoid python-docx dependency; prompt user to paste text or use PDF
	return ""


def _extract_text(data: bytes, filename: str, content_type: str) -> str:
	if content_type == "application/pdf" or (filename or "").lower().endswith(".pdf"):
		return _extract_text_from_pdf(data)
	if content_type in {
		"application/msword",
		"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
	}:
		return _extract_text_from_docx(data)
	# Plain text
	try:
		return data.decode("utf-8", errors="ignore")
	except Exception:
		return ""


def _extract_email(text: str) -> Optional[str]:
	m = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
	return m.group(0) if m else None


def _extract_name(text: str) -> Optional[str]:
	lines = [l.strip() for l in text.splitlines() if l.strip()]
	if not lines:
		return None
	# Heuristic: first line is name if it looks like two words with capitalization
	first = lines[0]
	if len(first.split()) <= 5 and re.match(r"^[A-Z][A-Za-z\-'`]+( [A-Z][A-Za-z\-'`]+)+$", first):
		return first
	# Fallback: None
	return None


def _extract_sections(text: str) -> dict:
	sections = {"education": "", "experience": "", "skills": "", "summary": ""}
	lower = text.lower()
	# naive section splits
	edu_idx = lower.find("education")
	exp_idx = lower.find("experience")
	skills_idx = lower.find("skills")
	summary_idx = lower.find("summary")
	sorted_idx = sorted([("education", edu_idx), ("experience", exp_idx), ("skills", skills_idx), ("summary", summary_idx)], key=lambda x: (x[1] if x[1] != -1 else 10**9))
	sorted_idx = [i for i in sorted_idx if i[1] != -1]
	if not sorted_idx:
		sections["summary"] = text.strip()
		return sections
	for i, (name, idx) in enumerate(sorted_idx):
		end = sorted_idx[i + 1][1] if i + 1 < len(sorted_idx) else len(text)
		sections[name] = text[idx:end].strip()
	return sections


def _parse_education(section: str) -> List[Education]:
	items: List[Education] = []
	for line in section.splitlines():
		line = line.strip(" -•\t")
		if not line or "education" in line.lower():
			continue
		year_m = re.findall(r"(19|20)\d{2}", line)
		inst_m = re.split(r",|-|\|", line)
		institution = inst_m[0].strip() if inst_m else None
		degree = None
		field = None
		if re.search(r"\b(B\.?S\.?|BSc|Bachelor|M\.?S\.?|MSc|Master|PhD|Doctor)\b", line, flags=re.I):
			degree = re.search(r"(B\.?S\.?|BSc|Bachelor|M\.?S\.?|MSc|Master|PhD|Doctor)", line, flags=re.I).group(0)
		if re.search(r"in [A-Za-z &/]+", line):
			field = re.search(r"in ([A-Za-z &/]+)", line).group(1)
		start, end = None, None
		if year_m:
			if len(year_m) >= 2:
				start, end = int(year_m[0]), int(year_m[1])
			elif len(year_m) == 1:
				end = int(year_m[0])
		items.append(Education(institution=institution or None, degree=degree, field_of_study=field, start_year=start, end_year=end))
	return items


def _parse_experience(section: str) -> List[Experience]:
	items: List[Experience] = []
	for line in section.splitlines():
		line = line.strip(" -•\t")
		if not line or "experience" in line.lower():
			continue
		year_m = re.findall(r"(19|20)\d{2}", line)
		title = None
		company = None
		parts = re.split(r" at | @ |,|-|\|", line)
		if parts:
			title = parts[0].strip()
			if len(parts) >= 2:
				company = parts[1].strip()
		start, end = None, None
		if year_m:
			if len(year_m) >= 2:
				start, end = int(year_m[0]), int(year_m[1])
			elif len(year_m) == 1:
				end = int(year_m[0])
		items.append(Experience(title=title, company=company, start_year=start, end_year=end, description=None))
	return items


def _parse_skills(section: str) -> List[Skill]:
	items: List[Skill] = []
	if not section:
		return items
	# find the line after 'skills'
	lines = [l for l in section.splitlines() if l.strip()]
	if not lines:
		return items
	body = []
	for l in lines:
		if "skills" in l.lower():
			continue
		body.append(l)
	text = " ".join(body)
	candidates = re.split(r"[,\n;•|]", text)
	for c in candidates:
		name = c.strip()
		if not name:
			continue
		if len(name) > 64:
			continue
		items.append(Skill(name=name))
	return items


def parse_resume_file(data: bytes, filename: str, content_type: str) -> UserProfile:
	text = _extract_text(data, filename, content_type)
	name = _extract_name(text)
	email = _extract_email(text)
	sections = _extract_sections(text)
	educations = _parse_education(sections.get("education", ""))
	experiences = _parse_experience(sections.get("experience", ""))
	skills = _parse_skills(sections.get("skills", ""))
	summary = sections.get("summary", "").strip()
	return UserProfile(
		full_name=name,
		email=email,
		summary=summary if summary else None,
		educations=educations,
		experiences=experiences,
		skills=skills,
	)


