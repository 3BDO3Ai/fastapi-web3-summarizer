# Web3 Article Summarizer - Usage Guide

This guide provides instructions on how to set up, run, and use the Web3 Article Summarizer API.

## Setup

1. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**

   Update the `.env` file with your API keys:
   
   - For OpenAI integration, add your API key to `OPENAI_API_KEY`
   - For Web3 functionality, add a provider URL to `WEB3_PROVIDER_URL` (e.g., from Alchemy or Infura)
   - Optionally set `HUGGINGFACE_API_KEY` if you prefer using HuggingFace for summarization

## Running the Application

### Local Development

Run the application using:

```bash
python run.py
```

The API will be available at http://localhost:8000.

### Using Docker

If you have Docker installed, you can build and run the application using Docker Compose:

```bash
docker-compose up -d
```

## API Endpoints

### 1. Summarize an Article

**Endpoint:** `POST /api/summarize`

**Input:**
```json
{
  "wallet_address": "0x...",
  "signature": "0x...",
  "article_url": "https://example.com/article"
}
```

**Notes:**
- The signature must be created by signing the message: "I am verifying my identity to use the Web3 Article Summarizer"
- You can use MetaMask or any Web3 wallet to create the signature

### 2. Get Summaries for a Wallet

**Endpoint:** `GET /api/summaries/{wallet_address}`

**Response:**
```json
{
  "summaries": [
    {
      "id": 1,
      "wallet_address": "0x...",
      "article_url": "https://example.com/article",
      "summary_content": "Summary text...",
      "created_at": "2025-05-18T12:34:56"
    }
  ]
}
```

## Using the Sample Client

For demonstration purposes, a sample client script is included:

```bash
python sample_client.py
```

This script:
1. Generates a temporary wallet and signature
2. Submits a Wikipedia article for summarization
3. Retrieves all summaries for the generated wallet

## Documentation

For detailed API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Running Tests

```bash
pytest
```

## Troubleshooting

### Common Issues

1. **Signature Verification Fails**
   - Ensure you're signing the exact message: "I am verifying my identity to use the Web3 Article Summarizer"
   - Check that the wallet address matches the one that created the signature

2. **Summarization Fails**
   - Verify your OpenAI API key is correct and has sufficient credits
   - If the article is too large, try a different article

3. **Database Issues**
   - By default, the app uses SQLite. The database file will be created in the project root
   - For persistent storage in Docker, ensure volumes are configured correctly
