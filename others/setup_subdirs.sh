#!/bin/bash

# Create top-level data folder for datasets, docs, etc.
mkdir -p data

# Core domain folders
mkdir -p ontology/src
mkdir -p kg/neo4j
mkdir -p ingestion
mkdir -p validation
mkdir -p notebooks
mkdir -p docs
mkdir -p tests

# FastAPI interface
touch main.py

# Unified FastAPI app folders with submodules for UI
mkdir -p webapp/ontology
mkdir -p webapp/kg
mkdir -p webapp/nlp_rag

# Templates and static assets for the webapp
mkdir -p webapp/templates/ontology
mkdir -p webapp/templates/kg
mkdir -p webapp/templates/nlp_rag
mkdir -p webapp/static/css
mkdir -p webapp/static/js

# Create placeholder Python files for each module backend
touch ingestion/haz_ingest.py
touch validation/rules.py
touch webapp/app.py
touch webapp/ontology/routes.py
touch webapp/kg/routes.py
touch webapp/nlp_rag/routes.py

# Create placeholder HTML template files
touch webapp/templates/index.html
touch webapp/templates/ontology/index.html
touch webapp/templates/kg/index.html
touch webapp/templates/nlp_rag/index.html

# Create README
touch README.md
