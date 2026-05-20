"""Chat engine for conversational AI."""

import httpx

from app.chat.memory import ConversationMemory
from app.chat.prompts import build_messages
from app.config import settings
from app.safety.input import sanitize_user_input
from app.safety.output import validate_response
from app.utils.logging import get_logger

logger = get_logger(__name__)


class ChatEngine:
    """Conversational AI engine."""

    def __init__(self):
        """Initialize the chat engine."""
        self.memory = ConversationMemory(max_turns=settings.MAX_CONVERSATION_TURNS)
        self.rag = None

        if settings.RAG_ENABLED:
            from app.rag.retriever import Retriever
            self.rag = Retriever(settings.RAG_DOCUMENTS_PATH)

    async def chat(self, user_input: str) -> str:
        """
        Process user input and generate a response.

        Args:
            user_input: The user's message

        Returns:
            The assistant's response
        """
        # Sanitize input (A0 baseline)
        safe_input = sanitize_user_input(user_input)

        # Log the interaction (without sensitive content)
        logger.info("chat_request", input_length=len(safe_input))

        # Get RAG context if enabled
        context = None
        if self.rag:
            context = self.rag.get_relevant_context(safe_input)

        # Build messages with history
        messages = build_messages(
            system_prompt=settings.SYSTEM_PROMPT,
            user_message=safe_input,
            history=self.memory.get_messages(),
            context=context,
        )

        # Call LLM
        response = await self._call_llm(messages)

        # Validate output (A0 baseline)
        validated_response = validate_response(response)

        # Update memory
        self.memory.add_user_message(safe_input)
        self.memory.add_assistant_message(validated_response)

        logger.info("chat_response", response_length=len(validated_response))

        return validated_response

    async def _call_llm(self, messages: list[dict]) -> str:
        """Call the LLM API."""
        async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.LLM_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.LLM_MODEL,
                    "messages": messages,
                    "max_tokens": settings.LLM_MAX_TOKENS,
                    "temperature": settings.LLM_TEMPERATURE,
                },
            )
            response.raise_for_status()

            data = response.json()
            return data["choices"][0]["message"]["content"]

    def clear_history(self):
        """Clear conversation history."""
        self.memory.clear()
        logger.info("history_cleared")

