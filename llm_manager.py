"""LLM Manager for interacting with Amazon Bedrock."""

import json
import uuid
from abc import ABC, abstractmethod
import boto3
from constants import MODEL_ID


class LLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    def summarise_diff(self, prev_content: str, curr_content: str) -> str:
        """Default implementation for summarizing content differences."""
        return f"Returns a mocked summary of the differences which changes on each invocation because it is appended with a UUID - {uuid.uuid4()}"
    
    def select(self, prompt: str) -> str:
        """Default implementation for selecting promotion channels."""
        prompt_lower = prompt.lower()
        if "api" in prompt_lower:
            return "GitHub"
        elif "security" in prompt_lower:
            return "Slack"
        else:
            return "InternalPortal"


class MockLLMClient(LLMClient):
    """Mock implementation of LLM client for testing."""
    pass


class BedrockLLM(LLMClient):
    """Implementation of LLM client using Amazon Bedrock."""
    
    def __init__(self):
        """Initialize the Bedrock client."""
        self.client = boto3.client(
            service_name='bedrock-runtime',
            region_name='us-west-2'
        )
    
    def summarise_diff(self, prev_content: str, curr_content: str) -> str:
        """Summarize differences between previous and current content."""
        prompt = f"""
        Compare the following two versions of content and generate a short, high-level summary of the meaningful differences:

        --- PREVIOUS VERSION ---
        {prev_content}

        --- CURRENT VERSION ---
        {curr_content}

        Respond in plain English with the most important updates developers should know about.
        """
        return self.invoke_bedrock(prompt)
    
    def select(self, diff_summary: str) -> str:
        """Select appropriate channels for promotion based on content."""
        prompt = f"Review the difference summary provided here {diff_summary} and suggest all the engagement channels this summary should be posted on, the engagement channel options are Github, Slack #security, Slack #APIs, Slack #DevOps, InternalDevPortal"
        return self.invoke_bedrock(prompt)
    
    def invoke_bedrock(self, prompt: str) -> str:
        """Invoke Bedrock model with the given prompt."""
        try:
            titan_prompt = f"\n\nHuman: {prompt}\n\nAssistant:"
            
            request_body = {
                "inputText": titan_prompt,
                "textGenerationConfig": {
                    "temperature": 0.5,
                    "topP": 0.9,
                    "maxTokenCount": 5000,
                    "stopSequences": []
                }
            }
            
            response = self.client.invoke_model(
                modelId=MODEL_ID,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response.get('body').read())
            response_text = response_body.get('outputText', '')
            print(f"Model output: {response_text}")
            return response_text
        except Exception as e:
            print(f"Error invoking Bedrock: {e}")
            raise RuntimeError(f"Failed to invoke Bedrock: {e}")