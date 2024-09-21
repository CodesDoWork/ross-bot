import json
from enum import Enum
from openai import OpenAI
from openai.types.beta.threads.run import Run
from typing import TypedDict, Literal
from src.assistant_config import instruction, model, tools
from src.data import get_df


class Assistant:

    def __init__(self):
        self.client = OpenAI()
        self.assistant = self.client.beta.assistants.create(instructions=instruction, model=model, tools=tools)
        self.states: dict[int, AssistantStatus] = {}
        self.df = get_df()

    def process_request(self, chat_id: int, request: str) -> str:
        if chat_id not in self.states:
            self.set_idle(chat_id)

        status = self.get_status(chat_id)
        if status == Assistant.Status.Idle:
            return self.process_idle(chat_id, request)
        elif status == Assistant.Status.Clarification:
            return self.process_clarification(chat_id, request)
        else:
            return "..."

    def process_idle(self, chat_id: int, request: str) -> str:
        self.states[chat_id]["status"] = Assistant.Status.Clarification
        return self.process_clarification(chat_id, request)

    def process_clarification(self, chat_id: int, request: str) -> str:
        self.add_message(chat_id, "user", request)
        return self.answer(chat_id)

    def add_message(self, chat_id: int, role: Literal["user", "assistant"], message: str):
        self.client.beta.threads.messages.create(
            thread_id=self.get_thread(chat_id),
            role=role,
            content=message,
        )

    def answer(self, chat_id: int) -> str:
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=self.get_thread(chat_id),
            assistant_id=self.assistant.id,
        )
        return self.handle_run(chat_id, run)

    def handle_run(self, chat_id: int, run: Run) -> str:
        if run.status == "completed":
            return self.client.beta.threads.messages.list(thread_id=self.get_thread(chat_id)).data[0].content[0].text.value
        return self.add_function_outputs(chat_id, run)

    def add_function_outputs(self, chat_id: int, run: Run) -> str:
        tool_outputs = []
        for tool in run.required_action.submit_tool_outputs.tool_calls:
            if tool.function.name == "get_relevant_people":
                tool_outputs.append({
                    "tool_call_id": tool.id,
                    "output": self.get_relevant_people(json.loads(tool.function.arguments))
                })
            else:
                raise Exception("Unsupported tool: " + tool.function.name)

        tool_run = self.client.beta.threads.runs.submit_tool_outputs_and_poll(
            thread_id=self.get_thread(chat_id),
            run_id=run.id,
            tool_outputs=tool_outputs
        )

        self.set_idle(chat_id)
        return self.handle_run(chat_id, tool_run)

    def get_relevant_people(self, parameters: dict) -> str:
        department = parameters["department"] if "department" in parameters else None
        position = parameters["position"] if "position" in parameters else None
        responsibility = parameters["responsibility"] if "responsibility" in parameters else None
        program = parameters["program"] if "program" in parameters else None

        print(parameters)

        df = self.df
        if department:
            df = df[df["department"] == department]
        if position:
            df = df[df["position"] == position]
        if responsibility:
            df = df[df["responsibilities"].str.contains(responsibility)]
        if program:
            df = df[df["programs"].dropna().str.contains(program)]

        relevant_people = map(lambda row: f"- Name: {row["name"]}, Email: {row['email']}, Phone: {row['phone']}, Responsibility: {row['description']}", df)
        print(relevant_people)

        return "Relevant people:\n- " + "\n- ".join(relevant_people)

    def set_idle(self, chat_id: int):
        thread = self.client.beta.threads.create()
        self.states[chat_id] = {"status": Assistant.Status.Idle, "thread": thread.id}

    def get_status(self, chat_id: int) -> "Assistant.Status":
        return self.states[chat_id]["status"]

    def get_thread(self, chat_id: int) -> str:
        return self.states[chat_id]["thread"]

    class Status(Enum):
        Idle = 0
        Clarification = 1
        Processing = 2


class AssistantStatus(TypedDict):
    status: Assistant.Status
    thread: str
