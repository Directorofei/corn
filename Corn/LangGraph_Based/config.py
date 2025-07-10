import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-chat")

DETECTION_CHATFLOW_ID = os.getenv("DETECTION_CHATFLOW_ID")
DETECTION_API_KEY = os.getenv("DETECTION_API_KEY")

QA_CHATFLOW_ID = os.getenv("QA_CHATFLOW_ID")
QA_API_KEY = os.getenv("QA_API_KEY")

DECISION_CHATFLOW_ID = os.getenv("DECISION_CHATFLOW_ID")
DECISION_API_KEY = os.getenv("DECISION_API_KEY")

