# Agent MVP - Deployment Guide

## Overview

This is an AI Agent MVP built with FastAPI and deployed on Google Cloud Platform (GCP) using Cloud Run. The agent is powered by Claude (Anthropic) and includes a CI/CD pipeline through GitHub Actions.

---

## Deployment Steps

### 1. GCP Project Setup

**What it does:** Creates and configures your Google Cloud environment where your application will run.

**Why it's important:** GCP needs a project container to organize all your resources (compute, storage, networking). Without this, you can't deploy anything.

**Steps:**

```bash
# Set your project ID
gcloud config set project YOUR_PROJECT_ID

# Set your preferred region (e.g., europe-west2 for London)
gcloud config set run/region YOUR_REGION
```

**Role:** Establishes the foundation - like setting up a workspace before building something. Everything else depends on having this configured correctly.

---

### 2. Enable Required APIs

**What it does:** Activates specific Google Cloud services that your application needs to function.

**Why it's important:** GCP services are modular and disabled by default for security and cost control. You must explicitly enable what you need.

**APIs to enable:**

- **Cloud Run API**: Runs your containerized application
- **Cloud Build API**: Builds your Docker images automatically
- **Artifact Registry API**: Stores your Docker images
- **Storage API**: Handles build artifacts and logs

**Steps:**
Go to GCP Console → APIs & Services → Enable APIs and Services → Search and enable each API

**Role:** Like turning on utilities in a building - you need electricity (Cloud Run), plumbing (networking), and storage before you can operate.

---

### 3. Create Service Account for GitHub Actions

**What it does:** Creates a special identity that GitHub Actions can use to deploy to GCP on your behalf.

**Why it's important:** GitHub needs permission to access your GCP project. A service account provides secure, limited access without sharing your personal credentials.

**Steps:**

1. Go to IAM & Admin → Service Accounts
2. Create service account named `github-actions-deployer`
3. Grant roles:
   - **Cloud Run Admin**: Deploy and manage Cloud Run services
   - **Service Account User**: Act as other service accounts
   - **Artifact Registry Writer**: Push Docker images
   - **Storage Admin**: Manage build artifacts
4. Create and download JSON key

**Role:** This is your security guard that lets GitHub Actions into your GCP project with specific, limited permissions. It's the bridge between GitHub and GCP.

---

### 4. Create Artifact Registry Repository

**What it does:** Creates a storage location for your Docker container images.

**Why it's important:** Cloud Run deploys containers, not raw code. You need a place to store these container images that GCP can access.

**Steps:**

```bash
gcloud artifacts repositories create agent-mvp \
    --repository-format=docker \
    --location=YOUR_REGION \
    --description="Docker repository for agent MVP"
```

**Role:** Think of it as a private warehouse where all versions of your packaged application are stored. Each deployment pulls the latest version from here.

---

### 5. Configure GitHub Repository

**What it does:** Sets up your code repository with deployment automation.

**Why it's important:** This creates the CI/CD pipeline that automatically builds and deploys your code when you push changes.

**Steps:**

1. Create GitHub repository
2. Add the service account JSON as a secret:
   - Go to Settings → Secrets and Variables → Actions
   - Create secret named `GCP_SA_KEY`
   - Paste entire JSON file contents
3. Update `deploy.yml` with your project ID and region

**Role:** This is your automation hub. Every time you commit code, GitHub Actions automatically packages, tests, and deploys it to production.

---

### 6. Deploy to Cloud Run

**What it does:** Takes your Docker container and runs it as a scalable web service.

**Why it's important:** Cloud Run is the actual compute platform that runs your application and makes it accessible via HTTPS.

**How it works:** GitHub Actions automatically:

1. Builds a Docker image from your code
2. Pushes the image to Artifact Registry
3. Deploys the image to Cloud Run
4. Provides you with a public HTTPS URL

**Steps:**

```bash
# Push code to trigger deployment
git add .
git commit -m "Deploy agent MVP"
git push origin main
```

**Role:** This is where your application comes alive. Cloud Run handles scaling, HTTPS certificates, and makes your agent accessible to the world.

