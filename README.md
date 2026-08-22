# InkDex-server
InkDex - index your documents and make their knowledge searchable.

InkDex is a FastAPI-based backend server for RAG (Retrieval-Augmented Generation) document management. It allows users to upload PDF documents, automatically chunks and indexes them using a SentenceTransformer model (`all-MiniLM-L6-v2`), stores vector embeddings using `pgvector` in PostgreSQL, and answers user questions contextually using the Gemini 3.5 Flash model.

---

## Prerequisites

Before starting, ensure you have the following installed on your system:
* **Python 3.10+**
* **PostgreSQL** (version 12+ recommended)
* **Redis Server** (required for background queue tasks)

---

## Database Configuration (pgvector & Indexing)

InkDex uses `pgvector` for storing and performing high-performance similarity searches on document content embeddings.

### 1. Install pgvector Extension
To use vector embeddings in your database, you must install the `pgvector` extension on your PostgreSQL server.

* **macOS (via Homebrew):**
  ```bash
  brew install pgvector
  ```
* **Linux (Debian/Ubuntu):**
  ```bash
  sudo apt-get install postgresql-server-dev-all
  git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
  cd pgvector
  make
  make install # may need sudo
  ```
* **Windows / Docker:**
  If you are running PostgreSQL inside Docker, use the official pgvector image:
  ```bash
  docker run --name inkdex-db -e POSTGRES_DB=inkdex -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d pgvector/pgvector:pg16
  ```

### 2. Enable Extension in pgAdmin/PostgreSQL
Open **pgAdmin** (or your preferred SQL client), connect to your database, open the Query Tool, and execute the following SQL statement:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

---

## Getting Started


### 1. Clone & Set Up Virtual Environment
```bash
git clone <repository-url>
cd inkdex
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the root of the project directory and fill in your keys:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/inkdex_db
REDIS_URL=redis://localhost:6379/0

# JWT Authentication Config
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

# Cloudinary Credentials
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Gemini LLM Config
GEMINI_API_KEY=your_gemini_api_key
```

> [!IMPORTANT]
> **Cloudinary Security Setting Configuration (Mandatory)**: 
> Because PDFs are uploaded as `image` resource types to support direct inline viewing/embedding on the frontend, Cloudinary's default security rules will block their delivery. 
> To enable public delivery:
> 1. Log in to your Cloudinary Console.
> 2. Go to **Settings -> Security**.
> 3. Scroll down to **Restricted media type delivery** (or **PDF and ZIP files delivery**).
> 4. Check **"Allow delivery of PDF and ZIP files"** and click **Save**.


### 4. Run Database Migrations
Use Alembic to create tables and set up the schema:
```bash
alembic upgrade head
```

### 5. Create HNSW Vector Index (For Production)
Once the tables are created by migrations, you can add an HNSW index on the `document_chunks` table's `embedding` column for fast cosine-similarity search results under high document volumes.

Run this SQL script in pgAdmin / Query Tool:

```sql
-- Create an HNSW index using Cosine Distance
CREATE INDEX IF NOT EXISTS ndx_document_chunks_embedding_cosine 
ON document_chunks 
USING hnsw (embedding vector_cosine_ops);
```

---


## Running the Application

This application requires running both the FastAPI web server and the background RQ queue worker.

### Start the FastAPI Dev Server
```bash
fastapi dev main.py
```
Your API docs will be available at `http://127.0.0.1:8000/docs`.

### Start the Background Worker (In a separate terminal)
Make sure Redis is running, then start the background worker queue:
```bash
OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES PYTHONPATH=. rq worker documents
```
*(The worker handles downloading PDFs, text extraction, chunking, and generation of sentence embeddings asynchronously.)*
