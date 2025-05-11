"""Content Amplifier Workflow implementation."""

from temporalio import workflow
from temporalio.common import RetryPolicy
from datetime import timedelta

with workflow.unsafe.imports_passed_through():
    from activities import (
        fetch_content, 
        summarise_content_diff, 
        select_promotion_channel, 
        promote_content, 
        ContentDiffInput,
        PromoteContentInput
    )


@workflow.defn
class ContentAmplifierWorkflow:
    """Workflow that monitors content changes and promotes updates."""
    
    def __init__(self) -> None:
        self.last_content_hash = ""
        self.last_content = ""
    
    @workflow.run
    async def run(self, url: str) -> None:
        """Run the content amplifier workflow."""
        workflow.logger.info(f"Starting workflow {workflow.info().workflow_id}")
        
        # Create activity stubs with timeout and retry policy
        config = workflow.ActivityConfig(
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=10),
                maximum_attempts=3
            )
        )
        
        while True:
            # Fetch the current content
            content = await workflow.execute_activity(
                fetch_content,
                url,
                **config
            )
            
            # Calculate hash of the content
            content_hash = str(hash(content))
            
            # Check if content has changed
            if content_hash != self.last_content_hash:
                workflow.logger.info("Content has changed, processing updates")
                
                # Summarize the differences using ContentDiffInput data class
                summary = await workflow.execute_activity(
                    summarise_content_diff,
                    ContentDiffInput(prev_content=self.last_content, current_content=content),
                    **config
                )
                
                if summary != "":
                    workflow.logger.info(f"Summary: {summary}")
                    
                    # Select promotion channel
                    channel = await workflow.execute_activity(
                        select_promotion_channel,
                        summary,
                        **config
                    )
                    
                    # Promote the content using PromoteContentInput data class
                    await workflow.execute_activity(
                        promote_content,
                        PromoteContentInput(summary=summary, channel=channel),
                        **config
                    )
                
                # Update the last content and hash
                self.last_content_hash = content_hash
                self.last_content = content
            else:
                workflow.logger.info("No content changes detected")
                
            # Sleep for 10 seconds before next check
            await workflow.sleep(timedelta(seconds=10))