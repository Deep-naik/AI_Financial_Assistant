
from app.services.groq_service import GroqService


groq_service = GroqService()

question = """
What is profit margin?
Explain how a business can use it
to evaluate financial performance.
"""

response = groq_service.generate_response(question)

print("\nGROQ AI RESPONSE")
print("=" * 50)
print(response)