---

### 7. Configure Authentication & Environment Variables

**What it does:** Secures your service and adds necessary API keys.

**Why it's important:** Protects your agent from unauthorized access and provides it with credentials to call external services (like Claude API).

**Steps:**

```bash
# Add API key for Claude
gcloud run services update agent-mvp \
    --region=YOUR_REGION \
    --set-env-vars="ANTHROPIC_API_KEY=your-key-here"

# For authenticated access (recommended for MVP)
# Service is already secured by default - only authenticated users can access

# For public access (if needed later)
gcloud run services add-iam-policy-binding agent-mvp \
    --region=YOUR_REGION \
    --member="allUsers" \
    --role="roles/run.invoker"
```

**Role:** This is your security layer and configuration management. It keeps your agent private and gives it the keys it needs to function.

---

## File Structure

```
agent-mvp/
├── .github/
│   └── workflows/
│       └── deploy.yml          # CI/CD pipeline configuration
├── app/
│   ├── __init__.py            # Makes app/ a Python package
│   ├── main.py                # FastAPI application entry point
│   └── agent.py               # Agent logic with LLM integration
├── Dockerfile                  # Container build instructions
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## File Descriptions

### `.github/workflows/deploy.yml`

**Type:** YAML configuration file  
**Purpose:** Defines the CI/CD pipeline for GitHub Actions

**What it does:**

- Triggers automatically when you push to the `main` branch
- Authenticates with GCP using your service account
- Builds a Docker image from your code
- Pushes the image to Artifact Registry
- Deploys the image to Cloud Run
- Outputs the service URL

**Why we need it:** Automates the entire deployment process. Without this, you'd have to manually build, push, and deploy every time you make a change.

**Key sections:**

- `on: push`: Defines when the workflow runs
- `env`: Sets environment variables (project ID, region, service name)
- `steps`: Sequential actions to build and deploy

---

### `app/__init__.py`

**Type:** Python package initializer  
**Purpose:** Makes the `app/` directory a Python package

**What it does:** Tells Python that this directory contains modules that can be imported.

**Why we need it:** Without this file, Python won't recognize `app/` as a package, and imports like `from app.main import app` will fail. It's a Python convention required for proper module structure.

---

### `app/main.py`

**Type:** Python application file  
**Purpose:** FastAPI application definition and HTTP endpoints

**What it does:**

- Creates the FastAPI application instance
- Defines HTTP endpoints (routes):
  - `GET /`: Welcome message
  - `GET /health`: Health check endpoint
  - `POST /agent/process`: Main agent endpoint that processes messages
- Initializes the agent
- Handles request/response models with Pydantic
- Runs the Uvicorn server

**Why we need it:** This is the entry point of your web application. It defines what URLs are available and what happens when someone calls them. Without this, you'd have no web interface.

**Key components:**

```python
app = FastAPI()  # Creates the web application
agent = SimpleAgent()  # Initializes your AI agent

@app.post("/agent/process")  # Defines an endpoint
async def process_message(request: AgentRequest):
    # Handles incoming requests
```

---

### `app/agent.py`

**Type:** Python module  
**Purpose:** Contains the AI agent logic and LLM integration

**What it does:**

- Defines the `SimpleAgent` class
- Integrates with Claude API (Anthropic)
- Processes user messages and generates AI responses
- Handles API authentication and error cases
- Provides structure for future enhancements (tools, memory)

**Why we need it:** This separates your business logic (the agent) from your web framework (FastAPI). This makes your code:

- Easier to test
- More maintainable
- Reusable in other contexts

**Key components:**

```python
class SimpleAgent:
    def __init__(self):
        # Initialize Claude API client
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    async def process(self, message: str, context: Optional[Dict] = None):
        # Call Claude API and return response
        response = self.client.messages.create(...)
        return response.content[0].text
