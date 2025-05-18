from web3 import Web3
from web3.auto import w3
import os
import logging
from fastapi import HTTPException
from dotenv import load_dotenv
from eth_account.messages import encode_defunct

load_dotenv()

WEB3_PROVIDER_URL = os.getenv("WEB3_PROVIDER_URL", "https://eth-mainnet.g.alchemy.com/v2/your_api_key")
web3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URL))

SIGN_MESSAGE = "I am verifying my identity to use the Web3 Article Summarizer"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def verify_signature(wallet_address: str, signature: str) -> bool:
    try:
        wallet_address = web3.to_checksum_address(wallet_address)
        
        message = SIGN_MESSAGE
        
        if not signature:
            raise ValueError("Empty signature provided")
        
        if not signature.startswith('0x'):
            signature = '0x' + signature
            
        message_encoded = encode_defunct(text=message)
        
        recovered_address = web3.eth.account.recover_message(message_encoded, signature=signature)
        
        is_valid = recovered_address.lower() == wallet_address.lower()
        logger.info(f"Signature verification for {wallet_address}: {'Valid' if is_valid else 'Invalid'}")
        return is_valid
    except Exception as e:
        logger.error(f"Signature verification error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Signature verification failed: {str(e)}")

async def get_message_to_sign() -> str:
    return SIGN_MESSAGE
