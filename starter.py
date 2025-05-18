"""Starter script to initiate the Content Amplifier workflow."""

import asyncio
import uuid
import argparse
from datetime import timedelta
from temporalio.client import Client, Schedule, ScheduleSpec, ScheduleState
from workflow import ContentAmplifierWorkflow
from constants import TASK_QUEUE, MONITORED_URL


async def start_workflow(monitored_url):
    """Start the Content Amplifier workflow."""
    # Connect to the Temporal server
    client = await Client.connect("localhost:7233")
    
    # Generate a unique workflow ID
    workflow_id = f"content-amplifier"
    print(f"Starting a new workflow: {workflow_id}")
    
    # Start the workflow
    await client.start_workflow(
        ContentAmplifierWorkflow,
        args=[monitored_url],
        id=workflow_id,
        task_queue=TASK_QUEUE
    )
    
    print("Workflow started and the app is terminating. Long live the workflow...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start Content Amplifier workflow')
    parser.add_argument('--url', default=MONITORED_URL, help='URL to monitor')
    args = parser.parse_args()
    
    asyncio.run(start_workflow(args.url))
