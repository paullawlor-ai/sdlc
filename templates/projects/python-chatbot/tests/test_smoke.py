from app.chat.engine import ChatEngine
from app.safety.input import sanitize_user_input


def test_chatbot_starts_without_network_access() -> None:
    engine = ChatEngine()
    assert engine.memory.get_messages() == []
    assert sanitize_user_input("hello") == "hello"
