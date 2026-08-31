# AKGG: An LLM-Driven Adaptive Knowledge Graph Game Framework for Personalized E-Learning

AKGG is an adaptive e-learning framework that combines:

- Large Language Models (LLMs)
- Knowledge Graphs
- Semantic Web technologies
- Learner modeling
- Adaptive quest generation
- Gamified learning
- Explainable rule-based adaptation

The framework represents educational domain knowledge and learner state explicitly and uses prerequisite relationships, learner mastery, misconceptions, concept difficulty, and graph structure to determine which learning activity should be presented next.

This repository accompanies the manuscript:

> **AKGG: An LLM-Driven Adaptive Knowledge Graph Game Framework for Personalized E-Learning**

---

## Overview

AKGG integrates generative AI with an explicit semantic adaptation layer.

The overall learning cycle is:

1. Generate a domain knowledge graph using an LLM.
2. Represent educational concepts and prerequisite relations.
3. Maintain learner mastery for each concept.
4. Identify knowledge gaps.
5. Rank candidate concepts using an explicit priority function.
6. Apply prerequisite gating to determine which concepts are currently eligible.
7. Generate an adaptive RPG-style learning quest.
8. Evaluate the learner response.
9. Update mastery and misconception information.
10. Repeat the adaptation cycle.

A central design goal is to keep the adaptation decision inspectable rather than delegating the entire recommendation process to an opaque generative model.

---

## Repository Contents

The repository contains supplementary material supporting the implementation and analyses reported in the manuscript.

### Semantic Web Resources

- `akgg_ontology.ttl`  
  OWL/RDF ontology defining the principal AKGG semantic entities and properties.

- `sparql_gap_query.rq`  
  SPARQL query used to retrieve learner knowledge gaps ordered by priority.

- `example_domain_learner_graph.ttl`  
  Example Turtle representation illustrating domain concepts, prerequisite relationships, and learner state.

---

## LLM Prompt Templates

The repository includes the prompt templates used by the prototype for:

- domain knowledge graph generation;
- adaptive quest generation;
- learner-response assessment and misconception detection.

Example files may include:

```text
llm_prompt_domain_graph_generation.txt
llm_prompt_quest_generation.txt
llm_prompt_misconception_detection.txt
