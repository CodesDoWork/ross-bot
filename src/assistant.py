import json
from pandas import DataFrame
from enum import Enum
from telebot.types import User
from openai import OpenAI
from openai.types.beta.threads.run import Run
from typing import TypedDict, Literal
from src.assistant_config import instruction, model, tools


class Assistant:

    def __init__(self, df: DataFrame):
        """
        Initializes the Assistant with the provided DataFrame and configures it with the OpenAI API client.

        :param df: A pandas DataFrame containing employee contact data.
        """
        self.client = OpenAI()
        self.assistant = self.client.beta.assistants.create(instructions=instruction, model=model, tools=tools)
        self.states: dict[int, AssistantStatus] = {}
        self.df = df

    def greet_user(self, chat_id: int, user: User) -> str:
        """
        Greets the user in their preferred language based on their user profile.

        :param chat_id: Telegram chat ID for the user.
        :param user: The Telegram User object.
        :return: A greeting message.
        """
        self.set_idle(chat_id)
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=self.get_thread(chat_id),
            assistant_id=self.assistant.id,
            instructions=f"Greet the user '{self.get_name(user)}'. It is important to use the language '{user.language_code}' for the greeting."
        )
        return self.handle_run(chat_id, run)

    def get_name(self, user: User) -> str:
        """
        Retrieves the name of the user, prioritizing full name, first name + last name, or username.

        :param user: The Telegram User object.
        :return: The user's name as a string.
        """
        if user.full_name:
            return user.full_name
        if user.first_name:
            name = user.first_name
            if user.last_name:
                name += " " + user.last_name
            return name
        return user.username

    def process_request(self, chat_id: int, request: str) -> str:
        """
        Processes a user's text request and decides whether to clarify or start processing based on the current state.

        :param chat_id: The user's chat ID.
        :param request: The user's message or request.
        :return: A response from the assistant.
        """
        if chat_id not in self.states:
            self.set_idle(chat_id)

        status = self.get_status(chat_id)
        if status == Assistant.Status.Processing:
            return self.process_clarification(chat_id, request)
        else:
            return self.process_idle(chat_id, request)

    def process_idle(self, chat_id: int, request: str) -> str:
        """
        Processes a user's request when the assistant is in an idle state.

        :param chat_id: The user's chat ID.
        :param request: The user's message or request.
        :return: The clarification response from the assistant.
        """
        self.states[chat_id]["status"] = Assistant.Status.Processing
        return self.process_clarification(chat_id, request)

    def process_clarification(self, chat_id: int, request: str) -> str:
        """
        Clarifies the user's request by adding the message to the conversation thread.

        :param chat_id: The user's chat ID.
        :param request: The user's message or request.
        :return: The response from the assistant.
        """
        self.add_message(chat_id, "user", request)
        return self.answer(chat_id)

    def add_message(self, chat_id: int, role: Literal["user", "assistant"], message: str):
        """
        Adds a message to the thread with a specific role (user or assistant).

        :param chat_id: The user's chat ID.
        :param role: Either "user" or "assistant" depending on who sends the message.
        :param message: The content of the message.
        """
        self.client.beta.threads.messages.create(
            thread_id=self.get_thread(chat_id),
            role=role,
            content=message,
        )

    def answer(self, chat_id: int) -> str:
        """
        Generates and returns an answer from the assistant.

        :param chat_id: The user's chat ID.
        :return: The assistant's response.
        """
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=self.get_thread(chat_id),
            assistant_id=self.assistant.id,
        )
        return self.handle_run(chat_id, run)

    def handle_run(self, chat_id: int, run: Run) -> str:
        """
        Handles the run result and returns the response from the assistant.

        :param chat_id: The user's chat ID.
        :param run: The result of the assistant's run.
        :return: The assistant's response.
        """
        if run.status == "completed":
            return self.client.beta.threads.messages.list(thread_id=self.get_thread(chat_id)).data[0].content[0].text.value
        return self.add_function_outputs(chat_id, run)

    def add_function_outputs(self, chat_id: int, run: Run) -> str:
        """
        Processes and adds the function outputs (such as retrieving relevant people).

        :param chat_id: The user's chat ID.
        :param run: The result of the assistant's run.
        :return: The assistant's response including tool outputs.
        """
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

        return self.handle_run(chat_id, tool_run)

    def get_relevant_people(self, parameters: dict) -> str:
        """
        Finds and returns relevant people based on the provided filters like department, position, responsibility, etc.

        :param parameters: A dictionary of filter parameters for finding relevant people.
        :return: A string listing the relevant people or a request for more details if too many results are found.
        """
        department = parameters["department"] if "department" in parameters else None
        position = parameters["position"] if "position" in parameters else None
        responsibility = parameters["responsibility"] if "responsibility" in parameters else None
        program = parameters["program"] if "program" in parameters else None
        location = parameters["location"] if "location" in parameters else None

        df = self.df.copy()
        # Apply department filter
        if department:
            filtered_df = df[df["department"] == department]
            if not filtered_df.empty:
                df = filtered_df

        # Apply position filter
        if position:
            filtered_df = df[df["position"] == position]
            if not filtered_df.empty:
                df = filtered_df

        # Apply responsibility filter
        if responsibility:
            filtered_df = df[df["responsibilities"].str.contains(responsibility)]
            if not filtered_df.empty:
                df = filtered_df

        # Apply program filter
        if program:
            filtered_df = df[df["programs"].dropna().str.contains(program)]
            if not filtered_df.empty:
                df = filtered_df

        # Apply location filter
        if location:
            filtered_df = df[df["location"] == location]
            if not filtered_df.empty:
                df = filtered_df

        relevant_people = list(map(lambda row: f"Name: {row['name']}, Email: {row['email']}, Phone: {row['phone']}, Responsibility: {row['description']}", df.iloc))
        if len(relevant_people) > 3:
            return "Please provide more information."

        return "Relevant people:\n- " + "\n- ".join(relevant_people)

    def ask_for_feedback(self, chat_id: int) -> str:
        """
        Asks the user for feedback on whether they are satisfied with the assistant's response.

        :param chat_id: The user's chat ID.
        :return: The assistant's feedback request message.
        """
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=self.get_thread(chat_id),
            assistant_id=self.assistant.id,
            instructions="Ask if the user is satisfied with your response. He should be able to answer with yes if he is satisfied and no if he is not."
        )
        return self.handle_run(chat_id, run)

    def positive_feedback(self, chat_id: int) -> str:
        """
        Handles positive feedback by thanking the user and setting the assistant's state to idle.

        :param chat_id: The user's chat ID.
        :return: The assistant's response to positive feedback.
        """
        self.set_idle(chat_id)
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=self.get_thread(chat_id),
            assistant_id=self.assistant.id,
            instructions="The user is satisfied. Say goodbye and thank them."
        )
        return self.handle_run(chat_id, run)

    def negative_feedback(self, chat_id: int) -> str:
        """
        Handles negative feedback by apologizing and asking for clarification to improve the response.

        :param chat_id: The user's chat ID.
        :return: The assistant's response to negative feedback.
        """
        self.set_processing(chat_id)
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=self.get_thread(chat_id),
            assistant_id=self.assistant.id,
            instructions="The user is unsatisfied. Be sorry. Think about how to improve and ask for clarification."
        )
        return self.handle_run(chat_id, run)

    def set_idle(self, chat_id: int):
        """
        Sets the assistant's state to idle for the specified chat ID.

        :param chat_id: The user's chat ID.
        """
        thread = self.client.beta.threads.create()
        self.states[chat_id] = {"status": Assistant.Status.Idle, "thread": thread.id}

    def set_processing(self, chat_id: int):
        """
        Sets the assistant's state to processing for the specified chat ID.

        :param chat_id: The user's chat ID.
        """
        self.states[chat_id]["status"] = Assistant.Status.Processing

    def set_feedback(self, chat_id: int):
        """
        Sets the assistant's state to feedback for the specified chat ID.

        :param chat_id: The user's chat ID.
        """
        self.states[chat_id]["status"] = Assistant.Status.Feedback

    def get_status(self, chat_id: int) -> "Assistant.Status":
        """
        Retrieves the current status of the assistant for the specified chat ID.

        :param chat_id: The user's chat ID.
        :return: The current status of the assistant.
        """
        return self.states[chat_id]["status"]

    def get_thread(self, chat_id: int) -> str:
        """
        Retrieves the thread ID associated with the specified chat ID.

        :param chat_id: The user's chat ID.
        :return: The thread ID for that chat.
        """
        return self.states[chat_id]["thread"]

    class Status(Enum):
        Idle = 0
        Processing = 1
        Feedback = 2


class AssistantStatus(TypedDict):
    status: Assistant.Status
    thread: str
