"""Worker process for running the Content Amplifier workflow."""

import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from workflow import ContentAmplifierWorkflow
import activities
from llm_manager import MockLLMClient, BedrockLLM
from constants import TASK_QUEUE

async def main():
    """Run the worker process."""
    # Connect to the Temporal server
    client = await Client.connect("localhost:7233")

    # Initialize the LLM client
    # Uncomment to use Bedrock implementation
    # activities.llm_client = BedrockLLM()
    # Use mock implementation by default
    activities.llm_client = MockLLMClient()

    interrupt_event = asyncio.Event()

    # Run a worker for the workflow
    async with Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[ContentAmplifierWorkflow],
        activities=[
            activities.fetch_content,
            activities.summarise_content_diff,
            activities.select_promotion_channel,
            activities.promote_content
        ]
    ):
        # Wait until interrupted
        print("Worker started, ctrl+c to exit")
        await interrupt_event.wait()
        print("Shutting down")



if __name__ == "__main__":
    asyncio.run(main())
