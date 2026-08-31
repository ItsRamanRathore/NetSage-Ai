# NetSage AI: Project Summary & Contribution

## About the Project
**NetSage AI** is an AI-assisted troubleshooting helper designed for Cisco-style lab networks (like Packet Tracer). Junior network engineers often know individual CLI commands but struggle to connect a symptom to the real root cause (e.g., VLAN, routing, DHCP, DNS, ACL, or NAT issues). 

NetSage AI bridges this gap by using a **Hybrid Diagnostic Approach**:
1. **Deterministic Rule Engine**: A Python-based strict regex engine (`checker.py`) that scans `show` command outputs for common config mistakes like mismatched gateways, missing NAT overloads, or administratively down interfaces.
2. **AI Prompt Library**: A structured LLM diagnostic engine (`engine.py`) that analyzes symptoms and outputs to return a strict JSON response containing the root cause, OSI layer, confidence, and exact fix steps.
3. **Human-in-the-Loop (HITL) Dashboard**: A Streamlit application (`app.py`) that presents the deterministic and AI results to an operator. The operator must explicitly **Approve**, **Edit**, or **Reject** the AI's proposed fix, which is then persisted to an audit log to ensure safe, responsible AI deployment.

## Tech Stack & System Architecture
- **Language**: Python 3.10+
- **User Interface**: Streamlit (for building the interactive Operations Dashboard)
- **Data Processing**: Pandas (for loading, querying, and displaying structured CSV case data)
- **Data Interchange**: JSON (for structured LLM inputs/outputs)
- **AI Integration**: Plug-and-play architecture using `google-genai`, `openai`, and `anthropic` SDKs, driven by a `system_config.json` file.
- **Target System**: Cisco IOS CLI / Packet Tracer

## Contribution
**Name:** [Insert Name Here]
**Role:** Full Stack Developer & AI Engineer

I developed the entirety of the NetSage AI project solo. My end-to-end contributions included:

### 1. Data & Prompt Engineering
- **Dataset Generation**: Curated the `data/cases.csv` dataset, generating 30 diverse troubleshooting scenarios spanning VLAN, DHCP, NAT, OSPF, ACL, and DNS issues with corresponding network concepts and severity.
- **Prompt Architecture**: Engineered the few-shot structured `diagnose_prompt.md` to force the LLM to output a precise JSON schema, preventing hallucinations in formatting and explicitly mapping CLI evidence to fix steps.

### 2. ML / AI Orchestration (`src/engine.py`)
- **Pipeline Architecture**: Designed the core orchestrator that merges the deterministic checker results with the AI prompt context.
- **Configurable Adapter**: Implemented a flexible adapter pattern to seamlessly switch between a Mock LLM and live APIs (Google Gemini, OpenAI, Anthropic) driven by the `system_config.json` configuration file.

### 3. Software Engineering & Deterministic Logic (`src/checker.py`)
- **Rule Engine Development**: Authored and optimized robust Python regex rules to dynamically catch common configuration anomalies (e.g., interface shutdown, VLAN trunking, IP conflicts, subnet mask errors, and gateway mismatches) across highly varied Cisco IOS command outputs.

### 4. Full Stack UI & Auditing (`src/app.py`)
- **Streamlit Application**: Built the interactive web dashboard that cleanly presents both deterministic and AI diagnostics side-by-side.
- **Human-in-the-Loop Safeguards**: Implemented the critical deployment decision gates (Approve/Edit/Reject) and the backend file I/O operations to persist these reviews to `data/review_log.jsonl`. 
- **Dashboard Analytics**: Developed the "Dashboard Summary" tab to visualize dataset composition and dynamically chart the live AI vs. Human Agreement Rate.

## Deliverables Completed
- `data/cases.csv` (30 test cases)
- `prompts/diagnose_prompt.md` (Structured prompt with few-shot examples)
- `src/checker.py` (Deterministic rules)
- `src/engine.py` (LLM integration)
- `src/app.py` (Streamlit HITL dashboard)
- `docs/model_audit_log.md` (Responsible AI logs and human corrections)
