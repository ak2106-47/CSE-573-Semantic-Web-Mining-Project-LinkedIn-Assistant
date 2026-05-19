from typing import Optional, List, Dict, Any

try:
	from neo4j import GraphDatabase
except Exception:
	GraphDatabase = None


class KnowledgeGraph:
	def __init__(self, uri: Optional[str] = None, user: Optional[str] = None, password: Optional[str] = None):
		self.available = GraphDatabase is not None and uri and user and password
		self._driver = GraphDatabase.driver(uri, auth=(user, password)) if self.available else None

	def close(self) -> None:
		if self._driver:
			self._driver.close()

	def upsert_skill(self, name: str) -> None:
		if not self._driver:
			return
		with self._driver.session() as session:
			session.run("MERGE (:Skill {name: $name})", name=name)

	def upsert_role(self, name: str) -> None:
		if not self._driver:
			return
		with self._driver.session() as session:
			session.run("MERGE (:Role {name: $name})", name=name)

	def relate_skill_role(self, skill: str, role: str, weight: float = 1.0) -> None:
		if not self._driver:
			return
		with self._driver.session() as session:
			session.run("""
				MERGE (s:Skill {name: $skill})
				MERGE (r:Role {name: $role})
				MERGE (s)-[e:REQUIRES]->(r)
				SET e.weight = coalesce(e.weight, 0) + $weight
			""", skill=skill, role=role, weight=weight)

	def paths_skill_to_role(self, skill: str, role: str, k: int = 3) -> List[Dict[str, Any]]:
		if not self._driver:
			return []
		with self._driver.session() as session:
			result = session.run("""
				MATCH p = shortestPath((:Skill {name: $skill})-[:REQUIRES*..4]->(:Role {name: $role}))
				RETURN p LIMIT $k
			""", skill=skill, role=role, k=k)
			paths = []
			for rec in result:
				paths.append({"path": str(rec["p"])})
			return paths


