# GuardPrompt

**Real-time prompt injection detection middleware for LLM-based applications.**

GuardPrompt sits between your users and your AI model. Every prompt gets analyzed before it reaches your LLM. Attacks get blocked. Clean prompts pass through. Your AI stays safe.

---

## The Problem

Companies building on top of LLMs face a growing attack surface that most security tools do not cover.

Users can manipulate AI assistants through carefully crafted prompts — overriding instructions, extracting system configuration, jailbreaking safety filters, or hiding attacks inside documents. These are not hypothetical threats. They are happening in production systems today.

Standard firewalls and WAFs do not understand natural language. They cannot detect these attacks.

---

## What GuardPrompt Does

GuardPrompt acts as a security proxy layer. Every user prompt passes through a three-layer detection engine before reaching your LLM API.

**What it detects:**
- Direct prompt injection — attempts to override or replace AI instructions
- Jailbreak attempts — requests to operate without safety guidelines
- Role manipulation — trying to redefine the AI as an unrestricted entity
- Data exfiltration — attempts to extract system prompts or internal configuration
- Indirect injection — attacks hidden inside documents, files, or external content
- Encoding evasion — attacks disguised using base64, hex, or other encoding

**What it returns:**
- A decision: `block`, `flag`, or `pass`
- A risk score from 0 to 100
- The detection reason
- Which detection layer caught it

---

## How Detection Works

GuardPrompt uses three independent detection layers that work together:

**Layer 1 — Rule-Based**
Pattern matching against a continuously updated ruleset of known attack signatures. Runs in under 5 milliseconds. No external calls.

**Layer 2 — Semantic AI**
A locally-running language model analyzes the intent behind the prompt. Catches novel attacks that have no known pattern — clever rephrasing, hypothetical framing, creative writing tricks.

**Layer 3 — Heuristic Analysis**
Structural checks on the prompt itself — unusual length, encoded content, language switching, character anomalies, and repetition patterns that indicate manipulation attempts.

All three layers run on every request. The final score is the highest signal across all layers. If any layer detects a high-confidence threat, the request is blocked immediately.

---

## Key Properties

**No data leaves the machine.**
The semantic detection layer runs on a local AI model via Ollama. Your users' prompts are never sent to any external API for analysis.

**Raw prompts are never stored.**
GuardPrompt logs the detection result, score, and reason — not the original prompt. A one-way hash is stored for deduplication purposes only.

**Designed to be fast.**
Rule-based detection completes in milliseconds. If Layer 1 catches a high-confidence attack, the other layers are skipped entirely to minimize latency.

**Dashboard included.**
A real-time web dashboard shows all analysis logs, block and flag counts, average risk scores, and detection patterns over time.

---

## Tech Stack

- **Backend:** Python, FastAPI
- **Detection AI:** Mistral 7B via Ollama (runs fully local)
- **Database:** SQLite
- **Frontend:** React, Vite
- **Platform:** Linux (Ubuntu 22.04), WSL2 compatible

---

## Use Cases

- Startups and companies building AI assistants or chatbots on top of LLM APIs
- Enterprises deploying internal AI tools where prompt confidentiality matters
- Developers who want a security layer between user input and their AI backend
- Any product where users interact directly with an AI model

---

## Status

GuardPrompt is currently in active development. The core detection engine, REST API, database logging, and dashboard are fully functional.

Upcoming: authentication and role-based access control, HTTPS support, and deployment packaging.

---

## Author

Built by Kaif — ByteFortix Security  
[github.com/kaifhoda1](https://github.com/kaifhoda1)

---

*GuardPrompt is a closed-source commercial product. This repository contains the public-facing project overview only.*
