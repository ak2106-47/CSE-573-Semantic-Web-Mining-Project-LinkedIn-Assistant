# Evaluation: Metrics, Experiments, Preliminary Findings

## 1. Method Comparison Table

| Method              | Speed           | Explainability        | Approx NDCG | Use Case               | Diversity |
| ------------------- | --------------- | --------------------- | ----------- | ---------------------- | --------- |
| **RapidFuzz Fuzzy** | Fast (~50ms)    | Low (Keyword)         | ~0.58       | Initial filtering      | Low       |
| **TF-IDF**          | Medium (~200ms) | Medium (term weights) | ~0.62       | Baseline lexical match | Low       |
| **Sentence BERT**   | Slow (~2s)      | Medium (embeddings)   | ~0.74       | Semantic search        | Medium    |
| **Rasch Scoring**   | Fast (~100ms)   | High (P, b, θ)        | ~0.78\*     | Final explainable      | High      |

> Rasch provides best accuracy and transparency, offering actionable insights for users.

---

## 2. System Performance Metrics

| Metric                | Value        | Notes                         |
| --------------------- | ------------ | ----------------------------- |
| Dataset Size          | 31,597 jobs  | LinkedIn public dataset       |
| Resume Parsing Time   | ~2-3 seconds | PDF/DOCX → structured profile |
| Search Latency        | ~50ms        | RapidFuzz on 31K jobs         |
| Rasch Scoring Time    | ~100ms       | 100 jobs, 4 requirements each |
| Graph Load Time       | ~30 seconds  | 100 jobs → Neo4j              |
| Chatbot Response Time | ~1-2 seconds | Template-based responses      |

---

## 3. Explainability Metrics

| Metric                       | Value         | How Measured                     |
| ---------------------------- | ------------- | -------------------------------- |
| Probability range (P values) | 0.34 - 0.74   | Shows variance in matching       |
| Difficulty range (b values)  | -0.30 to 0.65 | From Entry to Senior level roles |
| Transparency score           | High          | Users see P, b, θ values         |
| Avg. requirements per job    | 3.8           | Skill + Experience + Industry    |

---

## 4. Key Takeaways

- Rasch scoring provides transparent, explainable matching (see P, b, θ).
- System processes large-scale, real-world LinkedIn data efficiently.
- Knowledge graph (Neo4j) enables semantic, visual exploration.
- All major components (retrieval, explainability, graph viz) are implemented and tested.

---
