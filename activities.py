"""Activity implementations for the Content Amplifier workflow."""

import requests
from dataclasses import dataclass
from temporalio import activity
from llm_manager import LLMClient


# Global LLM client to be initialized in worker.py
llm_client: LLMClient = None


@dataclass
class ContentDiffInput:
    """Input data for content difference summarization."""
    prev_content: str
    current_content: str


@dataclass
class PromoteContentInput:
    """Input data for content promotion."""
    summary: str
    channel: str


@activity.defn
async def fetch_content(url: str) -> str:
    """Fetch content from the specified URL."""
    activity.logger.info(f"Fetching content from {url}")
    try:
        # Using requests synchronously is fine for simple HTTP calls
        # For production, consider using aiohttp for async HTTP requests
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        activity.logger.error(f"Failed to fetch content from {url}: {e}")
        raise RuntimeError(f"Failed to fetch content from {url}: {e}")


@activity.defn
async def summarise_content_diff(input_data: ContentDiffInput) -> str:
    """Summarize differences between previous and current content."""
    activity.logger.info("Summarizing content differences")
    if llm_client is None:
        raise RuntimeError("LLM client not initialized")
    return await llm_client.summarise_diff(input_data.prev_content, input_data.current_content)


@activity.defn
async def select_promotion_channel(summary: str) -> str:
    """Select appropriate channel for content promotion."""
    activity.logger.info("Selecting promotion channel")
    if llm_client is None:
        raise RuntimeError("LLM client not initialized")
    return await llm_client.select(summary)


@activity.defn
async def promote_content(input_data: PromoteContentInput) -> None:
    """Promote content to the selected channel."""
    activity.logger.info(f"Promoting content to {input_data.channel}")
    print(f"🚀 Promoting to {input_data.channel}. \nThe post will include -- {input_data.summary}")
    # Optionally: Add real Slack/GitHub posting logic here