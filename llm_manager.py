"""LLM Manager for interacting with Amazon Bedrock."""

import json
import uuid
from abc import ABC, abstractmethod
import aioboto3
from constants import MODEL_ID


class LLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    async def summarise_diff(self, prev_content: str, curr_content: str) -> str:
        """Default implementation for summarizing content differences."""
        return f"Returns a mocked summary of the differences which changes on each invocation because it is appended with a UUID - {uuid.uuid4()}"
    
    async def select(self, prompt: str) -> str:
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
    
    def __init__(self, model_id=None, region=None):
        """Initialize the Bedrock client.
        
        Args:
            model_id (str, optional): The Bedrock model ID to use. Defaults to value from constants.
            region (str, optional): The AWS region to use. Defaults to us-west-2.
        """
        self.model_id = model_id or MODEL_ID
        self.region = region or "us-west-2"
        self.session = aioboto3.Session()
    
    async def summarise_diff(self, prev_content: str, curr_content: str) -> str:
        """Summarize differences between previous and current content."""
        prompt = f"""
        Compare the following two versions of content and generate a short, high-level summary of the meaningful differences:

        --- PREVIOUS VERSION ---
        {prev_content}

        --- CURRENT VERSION ---
        {curr_content}

        Respond in plain English with the most important updates readers should know about.
        """
        return await self.invoke_bedrock(prompt)
    
    async def select(self, diff_summary: str) -> str:
        """Select appropriate channels for promotion based on content."""
        prompt = f"""
                Review the difference summary provided here: {diff_summary}
                and suggest all the engagement channels this summary should be posted on.
                It should return a json list of strings with the channel names.
                The engagement channel options are:
                - Github
                - Slack #security
                - Slack #APIs
                - Slack #DevOps
                - InternalDevPortal
                """
        return await self.invoke_bedrock(prompt)
    
    async def invoke_bedrock(self, prompt: str) -> str:
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
            
            async with self.session.client(
                service_name='bedrock-runtime',
                region_name=self.region
            ) as client:
                response = await client.invoke_model(
                    modelId=self.model_id,
                    accept="application/json",
                    body=json.dumps(request_body)
                )
                
                # aioboto3 response handling is slightly different
                body = await response['body'].read()
                response_body = json.loads(body)
                response_text = response_body["results"][0]["outputText"]
                return response_text
        except Exception as e:
            print(f"Error invoking Bedrock: {e}")
            raise RuntimeError(f"Failed to invoke Bedrock: {e}")