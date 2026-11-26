import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("ANTHROPIC_API_KEY")
print("KEY:", key[:10] + "..." if key else "NOT FOUND")

from anthropic import Anthropic

client = Anthropic(api_key=key)
model = "claude-opus-5-5"

message = client.messages.create(
    model=model,
    max_tokens=1000,
    thinking={"type": "adaptive", "display": "omitted"},
    messages=[
        {
            "role": "user",
            "content": "Write a poem about the importance of data engineering in the modern world. In 1 sentence"
        }
    ]
)

for block in message.content:
    if block.type == "text":
        print(block.text)