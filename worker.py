import asyncio

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker

from activities import extract_entities

CustomExtractionQueue = "CustomExtractQueue"


async def main():
    client = await Client.connect("localhost:7233", namespace="bioinformatics")
    # Run the worker
    worker = Worker(
        client, task_queue=CustomExtractionQueue, activities=[extract_entities], identity="NER-Worker"
    )
    print("Start pubtator worker...")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
