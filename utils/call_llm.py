from openai import OpenAI, RateLimitError, APITimeoutError, APIConnectionError
import os
import time
import random
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Learn more about calling the LLM: https://the-pocket.github.io/PocketFlow/utility_function/llm.html
def call_llm(prompt, max_retries=3, base_delay=1.0):    
    """
    Call LLM with automatic retry and rate limit handling.
    
    Args:
        prompt: The prompt to send to the LLM
        max_retries: Maximum number of retry attempts (default: 3)
        base_delay: Base delay in seconds for exponential backoff (default: 1.0)
    
    Returns:
        str: The LLM response
        
    Raises:
        Exception: If all retry attempts fail
    """
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "your-api-key"))
    
    for attempt in range(max_retries + 1):
        try:
            r = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                timeout=30  # 30 second timeout
            )
            return r.choices[0].message.content
            
        except RateLimitError as e:
            if attempt == max_retries:
                raise Exception(f"Rate limit exceeded after {max_retries} retries: {str(e)}")
            
            # Extract wait time from error message if available
            wait_time = base_delay * (2 ** attempt) + random.uniform(0, 1)
            
            # Try to extract specific wait time from error message
            error_msg = str(e)
            if "try again in" in error_msg:
                try:
                    # Extract wait time from error message (e.g., "try again in 80ms")
                    wait_part = error_msg.split("try again in")[1].split()[0]
                    if "ms" in wait_part:
                        wait_time = float(wait_part.replace("ms", "")) / 1000.0
                    elif "s" in wait_part:
                        wait_time = float(wait_part.replace("s", ""))
                except:
                    pass  # Use exponential backoff if parsing fails
            
            print(f"Rate limit hit, waiting {wait_time:.2f} seconds before retry {attempt + 1}/{max_retries}")
            time.sleep(wait_time)
            
        except (APITimeoutError, APIConnectionError) as e:
            if attempt == max_retries:
                raise Exception(f"API connection error after {max_retries} retries: {str(e)}")
            
            wait_time = base_delay * (2 ** attempt) + random.uniform(0, 1)
            print(f"API connection error, waiting {wait_time:.2f} seconds before retry {attempt + 1}/{max_retries}")
            time.sleep(wait_time)
            
        except Exception as e:
            # For other errors, don't retry
            raise Exception(f"LLM call failed: {str(e)}")
    
    raise Exception("Unexpected error in call_llm")
    
if __name__ == "__main__":
    prompt = "What is the meaning of life?"
    print(call_llm(prompt))