```

---

### `Dockerfile`

**Type:** Docker configuration file  
**Purpose:** Instructions for building a container image

**What it does:**

- Starts from a base Python 3.11 image
- Copies your code into the container
- Installs Python dependencies
- Configures the runtime environment
- Defines the command to start your application

**Why we need it:** Cloud Run runs containers, not raw Python code. This file tells Docker how to package your application into a self-contained, runnable unit. Think of it as a recipe for creating a virtual machine that runs your app.

**Key sections:**

```dockerfile
FROM python:3.11-slim           # Base operating system
COPY requirements.txt .         # Copy dependency list
RUN pip install -r requirements.txt  # Install dependencies
COPY app/ ./app/                # Copy your code
CMD exec uvicorn app.main:app   # Start the application
```

---

### `requirements.txt`

**Type:** Text file (Python dependency manifest)  
**Purpose:** Lists all Python packages your application needs

**What it does:**

- Specifies exact versions of libraries
- Ensures consistent environments across local/production
- Used by pip to install dependencies

**Why we need it:** Python projects rely on external libraries. This file ensures:

- Everyone uses the same versions
- Docker builds are reproducible
- Dependencies are documented

**Contents:**

```
fastapi==0.104.1        # Web framework
uvicorn[standard]==0.24.0  # ASGI server
pydantic==2.5.0         # Data validation
httpx==0.25.1           # HTTP client
anthropic==0.39.0       # Claude API SDK
```

---

## How It All Works Together

1. **You write code** in `app/main.py` and `app/agent.py`
2. **You push to GitHub** which triggers `deploy.yml`
3. **GitHub Actions** reads `Dockerfile` to build a container
4. **Docker** installs packages from `requirements.txt`
5. **The container** is pushed to Artifact Registry
6. **Cloud Run** deploys the container and runs `app/main.py`
7. **Users** can now call your agent via HTTPS endpoints

---

## Testing Your Agent

### Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
export ANTHROPIC_API_KEY="your-key-here"

# Run locally
python -m app.main

# Open browser to http://localhost:8080/docs
```

### Cloud Testing (Authenticated)

```bash
# Use proxy for secure local access
gcloud run services proxy agent-mvp --region=YOUR_REGION

# Then access at http://localhost:8080

# Or use curl with authentication
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  -X POST YOUR_SERVICE_URL/agent/process \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

---

## Architecture Overview

```
Developer
    ↓ (git push)
GitHub Repository
    ↓ (triggers)
GitHub Actions (deploy.yml)
    ↓ (builds)
Docker Image
    ↓ (stores in)
Artifact Registry
    ↓ (deploys to)
Cloud Run
    ↓ (serves)
HTTPS Endpoint
    ↓ (calls)
Claude API
```

---

## Cost Considerations

**Free Tier Includes:**

- Cloud Run: 2 million requests/month
- Artifact Registry: 0.5 GB storage
- Cloud Build: 120 build-minutes/day

This MVP should stay well within free tier limits for development and testing.

---

## Next Steps

1. **Add more agent capabilities**: Integrate tools, web search, database access
2. **Implement memory**: Store conversation history with Firestore
3. **Add authentication**: Implement API keys or OAuth
4. **Monitoring**: Set up Cloud Logging and alerts
5. **Scale**: Adjust Cloud Run settings for production traffic

---

## Security Best Practices

- ✅ Service account with minimal required permissions
- ✅ API keys stored as environment variables (not in code)
- ✅ Authenticated Cloud Run service by default
- ✅ HTTPS encryption automatic with Cloud Run
- ⚠️ Remember to rotate service account keys periodically
- ⚠️ Monitor API usage and set budget alerts

---

## Troubleshooting

**Deployment fails:**

- Check GitHub Actions logs for specific errors
- Verify service account has all required roles
- Ensure APIs are enabled in GCP

**403 Forbidden error:**

- Service requires authentication by default
- Use `gcloud run services proxy` for secure access
- Or add IAM policy binding for public access

**Agent returns errors:**

- Verify ANTHROPIC_API_KEY is set correctly
- Check Cloud Run logs: `gcloud run services logs read agent-mvp --region=YOUR_REGION`
- Ensure API key has sufficient credits

---

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
