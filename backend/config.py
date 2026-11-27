import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./caseflow.db")
SESSION_HOURS = 8
