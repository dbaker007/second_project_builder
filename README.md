# The Sentinel Ecosystem: Agentic Software Engineering

A two-project symphony designed to transform "English Intent" into "Verified Code." This ecosystem moves beyond simple code generation, providing a structured architecture for the AI-Centric development age.

---

## 1. Project Manager (The Architect)
**Status:** In Development (Phase 2: Persistence)  
**Role:** Intent Refinement & Context Management  

The Project Manager is an NLI-driven (Natural Language Interface) assistant that acts as the "Frontend for Intent." It solves the "Information Gap" by helping the user bridge the distance between a vague idea and a technically sound requirement.

### Key Responsibilities:
*   **Contextual Awareness**: Maintains a persistent SQLite database of tracked repositories and their specific technical footprints.
*   **Requirement Refinement**: Collaborates with the user to transform plain English into "Builder-ready" `requirements.md` files.
*   **GitHub Integration**: Manages secure credentials and fetches real-time repository data (READMEs, file trees) to ground the AI's reasoning.
*   **Hand-off**: Triggers the Builder by committing finalized requirements to the target repository.

---

## 2. The Builder (The Engineer)
**Status:** Operational / Core Engine Complete  
**Role:** Autonomous Execution & Verification  

The Builder is the high-autonomy "Execution Engine." It is a headless agentic loop that monitors for requirement changes and manages the heavy lifting of implementation, testing, and deployment.

### Key Responsibilities:
*   **Autonomous Planning**: Uses reasoning models (DeepSeek-R1 / Qwen-30B) to derive architectural plans from requirement deltas.
*   **Self-Correcting Loop**: Employs a Coder/QA feedback cycle to detect and repair bugs (such as import hallucinations or syntax errors) before human review.
*   **Stall Detection**: Features an intelligent MD5-based "Stall Detector" that monitors error signatures. It ensures the agent persists through productive struggle but terminates during logic loops to save compute.
*   **Layman-Ready Output**: Automatically generates professional `src/` layouts and `pyproject.toml` configurations, ensuring the final product "just works" for the end user via `uv`.

---

## 🛠️ The Technology Stack
*   **Orchestration:** LangGraph (State Management)
*   **Reasoning:** qwen3-coder:30b-a3b-q4_k_m (Local via Ollama)
*   **Execution:** Aider-Chat (Surgical Code Edits)
*   **Environment:** Python 3.12+ / uv (Package Management)
*   **Persistence:** SQLite3

---

## 🧠 Strategic Narrative
This ecosystem demonstrates a shift from **Programmer-Centric** to **AI-Centric** engineering. By decoupling **Strategy (Project Manager)** from **Execution (The Builder)**, I have created a scalable workflow where human oversight is focused on high-level architectural intent, while the AI handles the commoditized details of implementation and verification.

# Sentinel Healer (V2)

Sentinel Healer is an autonomous, repository-agnostic maintenance agent. It operates as a persistent daemon that monitors a project's `requirements.md` and implements features using a Test-Driven Development (TDD) cycle.



## 🛠️ Technical Stack
- **Language**: Python 3.12+
- **Orchestration**: LangGraph
- **Package Manager**: uv
- **Test Runner**: pytest (Mock-centric)
- **Primary LLMs**: 
    - qwen3-coder:30b-a3b-q4_k_m

## 🧠 Agent Context (LTM)
<!-- AGENT_CONTEXT_START -->
- **Status**: Initialization Phase
- **Mode**: TDD Contract-First
- **Infrastructure**: Immutable main.py heartbeat and NodeFactory dependency injection.
<!-- AGENT_CONTEXT_END -->

---
*Note: This README is automatically updated by the Sentinel Healer agent. Do not remove the AGENT_CONTEXT blocks.*

