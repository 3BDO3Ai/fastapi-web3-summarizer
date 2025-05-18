from web3 import Web3
from web3.auto import w3
import os
from fastapi import HTTPException
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Web3 with provider from environment variable
WEB3_PROVIDER_URL = os.getenv("WEB3_PROVIDER_URL", "https://eth-mainnet.g.alchemy.com/v2/your_api_key")
web3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URL))

# Message to be signed by the user
SIGN_MESSAGE = "I am verifying my identity to use the Web3 Article Summarizer"

async def verify_signature(wallet_address: str, signature: str) -> bool:
    """
    Verify that the signature was created by the wallet address.
    
    Args:
        wallet_address: The Ethereum wallet address
        signature: The signature created by the wallet
        
    Returns:
        bool: True if signature is valid, False otherwise
    """
    try:
        # Make sure address is checksum format
        wallet_address = web3.to_checksum_address(wallet_address)
        
        # Prepare the message that was signed
        message = SIGN_MESSAGE
        
        # Handle different signature formats
        if not signature:
            raise ValueError("Empty signature provided")
        
        # If signature doesn't start with 0x, add it
        if not signature.startswith('0x'):
            signature = '0x' + signature
            
        # Create the message hash
        from eth_account.messages import encode_defunct
        message_encoded = encode_defunct(text=message)
        
        # Recover the address that signed the message
        recovered_address = web3.eth.account.recover_message(message_encoded, signature=signature)
        
        # Check if the recovered address matches the provided address
        return recovered_address.lower() == wallet_address.lower()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Signature verification failed: {str(e)}")
        
def get_message_to_sign() -> str:
    """
    Returns the message that should be signed by the wallet
    """
    return SIGN_MESSAGE
