# Gemini Enterprise Agent Automation

## Objective

This project automates the migration of agent configurations from a central CSV file to Gemini Enterprise Low-Code Agents.

The automation uses Python and Playwright to interact with the Gemini Enterprise web interface.

## Migration Flow

Gem configuration
        ↓
Central CSV
        ↓
CSV Reader
        ↓
Playwright
        ↓
Gemini Enterprise
        ↓
Low-Code Agent
        ↓
Verification

## CSV Structure

The expected CSV contains:

- Sl No.
- Gem Name
- Description
- Instructions

Each CSV row represents one agent.

## Project Structure

```text
gemini_agent_automation/
│
├── artifacts/
├── data/
├── logs/
├── output/
├── src/
│
├── main.py
├── .env
├── .env.example
├── requirements.txt
└── README.md