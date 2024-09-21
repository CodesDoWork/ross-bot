from enum import Enum
from openai import OpenAI
from typing import TypedDict
from src.assistant_config import instruction, model, tools


class Assistant:

    def __init__(self):
        self.client = OpenAI()
        self.assistant = self.client.beta.assistants.create(instructions=instruction, model=model, tools=tools)
        self.states: dict[int, AssistantStatus] = {}

    def process_request(self, chat_id: int, request: str) -> str:
        if chat_id not in self.states:
            self.set_idle(chat_id)
        return request

    def gpt(self, request: str) -> str:
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": request
                }
            ]
        )

        return completion.choices[0].message.content

    def set_idle(self, chat_id: int):
        thread = self.client.beta.threads.create()
        self.states[chat_id] = {"status": Assistant.Status.Idle, "thread": thread}

    class Status(Enum):
        Idle = 0
        Clarification = 1
        Processing = 2


class AssistantStatus(TypedDict):
    status: Assistant.Status
    thread: int
