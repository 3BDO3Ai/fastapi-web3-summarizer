import os
import openai
import httpx
import json
from transformers import pipeline
from fastapi import HTTPException
from dotenv import load_dotenv
import logging
from typing import Dict, Any, Optional

# Load environment variables
load_dotenv()

# Initialize API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# HuggingFace API constants
HF_API_URL = "https://api-inference.huggingface.co/models/"

# Get the model from environment variable or use default
HF_MODEL = os.getenv("HUGGINGFACE_MODEL", "facebook/bart-large-cnn")

# List of recommended summarization models
RECOMMENDED_MODELS = {
    "facebook/bart-large-cnn": "Good general-purpose news summarizer",
    "sshleifer/distilbart-cnn-12-6": "Faster, smaller version of BART",
    "google/pegasus-xsum": "Higher quality but slower",
    "t5-base": "Versatile text-to-text model",
    "facebook/bart-large-xsum": "Extreme summarization (very concise)"
}

class SummarizerService:
    def __init__(self):
        # Determine which service to use based on available API keys
        if OPENAI_API_KEY:
            self.service_type = "openai"
            openai.api_key = OPENAI_API_KEY
            logging.info("Using OpenAI for summarization")
        elif HUGGINGFACE_API_KEY:
            self.service_type = "huggingface"
            self.hf_headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
            self.model_name = HF_MODEL
            logging.info(f"Using HuggingFace Inference API with model: {self.model_name}")
            
            # Log if using a recommended model
            if self.model_name in RECOMMENDED_MODELS:
                logging.info(f"Model description: {RECOMMENDED_MODELS[self.model_name]}")
            else:
                logging.warning(f"Using custom model: {self.model_name} (not in recommended list)")
            
            # Also initialize a local pipeline as fallback if possible
            try:
                self.local_pipeline = pipeline("summarization")
                logging.info("Successfully initialized local HuggingFace pipeline as fallback")
                self.has_local_fallback = True
            except Exception as e:
                logging.warning(f"Could not initialize local HuggingFace pipeline: {e}")
                self.has_local_fallback = False
        else:
            # If no API keys are available, use mock service for testing
            logging.warning("No API keys found for OpenAI or HuggingFace. Using mock summarizer.")
            self.service_type = "mock"
    
    async def summarize_text(self, text: str, max_length: int = 1500) -> str:
        """
        Summarize the provided text using either OpenAI, HuggingFace, or a mock service
        
        Args:
            text: The text to summarize
            max_length: Maximum length of text to summarize (for truncation)
            
        Returns:
            str: Summarized text
        """
        # Truncate text if too long
        if len(text) > max_length:
            text = text[:max_length]
        
        try:
            if self.service_type == "openai":
                return await self._summarize_with_openai(text)
            elif self.service_type == "huggingface":
                return await self._summarize_with_huggingface(text)
            else:
                return await self._mock_summarize(text)
        except Exception as e:
            logging.error(f"Summarization failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")
    
    async def _summarize_with_openai(self, text: str) -> str:
        """Use OpenAI API to summarize text"""
        try:
            # Modern OpenAI client implementation
            client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes articles."},
                    {"role": "user", "content": f"Please summarize the following article: {text}"}
                ],
                max_tokens=500,
                temperature=0.5
            )
            return response.choices[0].message.content
        except ImportError:
            # Fallback for older versions of the OpenAI library
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes articles."},
                    {"role": "user", "content": f"Please summarize the following article: {text}"}
                ],
                max_tokens=500,
                temperature=0.5
            )
            return response.choices[0].message.content
    
    async def _summarize_with_huggingface(self, text: str) -> str:
        """Use HuggingFace Inference API to summarize text"""
        # For the Inference API, we need to limit text length and chunk it appropriately
        # Most models have a max token limit (e.g., 1024 tokens)
        
        # Split longer texts into manageable chunks
        # BART models typically handle ~1024 tokens which is roughly 750-1000 chars
        chunks = [text[i:i+3000] for i in range(0, len(text), 3000)]
        all_summaries = []
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                for chunk in chunks:
                    # First try the HuggingFace Inference API
                    try:
                        summary = await self._call_huggingface_api(client, chunk)
                        if summary:
                            all_summaries.append(summary)
                        else:
                            # If the API call returns empty, use fallback methods
                            fallback_summary = await self._huggingface_fallback(chunk)
                            all_summaries.append(fallback_summary)
                    except Exception as e:
                        logging.error(f"HuggingFace API error: {str(e)}")
                        # Use fallback if API call fails
                        fallback_summary = await self._huggingface_fallback(chunk)
                        all_summaries.append(fallback_summary)
            
            # Combine the summaries from all chunks
            return " ".join(all_summaries).strip()
            
        except Exception as e:
            logging.error(f"Error during HuggingFace summarization: {str(e)}")
            # Last resort fallback to mock summarizer
            return await self._mock_summarize(text)
    
    async def _call_huggingface_api(self, client: httpx.AsyncClient, text: str) -> Optional[str]:
        """Call the HuggingFace Inference API for summarization"""
        # Adjust parameters based on model type
        if 't5' in self.model_name.lower():
            # T5 models need different parameters
            payload = {
                "inputs": text,
                "parameters": {
                    "max_length": 250,
                    "min_length": 40,
                    "do_sample": False,
                    "task": "summarization"
                }
            }
        else:
            # BART and other models
            payload = {
                "inputs": text,
                "parameters": {
                    "max_length": 250,
                    "min_length": 50,
                    "do_sample": False
                }
            }
        
        response = await client.post(
            f"{HF_API_URL}{self.model_name}",
            headers=self.hf_headers,
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            # Handle different response formats
            if isinstance(result, list) and len(result) > 0:
                if 'summary_text' in result[0]:
                    return result[0]['summary_text']
                elif 'generated_text' in result[0]:
                    return result[0]['generated_text']
            elif isinstance(result, dict) and 'summary_text' in result:
                return result['summary_text']
        
        # Return None if we couldn't parse the response
        return None
        
    async def _huggingface_fallback(self, text: str) -> str:
        """Fallback method when the HuggingFace API fails"""
        # Try the local pipeline if available
        if hasattr(self, 'has_local_fallback') and self.has_local_fallback:
            try:
                result = self.local_pipeline(text, max_length=150, min_length=40, do_sample=False)
                return result[0]['summary_text']
            except Exception as e:
                logging.error(f"Local pipeline fallback failed: {str(e)}")
                
        # If local pipeline fails or isn't available, use mock summarizer
        return await self._mock_summarize(text)
        
    async def _mock_summarize(self, text: str) -> str:
        """
        Mock summarization for testing purposes when no API keys are available
        
        This creates a simple summary by extracting important sentences from the text
        """
        # Split text into sentences
        sentences = text.split(". ")
        
        # For very short texts, just return the original
        if len(sentences) <= 3:
            return text
            
        # Simple heuristic: take the first sentence, a middle sentence, and the last sentence
        important_sentences = [
            sentences[0],
            sentences[len(sentences)//2],
            sentences[-1]
        ]
        
        # Join with periods and ensure proper formatting
        summary = ". ".join(important_sentences)
        if not summary.endswith("."):
            summary += "."
            
        return summary

# Create a singleton instance
summarizer = SummarizerService()
