"""Provider block responses normalize once for every text creation plugin."""

import pytest
from open_notebook_creator_sdk.models import normalize_text_response
from pydantic import BaseModel


class AIMessage(BaseModel):
    content: str | list
    usage_metadata: dict | None = None


def test_normalizes_gemini_blocks_preserving_usage_without_mutation():
    original = AIMessage(
        content=[
            {
                "type": "text",
                "text": '{"ok":true}',
                "extras": {"signature": "private-signature"},
            }
        ],
        usage_metadata={"input_tokens": 12, "output_tokens": 3, "total_tokens": 15},
    )
    normalized = normalize_text_response(original)
    assert normalized.content == '{"ok":true}'
    assert normalized.usage_metadata == original.usage_metadata
    assert isinstance(original.content, list)
    assert "signature" not in normalized.content


def test_excludes_reasoning_and_nontext_blocks():
    message = AIMessage(
        content=[
            {"type": "text", "text": "hidden", "thought": True},
            {"type": "reasoning", "reasoning": "private"},
            {"type": "text", "text": "answer"},
        ]
    )
    assert normalize_text_response(message).content == "answer"


@pytest.mark.parametrize("content", ["plain text", '{"cards":[]}'])
def test_plain_text_is_unchanged(content):
    message = AIMessage(content=content)
    assert normalize_text_response(message) is message


@pytest.mark.parametrize(
    "content",
    [
        [],
        [{"type": "reasoning", "reasoning": "private"}],
        [{"type": "text", "text": "   "}],
    ],
)
def test_empty_or_thought_only_output_fails(content):
    with pytest.raises(ValueError, match="no usable text"):
        normalize_text_response(AIMessage(content=content))
