# Smart Culinary & Recipe Coach 👨‍🍳

An autonomous AI agent for home cooks that manages pantry inventory, searches tailored recipes, generates dish presentation images & videos, enforces allergy restrictions, and renders interactive UI cards.

![Smart Culinary Coach Demo](demo.gif)

---

## 🌟 Key Features & Capabilities

The following features are fully implemented in code (`app/` and `frontend/`):

- **Pantry Inventory Management (Firestore)**:
  - Query, add, update, and remove available ingredients in a Google Cloud Firestore database (`get_pantry_items`, `add_or_update_pantry_item`, `remove_pantry_item`).
- **Allergy & Dietary Memory Enforcement (Memory Bank)**:
  - Remembers and strictly enforces user food allergies (nuts, dairy, gluten, etc.) across chat sessions via ADK `PreloadMemoryTool` and `add_session_to_memory` callbacks.
- **Recipe Search (Internal & External Public API)**:
  - Searches an internal catalog (`search_recipes`) and fetches real-world online recipes from **TheMealDB** public REST API (`fetch_online_recipes`).
- **Generative Food Images (Imagen)**:
  - Generates high-resolution food presentation images using `gemini-3.1-flash-lite-image`, saving them as in-memory artifacts and uploading them to a public Google Cloud Storage bucket (`generate_dish_image`).
- **Short Dish Videos (Google Omni)**:
  - Generates 5-second food clips using `gemini-omni-flash-preview` via Google GenAI Interactions API (`generate_dish_video`), uploading bytes directly to Cloud Storage.
- **Python Code Execution Sandbox**:
  - Executes Python in a secure Agent Platform sandbox (`AgentEngineSandboxCodeExecutor`) for scaling recipe ingredient ratios and unit conversions.
- **Interactive A2UI Card Components**:
  - Generates structured UI card layouts (Cards, Columns, Rows, Text, Images) using `A2uiSchemaManager` (v0.8) and the `BasicCatalog`.
- **Custom Web Frontend & A2A Proxy**:
  - Includes a lightweight FastAPI A2A proxy (`frontend/main.py`) and a branded single-page chat interface (`frontend/static/index.html`) with clickable prompt suggestions and A2UI card rendering.

---

## 🛠️ Architecture & Tech Stack

- **Agent Framework**: Google Agent Development Kit (ADK) `Agent` & `App`
- **Generative AI Models**:
  - Reasoning: `gemini-flash-latest`
  - Image Generation: `gemini-3.1-flash-lite-image`
  - Video Generation: `gemini-omni-flash-preview`
- **Database & Storage**: Google Cloud Firestore & Google Cloud Storage
- **UI & Proxy**: FastAPI, `a2a-sdk`, HTML5/Vanilla CSS, A2UI Agent SDK (v0.8)
- **Deployment Targets**: Google Vertex AI Agent Runtime & Google Cloud Run

---

## 🚀 Local Setup & Development

### 1. Prerequisites & Environment Setup

Ensure Python 3.11+ and `uv` are installed. Clone the repository and install dependencies:

```bash
uv sync
```

Set required environment variables:

```bash
export GOOGLE_CLOUD_PROJECT="qwiklabs-gcp-03-7f83d2a066bb"
export GOOGLE_CLOUD_LOCATION="us-east1"
export GOOGLE_GENAI_USE_VERTEXAI=true
```

### 2. Run Local Agent Playground

Launch the interactive ADK agent playground for testing tools and prompts locally:

```bash
uv run adk web --port 18080 --allow_origins "*" --reload_agents
```

### 3. Run Frontend Server Locally

To run the custom FastAPI proxy and web chat interface locally:

```bash
cd frontend
pip install -r requirements.txt
AGENT_ENGINE_RESOURCE_NAME="<YOUR_AGENT_ENGINE_RESOURCE_NAME>" AGENT_DIRECTORY="app" python3 main.py
```

---

## 🚢 Deployment Instructions

### Deploy Agent to Agent Runtime

To deploy or update the agent on Vertex AI Agent Runtime:

```bash
agents-cli deploy --project $GOOGLE_CLOUD_PROJECT --region $GOOGLE_CLOUD_LOCATION --no-confirm-project
```

### Deploy Frontend to Cloud Run

To deploy the frontend proxy server to Cloud Run:

```bash
cd frontend
gcloud run deploy smart-culinary-coach-frontend \
  --source . \
  --project $GOOGLE_CLOUD_PROJECT \
  --region $GOOGLE_CLOUD_LOCATION \
  --set-env-vars AGENT_ENGINE_RESOURCE_NAME="<YOUR_AGENT_ENGINE_RESOURCE_NAME>",AGENT_DIRECTORY="app" \
  --allow-unauthenticated
```
