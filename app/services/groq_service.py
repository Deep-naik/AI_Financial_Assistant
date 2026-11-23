
from groq import Groq

from app.config import settings


class GroqService:

    def __init__(self):

        self.client = Groq(
            api_key=settings.GROQ_API_KEY
        )

        self.model = settings.GROQ_MODEL

    def generate_response(
        self,
        user_message: str,
        system_message: str = (
            "You are an expert financial business "
            "intelligence assistant. Provide clear, "
            "accurate and evidence-based answers."
        )
    ):

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            temperature=0.3,
            max_completion_tokens=1500
        )

        return response.choices[0].message.content
