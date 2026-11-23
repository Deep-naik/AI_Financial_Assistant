
from app.config import settings

print("Application:", settings.APP_NAME)
print("Debug:", settings.DEBUG)
print("Groq Model:", settings.GROQ_MODEL)
print("Database:", settings.DATABASE_URL)

# Never print the actual API key.
print(
    "Groq API Key Loaded:",
    bool(settings.GROQ_API_KEY)
)
