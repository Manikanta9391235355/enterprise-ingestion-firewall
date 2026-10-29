
from backend.llm_service import classify_message
from backend.schemas import FirewallResult, TokenMetadata


async def process_message(message: str):
    classification, usage = await classify_message(message)

    input_tokens = (
        usage.prompt_tokens if usage else 0
    )
    output_tokens = (
        usage.completion_tokens if usage else 0
    )

    return FirewallResult(
        intent=classification.intent,
        risk=classification.risk,
        priority=classification.priority,
        tokens=TokenMetadata(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
        ),
    )
