"""Prompt building utilities."""


def build_messages(
    system_prompt: str,
    user_message: str,
    history: list[dict] | None = None,
    context: str | None = None,
) -> list[dict]:
    """
    Build the messages array for the LLM.

    Args:
        system_prompt: The system prompt
        user_message: The current user message
        history: Previous conversation messages
        context: RAG context to include

    Returns:
        List of message dictionaries
    """
    messages = []

    # Build system prompt with context if provided
    full_system = system_prompt
    if context:
        full_system += f"\n\nRelevant context:\n{context}"

    messages.append({"role": "system", "content": full_system})

    # Add history
    if history:
        messages.extend(history)

    # Add current user message
    messages.append({"role": "user", "content": user_message})

    return messages

