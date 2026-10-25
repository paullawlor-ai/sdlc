"""Conversation memory management."""

from dataclasses import dataclass, field


@dataclass
class ConversationMemory:
    """Manages conversation history with a sliding window."""

    max_turns: int = 10
    messages: list[dict] = field(default_factory=list)

    def add_user_message(self, content: str) -> None:
        """Add a user message to history."""
        self.messages.append({"role": "user", "content": content})
        self._trim()

    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to history."""
        self.messages.append({"role": "assistant", "content": content})
        self._trim()

    def get_messages(self) -> list[dict]:
        """Get all messages in history."""
        return self.messages.copy()

    def clear(self) -> None:
        """Clear all messages."""
        self.messages = []

    def _trim(self) -> None:
        """Trim history to max_turns (pairs of messages)."""
        max_messages = self.max_turns * 2
        if len(self.messages) > max_messages:
            self.messages = self.messages[-max_messages:]
