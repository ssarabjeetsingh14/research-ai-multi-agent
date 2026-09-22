# 🔎 AI Multi-Agent Research System

An AI-powered multi-agent research system that automatically searches the web, analyzes information, generates a research report, and reviews the generated content using specialized AI agents.

The application provides a user-friendly **Streamlit interface** and uses LLMs, web-search tools, and agentic workflows to automate research.


## 📌 Project Overview

Researching a topic manually often requires searching multiple websites, reading different sources, extracting important information, and organizing the findings.

This project automates that workflow using multiple specialized AI agents.

### Workflow

```text
                👤 User
                  │
                  ▼
          📝 Research Topic
                  │
                  ▼
        ┌───────────────────┐
        │   Search Agent    │
        │                   │
        │ Searches the web  │
        └─────────┬─────────┘
                  │
                  ▼
        ┌───────────────────┐
        │   Reader Agent    │
        │                   │
        │ Analyzes sources  │
        └─────────┬─────────┘
                  │
                  ▼
        ┌───────────────────┐
        │   Writer Agent    │
        │                   │
        │ Creates report    │
        └─────────┬─────────┘
                  │
                  ▼
        ┌───────────────────┐
        │   Critic Agent    │
        │                   │
        │ Reviews content   │
        └─────────┬─────────┘
                  │
                  ▼
          📊 Final Research
               Report
