# CureVox — Hackathon Ready Demo

## Overview
CureVox is an AI-first triage demo: live cough analysis, rash photo check, and conversational symptom advice.
This repo contains a polished frontend (static HTML + JS) and a unified Flask backend with lightweight ML fallbacks.

## Quick start (local)
1. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
