from acme_policy_copilot.database.connection import Base, engine
from acme_policy_copilot.database.models import (
    User,
    Conversation,
    Message,
)

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()
