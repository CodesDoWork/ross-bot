from openai import OpenAI


class Assistant:

    def __init__(self):
        self.client = OpenAI()

    def process_request(self, chat_id: int, request: str) -> str:
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
