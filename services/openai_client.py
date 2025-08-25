# services/openai_client.py
from openai import OpenAI
import json

def classify_items(items: list, assistant_id: str, api_key: str):
    """
    Send list of items to OpenAI Assistant and return parsed JSON result.
    """
    client = OpenAI(api_key=api_key)

    # Create thread
    thread = client.beta.threads.create()

    # Add user message (items as JSON)
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=json.dumps(items, ensure_ascii=False)
    )

    # Run assistant
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )

    if run.status == 'completed':
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        msg_content = messages.data[0].content[0].text.value
        return json.loads(msg_content)
    else:
        raise RuntimeError(f"Run failed with status: {run.status}")
