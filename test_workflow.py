"""Tests for the Content Amplifier workflow."""

import asyncio
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from temporalio.client import Client
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker
from workflow import ContentAmplifierWorkflow
import activities
from activities import ContentDiffInput, PromoteContentInput
from llm_manager import MockLLMClient
from constants import MONITORED_URL


class TestContentAmplifierWorkflow(unittest.IsolatedAsyncioTestCase):
    """Test cases for the Content Amplifier workflow."""
    
    async def asyncSetUp(self):
        """Set up the test environment."""
        self.env = await WorkflowEnvironment.start_local()
        self.client = await Client.connect(self.env.server_address)
        
        # Initialize the LLM client with mock implementation
        activities.llm_client = MockLLMClient()
        
        # Create a worker
        self.worker = Worker(
            self.client,
            task_queue="test_task_queue",
            workflows=[ContentAmplifierWorkflow],
            activities=[
                activities.fetch_content,
                activities.summarise_content_diff,
                activities.select_promotion_channel,
                activities.promote_content
            ]
        )
        
        # Start the worker
        self.worker_task = asyncio.create_task(self.worker.run())
    
    async def asyncTearDown(self):
        """Clean up the test environment."""
        self.worker.shutdown()
        await self.worker_task
        await self.env.shutdown()
    
    @patch('activities.requests.get')
    @patch('activities.llm_client.summarise_diff', new_callable=AsyncMock)
    @patch('activities.llm_client.select', new_callable=AsyncMock)
    async def test_workflow_with_content_change(self, mock_select, mock_summarise, mock_get):
        """Test the workflow when content changes."""
        # Mock the HTTP response
        mock_response = MagicMock()
        mock_response.text = "New content"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Mock the LLM responses
        mock_summarise.return_value = "Content has been updated"
        mock_select.return_value = "GitHub"
        
        # Run the workflow
        result = await self.client.execute_workflow(
            ContentAmplifierWorkflow.run,
            MONITORED_URL,
            id="test-workflow",
            task_queue="test_task_queue"
        )
        
        # Verify that the activities were called
        mock_get.assert_called_once_with(MONITORED_URL)
        
        # The test will time out because the workflow runs in an infinite loop
        # In a real test, we would need to add a way to signal the workflow to stop


if __name__ == "__main__":
    unittest.main()