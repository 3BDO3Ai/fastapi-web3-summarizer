import asyncio
import httpx
from eth_account import Account
from eth_account.messages import encode_defunct
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Base URL - adjust if your server is running elsewhere
API_BASE_URL = "http://localhost:8000/api"

# The message that needs to be signed
SIGN_MESSAGE = "I am verifying my identity to use the Web3 Article Summarizer"

async def generate_wallet_and_signature():
    """Generate a temporary wallet and signature for demo purposes"""
    # WARNING: In a real application, you should use a secure wallet
    # This is for demonstration purposes only
    
    # Create a random account
    private_key = os.urandom(32).hex()
    account = Account.from_key(private_key)
    wallet_address = account.address
    
    # Sign the message
    message = encode_defunct(text=SIGN_MESSAGE)
    signed_message = Account.sign_message(message, private_key)
    
    # Format the signature correctly - ensure it has the 0x prefix
    signature = signed_message.signature.hex()
    if not signature.startswith('0x'):
        signature = '0x' + signature
    
    print(f"Generated signature: {signature[:10]}...{signature[-4:]}")
    
    return wallet_address, signature

async def summarize_article(wallet_address, signature, article_url):
    """Submit an article for summarization"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/summarize",
            json={
                "wallet_address": wallet_address,
                "signature": signature,
                "article_url": article_url
            }
        )
        
        if response.status_code == 201:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None

async def get_summaries(wallet_address):
    """Get all summaries for a wallet address"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/summaries/{wallet_address}")
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None

async def main():
    # Generate wallet and signature
    wallet_address, signature = await generate_wallet_and_signature()
    print(f"Generated wallet address: {wallet_address}")
    print(f"Using message: '{SIGN_MESSAGE}'")
    
    # Sample article URL
    article_url = "https://en.wikipedia.org/wiki/Blockchain"
    
    # Submit article for summarization
    print(f"\nSubmitting article for summarization: {article_url}")
    try:
        summary = await summarize_article(wallet_address, signature, article_url)
        if summary is None:
            print("Failed to summarize article. See error details above.")
    except Exception as e:
        print(f"Error during summarization request: {str(e)}")
        import traceback
        print(traceback.format_exc())
        summary = None
    
    if summary:
        print("\nSummary created successfully:")
        print(f"ID: {summary['id']}")
        print(f"Created at: {summary['created_at']}")
        print(f"Summary: {summary['summary_content'][:200]}...")
    
    # Get all summaries for this wallet
    print("\nFetching all summaries for this wallet...")
    summaries = await get_summaries(wallet_address)
    
    if summaries:
        print(f"Found {len(summaries['summaries'])} summaries:")
        for i, summary in enumerate(summaries['summaries']):
            print(f"\n{i+1}. Article: {summary['article_url']}")
            print(f"   Created: {summary['created_at']}")
            print(f"   Summary: {summary['summary_content'][:100]}...")

if __name__ == "__main__":
    asyncio.run(main())
