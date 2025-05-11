# My Agent Smith - Python

A Python implementation of the Agent Smith content amplifier using Temporal workflows.

## Overview

This application monitors a specified URL for content changes. When changes are detected, it:

1. Fetches the content from the URL
2. Summarizes the differences between the previous and current content using LLM
3. Selects appropriate promotion channels based on the content
4. Promotes the content to the selected channels

## Architecture

The application uses Temporal for workflow orchestration and Amazon Bedrock for LLM capabilities:

- **Workflow**: Orchestrates the entire process and maintains state between executions
- **Activities**: Perform individual tasks like fetching content, summarizing differences, etc.
- **LLM Client**: Interfaces with Amazon Bedrock for AI-powered content analysis

## Prerequisites

- Python 3.8+
- Temporal server running locally or remotely
- AWS credentials configured (for Bedrock integration)

## Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Start the Temporal Worker

Using the mock LLM client (default):
```bash
python worker.py
```

Using the Amazon Bedrock LLM client:
```bash
python worker.py --use-bedrock
```

With custom model ID and region:
```bash
python worker.py --use-bedrock --model-id anthropic.claude-v2 --region us-east-1
```

### Start the Workflow

```bash
python starter.py
```

## Configuration

Edit `constants.py` to configure:

- `MONITORED_URL`: The URL to monitor for content changes
- `MODEL_ID`: The default Amazon Bedrock model ID to use
- `TASK_QUEUE`: The Temporal task queue name

## Command Line Arguments

The worker supports the following command line arguments:

- `--use-bedrock`: Use the Bedrock LLM client instead of the mock client
- `--model-id`: Specify a custom Bedrock model ID (overrides the one in constants.py)
- `--region`: Specify a custom AWS region for Bedrock (defaults to us-west-2)

## Testing

Run the tests:

```bash
python -m unittest test_workflow.py
```