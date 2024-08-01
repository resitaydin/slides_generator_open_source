import requests
import base64
import uuid
import json
import time
from typing import Dict, Optional, Any
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

AUTH_TOKEN = os.getenv("AUTH_TOKEN")
COOKIE = os.getenv("COOKIE")

# print(f"AUTH_TOKEN: {AUTH_TOKEN}")
# print(f"COOKIE: {COOKIE}")

def get_auth_token(timeout: float = 2) -> Dict[str, Any]:
    """
    Get authentication token.

    Args:
        timeout (float): Timeout duration in seconds.

    Returns:
        Dict[str, Any]: Dictionary containing the access token and its expiration time.
    """
    url = "https://beta.saluteai.sberdevices.ru/v1/token"
    payload = 'scope=GIGACHAT_API_CORP'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': str(uuid.uuid4()),
        'Cookie': COOKIE,
        'Authorization': f'Basic {AUTH_TOKEN}'
    }
    response = requests.post(url, headers=headers, data=payload, timeout=timeout)
    response_dict = response.json()
    return {
        'access_token': response_dict['tok'],
        'expires_at': response_dict['exp']
    }

def check_auth_token(token_data: Dict[str, Any]) -> bool:
    """
    Check if the authentication token is valid.

    Args:
        token_data (Dict[str, Any]): Dictionary containing token data.

    Returns:
        bool: True if the token is valid, False otherwise.
    """
    return token_data['expires_at'] - time.time() > 5

token_data: Optional[Dict[str, Any]] = None

def get_response(
    prompt: str,
    model: str,
    timeout: int = 120,
    n: int = 1,
    fuse_key_word: Optional[str] = None,
    use_giga_censor: bool = False,
    max_tokens: int = 512,
) -> requests.Response:
    """
    Send a text generation request to the API.

    Args:
        prompt (str): The input prompt.
        model (str): The model to be used for generation.
        timeout (int): Timeout duration in seconds.
        n (int): Number of responses.
        fuse_key_word (Optional[str]): Additional keyword to include in the prompt.
        use_giga_censor (bool): Whether to use profanity filtering.
        max_tokens (int): Maximum number of tokens in the response.

    Returns:
        requests.Response: API response.
    """
    global token_data
    
    url = "https://beta.saluteai.sberdevices.ru/v1/chat/completions"
    payload = json.dumps({
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": ' '.join([fuse_key_word, prompt]) if fuse_key_word else prompt
            }
        ],
        "temperature": 0.87,
        "top_p": 0.47,
        "n": n,
        "stream": False,
        "max_tokens": max_tokens,
        "repetition_penalty": 1.07,
        "profanity_check": use_giga_censor
    })

    if token_data is None or not check_auth_token(token_data): 
        token_data = get_auth_token()
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {token_data["access_token"]}'
    }
    response = requests.post(url, headers=headers, data=payload, timeout=timeout)
    return response
   
def giga_generate(
    prompt: str, 
    model_version: str = "GigaChat-Pro", 
    max_tokens: int = 2048
) -> str:
    """
    Generate text using the GigaChat model.

    Args:
        prompt (str): The input prompt.
        model_version (str): The version of the model to use.
        max_tokens (int): Maximum number of tokens in the response.

    Returns:
        str: Generated text.
    """
    response = get_response(
        prompt,
        model_version,
        use_giga_censor=False,
        max_tokens=max_tokens,
    )
    response_dict = response.json()

    if response_dict['choices'][0]['finish_reason'] == 'blacklist':
        print('GigaCensor triggered!')
        return 'Censored Text'
    else:
        response_str = response_dict['choices'][0]['message']['content']
        return response_str