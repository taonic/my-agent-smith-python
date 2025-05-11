"""Worker process for running the Content Amplifier workflow."""

import asyncio
import argparse
from temporalio.client import Client
from temporalio.worker import Worker
from workflow import ContentAmplifierWorkflow
import activities
from llm_manager import MockLLMClient, BedrockLLM
from constants import TASK_QUEUE, MODEL_ID


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Content Amplifier Worker")
    parser.add_argument("--use-bedrock", action="store_true", default=False, help="Use Bedrock LLM instead of mock")
    parser.add_argument("--model-id", type=str, default=MODEL_ID, help="Bedrock model ID to use")
    parser.add_argument("--region", type=str, default="ap-southeast-2", help="AWS region for Bedrock")
    return parser.parse_args()


async def main():
    """Run the worker process."""
    args = parse_args()
    
    # Connect to the Temporal server
    client = await Client.connect("localhost:7233")
    
    # Initialize the LLM client based on command line arguments
    if args.use_bedrock:
        activities.llm_client = BedrockLLM(
            model_id=args.model_id,
            region=args.region
        )
        print(f"Using Bedrock LLM with model {args.model_id} in region {args.region}")
    else:
        activities.llm_client = MockLLMClient()
        print("Using Mock LLM client")
    
    # Create a worker
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[ContentAmplifierWorkflow],
        activities=[
            activities.fetch_content,
            activities.summarise_content_diff,
            activities.select_promotion_channel,
            activities.promote_content
        ]
    )
    
    print("Worker started")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())