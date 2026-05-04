# MahabharataOS

An AI-powered pipeline that converts raw, unstructured thoughts into publish ready LinkedIn posts without losing your voice.

> Named after the Mahabharata's principle of structured strategy 
> under chaos. Same logic. Applied to ideas.


## What It Does

Most AI tools generate content for you.
This system makes *you* generate better content faster, 
consistently, and in your own voice.

**Input:** A raw thought (text or voice note)  
**Output:** A structured, publish-ready LinkedIn post under 30 minutes


## How It Works
Raw Thought (Text / Voice)
↓
CEO Engine         → interprets intent, defines objective
↓
Delegation Engine  → breaks task into ordered steps
↓
Media Engine       → generates LinkedIn ready drafts
↓
Case Study Engine  → adds real world proof (where relevant)
↓
QA Layer           → removes generic AI tone, tightens voice
↓
Final Output       → ready to publish

Each stage is modular. The system can extend beyond content without rebuilding from scratch.

## Core Components

**CEO Engine** — decision layer
- Interprets user intent
- Classifies and prioritizes the task
- Defines the execution plan

**Delegation Engine** — workflow layer
- Breaks plan into discrete steps
- Routes them to the right module in order

**Media Engine** — content layer
- Transforms ideas into structured posts
- Preserves tone and voice
- Generates multiple draft options

**Case Study Engine** — credibility layer
- Detects when proof strengthens the argument
- Fetches relevant business examples
- Integrates them into the draft

**QA Layer** — quality layer
- Strips generic AI phrasing
- Improves readability
- Maintains authenticity


## Key Features

- Structured idea to output pipeline
- Modular, agent based architecture
- Human in the loop at every stage
- Campaign persistence via SQLite
- Observable execution via UI dashboard


## Tech Stack

| Layer    | Stack                          |
|----------|-------------------------------|
| Frontend | React / Next.js                |
| Backend  | Python, FastAPI, SQLAlchemy    |
| AI       | OpenAI / Claude APIs           |
| Database | SQLite → PostgreSQL (planned)  |


## Project Structure

frontend/   → UI dashboard and interaction layer
backend/    → engines, orchestration, AI integration, database


## Getting Started

**Prerequisites:** Node.js, Python 3.10+

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
npm run dev
```

## Current Status

Active focus:
- Thought → LinkedIn post pipeline
- Voice consistency across outputs
- Case study integration
- Sub 30 minute daily execution

Planned:
- Persistent memory (voice profile, recurring themes)
- Research and communication workflows
