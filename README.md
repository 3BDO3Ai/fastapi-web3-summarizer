# FastAPI Web3 Article Summarizer

[![Docker Image](https://img.shields.io/docker/pulls/3bdoai3/web3-summarizer-api.svg)](https://hub.docker.com/r/3bdoai3/web3-summarizer-api)

A REST API that allows users to submit articles for summarization while verifying their identity using Web3 signatures. This project is built according to the specified task requirements, including Web3 validation, article scraping, AI-powered summarization, and database storage.

## Features

- **Web3 Authentication**: Secure signature verification using Web3.py
- **Article Scraping**: Efficiently extracts content from provided URLs
- **Dual AI Integration**: Supports both OpenAI and HuggingFace for summarization
  - Configurable HuggingFace model selection
  - Graceful fallback mechanisms when API keys aren't available
- **Database Storage**: Persistent storage of summaries with PostgreSQL
- **Async Implementation**: Non-blocking API design for better performance
- **Clean Architecture**: Modular code structure with separation of concerns
- **Docker Integration**: Production-ready containerization with multi-stage builds
- **Docker Hub Support**: Easy publishing to Docker Hub with automated scripts

## API Endpoints

### POST /api/summarize
- **Purpose**: Submit an article URL for summarization
- **Authentication**: Requires wallet address and signature for verification
- **Input**:
  ```json
  {
    "wallet_address": "0x...",
    "signature": "0x...",
    "article_url": "https://example.com/article"
  }
  ```
- **Process**: Verifies signature → Scrapes article → Summarizes content → Stores in database
- **Response**: Returns the summarized content with metadata

### GET /api/summaries/{wallet_address}
- **Purpose**: Retrieve all summaries associated with a wallet address
- **Response**: Returns an array of all summaries created by the specified wallet

## Tech Stack

- **Backend**: Python 3.10, FastAPI
- **Authentication**: Web3.py for Ethereum signature verification
- **Data Storage**: PostgreSQL
- **AI Integration**: 
  - OpenAI GPT-3.5 for summarization when OpenAI API key is available
  - HuggingFace models (configurable) with multiple fallback mechanisms
- **Scraping**: Beautiful Soup and httpx for asynchronous content extraction
- **Containerization**: Docker and Docker Compose support

## Setup Instructions

### Local Development

1. **Clone the repository**
   ```bash
   git clone [repository-url]
   cd fastapi-web3-summarizer
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Unix/MacOS
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

5. **Run the application**
   ```bash
   python run.py
   # Alternatively: uvicorn app.main:app --reload
   ```

### Docker Setup

#### Using Local Build
```bash
docker-compose up -d
```

#### Using Docker Hub Image
The application is available as a Docker image on Docker Hub:

```bash
# Pull and run using the published image
docker pull 3bdoai3/web3-summarizer-api:latest
docker-compose up -d
```

#### Publishing to Docker Hub
To publish your own version to Docker Hub:

```bash
# For Windows users
.\publish_to_dockerhub.ps1 YOUR_DOCKERHUB_USERNAME

# For Linux/Mac users
chmod +x publish_to_dockerhub.sh
./publish_to_dockerhub.sh YOUR_DOCKERHUB_USERNAME
```

## Usage

### API Access

The API will be available at `http://localhost:8000`

### Documentation

Comprehensive API documentation is available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Sample Client

A sample client is included to demonstrate the full workflow:

```bash
python sample_client.py
```

This script:
1. Generates a temporary wallet and signs a message
2. Submits an article URL for summarization
3. Retrieves all summaries for the wallet

### AI Integration Options

1. **OpenAI**: Add your API key to the `.env` file:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

2. **HuggingFace**: Add your API key and select a model:
   ```
   HUGGINGFACE_API_KEY=your_api_key_here
   HUGGINGFACE_MODEL=facebook/bart-large-cnn
   ```
   
   Available models include:
   - `facebook/bart-large-cnn` (default)
   - `sshleifer/distilbart-cnn-12-6` (faster)
   - `google/pegasus-xsum` (higher quality)
   - `facebook/bart-large-xsum` (more concise)

### Web3 Signature Verification

To generate a valid signature for testing, use the message:
```
I am verifying my identity to use the Web3 Article Summarizer
```

### Testing

Run tests with:
```bash
pytests
```

## Project Structure

```
├── app/                     # Main application package
│   ├── routers/             # API route definitions
│   ├── schemas/             # Pydantic models
│   ├── services/            # Business logic
│   ├── database.py          # Database configuration
│   ├── main.py              # FastAPI application
│   └── models.py            # SQLAlchemy models
├── tests/                   # Test suite
├── .env                     # Environment variables (create from .env.example)
├── .env.example             # Example environment configuration
├── docker-compose.yml       # Docker Compose configuration
├── Dockerfile               # Docker configuration with multi-stage build
├── publish_to_dockerhub.ps1 # PowerShell script for Docker Hub publishing
├── publish_to_dockerhub.sh  # Bash script for Docker Hub publishing
├── requirements.txt         # Python dependencies
├── run.py                   # Application entry point
└── sample_client.py         # Example client implementation
```

## Evaluation Criteria Fulfillment

1. **Clean, modular FastAPI structure**: 
   - Separation of concerns with routers, services, and schemas
   - Clear dependency injection
   - Organized project structure

2. **Correct use of signature validation**:
   - Proper Web3.py integration
   - Secure signature verification
   - Appropriate error handling

3. **Working AI integration**:
   - Dual support for OpenAI and HuggingFace
   - Configurable model selection
   - Graceful fallbacks when keys are missing

4. **Async usage and database handling**:
   - Fully asynchronous API design
   - SQLAlchemy integration with async patterns
   - Clean repository pattern implementation
