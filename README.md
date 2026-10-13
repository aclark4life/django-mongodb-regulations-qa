# Regulations QA

A Django application that ingests Federal Register regulatory documents
(e.g., EPA rules), auto-embeds them, and enables semantic Q&A search over them using [MongoDB Atlas Vector Search](https://www.mongodb.com/products/platform/atlas-vector-search).

Documents are stored as plain text, MongoDB Atlas automatically generates and manages the embeddings for the `abstract` field via Atlas vector search index's built-in embedding model, so there's no separate embedding service or API call to maintain.

## Requirements

- Python 3.13+
- A MongoDB Atlas cluster with an
  [auto-embedding (automated embedding) vector search index](https://www.mongodb.com/docs/vector-search/crud-embeddings/automated-embedding/)
  configured on the `abstract` field of the `documents_document` collection.

## Setup

1. Clone the repo and create a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with the following variables:

   ```bash
   SECRET_KEY=your-django-secret-key
   MONGODB_URI="mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?appName=documents"
   DB_NAME=your-database-name
   VECTOR_INDEX_NAME=your-vector-index-name
   ```

4. Apply migrations:

   ```bash
   python manage.py migrate
   ```

## Usage

### Ingest documents

Fetch regulatory documents from the Federal Register API and save them to MongoDB:

```bash
python manage.py ingest_federal_register --agency environmental-protection-agency --limit 100
```

- `--agency`: Federal Register agency slug (default: `environmental-protection-agency`)
- `--limit`: maximum number of documents to save

No embedding step is required here because once documents land in the collection, MongoDB Atlas's vector search index auto-embeds the `abstract` field in the background.

### Search documents

Run a plain-text semantic search over the ingested documents:

```bash
python manage.py search_docs "What are the emissions standards for diesel engines?"
```

The question text is passed directly to `$vectorSearch` — MongoDB auto-embeds the query using the index, so no query vector or external embedding call is needed. Results are ranked by vector search score and show the document number and title.

## Project structure

- [documents/models.py](documents/models.py) — the `Document` model
- [documents/services/search_service.py](documents/services/search_service.py) — MongoDB vector search query logic
- [documents/management/commands/](documents/management/commands) — `ingest_federal_register` and `search_docs` commands
- [regulations_qa/](regulations_qa) — Django project settings and configuration
- [mongo_migrations/](mongo_migrations) — Mongo-backed migrations for Django's built-in apps

NB: The Data used comes from the Federal Register, which publishes US government documents. This project is independent and not affiliated with or endorsed by the Federal Register.

