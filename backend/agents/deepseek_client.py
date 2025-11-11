"""
Deepseek API Client with Streaming Support
"""

import requests
import os
from dotenv import load_dotenv
from typing import List, Dict, Generator
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()


class DeepseekClient:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = "https://api.deepseek.com/chat/completions"
        self.model = "deepseek-chat"

        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY not found in environment variables!")

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """Regular non-streaming chat"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            response = requests.post(
                self.base_url, headers=headers, json=payload, timeout=30, verify=False
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]

        except requests.exceptions.RequestException as e:
            print(f"Error calling Deepseek API: {e}")
            raise

    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> Generator[str, None, None]:
        """Streaming chat - yields tokens as they arrive"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,  # Enable streaming
        }

        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                stream=True,
                timeout=30,
                verify=False,
            )
            response.raise_for_status()

            # Parse SSE stream
            for line in response.iter_lines():
                if line:
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        data = line[6:]  # Remove 'data: ' prefix
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            if "choices" in chunk and len(chunk["choices"]) > 0:
                                delta = chunk["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue

        except requests.exceptions.RequestException as e:
            print(f"Error in streaming: {e}")
            raise

    def chat_with_system(
        self, system_prompt: str, user_message: str, temperature: float = 0.7
    ) -> str:
        """Convenience method"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]
        return self.chat(messages, temperature=temperature)


# Test function
def test_deepseek():
    client = DeepseekClient()

    response = client.chat_with_system(
        system_prompt="You are a helpful assistant for PartSelect.com, specializing in refrigerator and dishwasher parts.",
        user_message="Hello! Can you help me with my refrigerator?",
    )

    print("Deepseek Response:")
    print(response)


if __name__ == "__main__":
    test_deepseek()
