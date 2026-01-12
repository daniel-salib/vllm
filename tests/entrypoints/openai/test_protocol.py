# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright contributors to the vLLM project
from openai_harmony import (
    Message,
)

from vllm.entrypoints.openai.protocol import (
    ResponsesRequest,
    serialize_message,
    serialize_messages,
)


def test_serialize_message() -> None:
    dict_value = {"a": 1, "b": "2"}
    assert serialize_message(dict_value) == dict_value

    msg_value = {
        "role": "assistant",
        "name": None,
        "content": [{"type": "text", "text": "Test 1"}],
        "channel": "analysis",
    }
    msg = Message.from_dict(msg_value)
    assert serialize_message(msg) == msg_value


def test_serialize_messages() -> None:
    assert serialize_messages(None) is None
    assert serialize_messages([]) is None

    dict_value = {"a": 3, "b": "4"}
    msg_value = {
        "role": "assistant",
        "name": None,
        "content": [{"type": "text", "text": "Test 2"}],
        "channel": "analysis",
    }
    msg = Message.from_dict(msg_value)
    assert serialize_messages([msg, dict_value]) == [msg_value, dict_value]


class TestResponsesRequestInputNormalization:
    """Tests for ResponsesRequest input normalization.

    These tests verify the function_call_parsing validator correctly
    normalizes input items from clients with different serialization styles.
    """

    def test_strips_none_values_from_input_items(self):
        """Test that None values are stripped from input items.

        Clients may include None for optional fields with different
        serialization configs. These should be stripped to avoid validation
        errors and ensure consistent processing.
        """
        input_data = {
            "model": "test-model",
            "input": [
                {
                    "type": "message",
                    "role": "user",
                    "content": "Hello",
                    "name": None,  # Should be stripped
                    "status": None,  # Should be stripped
                }
            ],
        }

        validated = ResponsesRequest.function_call_parsing(input_data)
        processed_item = validated["input"][0]

        assert "name" not in processed_item
        assert "status" not in processed_item
        assert processed_item["content"] == "Hello"

    def test_handles_string_content_unchanged(self):
        """Test that string content is preserved without modification.

        Messages with simple string content (not array) should pass through
        unchanged.
        """
        input_data = {
            "model": "test-model",
            "input": [
                {
                    "type": "message",
                    "role": "user",
                    "content": "Simple string message",
                }
            ],
        }

        validated = ResponsesRequest.function_call_parsing(input_data)
        processed_item = validated["input"][0]

        assert processed_item["content"] == "Simple string message"


class TestOutputTextToInputTextConversion:
    """Tests for output_text to input_text conversion in multi-turn conversations.

    When clients echo back previous assistant messages as input for multi-turn
    conversations, the content types need to be converted from output format
    (output_text) to input format (input_text) to match the expected schema.
    """

    def test_converts_output_text_to_input_text(self):
        """Test that output_text content types are converted to input_text.

        This is critical for multi-turn conversations where clients send back
        the previous assistant response as part of the conversation history.
        """
        input_data = {
            "model": "test-model",
            "input": [
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [
                        {"type": "output_text", "text": "Hello!"},
                        {"type": "output_text", "text": "How can I help?"},
                    ],
                }
            ],
        }

        validated = ResponsesRequest.function_call_parsing(input_data)
        processed_item = validated["input"][0]

        # output_text should be converted to input_text
        assert processed_item["content"][0]["type"] == "input_text"
        assert processed_item["content"][1]["type"] == "input_text"
        # Text content should be preserved
        assert processed_item["content"][0]["text"] == "Hello!"
        assert processed_item["content"][1]["text"] == "How can I help?"

    def test_preserves_input_text_unchanged(self):
        """Test that input_text content types are not modified.

        Content that is already in input_text format should pass through
        unchanged.
        """
        input_data = {
            "model": "test-model",
            "input": [
                {
                    "type": "message",
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "Question here"},
                    ],
                }
            ],
        }

        validated = ResponsesRequest.function_call_parsing(input_data)
        processed_item = validated["input"][0]

        assert processed_item["content"][0]["type"] == "input_text"
        assert processed_item["content"][0]["text"] == "Question here"

    def test_handles_mixed_content_types(self):
        """Test that mixed content types are handled correctly.

        Only output_text should be converted; other content types should
        be preserved as-is.
        """
        input_data = {
            "model": "test-model",
            "input": [
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [
                        {"type": "output_text", "text": "Response text"},
                        {"type": "refusal", "refusal": "I cannot help with that"},
                    ],
                }
            ],
        }

        validated = ResponsesRequest.function_call_parsing(input_data)
        processed_item = validated["input"][0]

        # output_text converted to input_text
        assert processed_item["content"][0]["type"] == "input_text"
        # refusal preserved as-is
        assert processed_item["content"][1]["type"] == "refusal"

    def test_string_content_not_affected(self):
        """Test that string content (non-array) is not affected by conversion."""
        input_data = {
            "model": "test-model",
            "input": [
                {
                    "type": "message",
                    "role": "assistant",
                    "content": "Simple string response",
                }
            ],
        }

        validated = ResponsesRequest.function_call_parsing(input_data)
        processed_item = validated["input"][0]

        # String content should pass through unchanged
        assert processed_item["content"] == "Simple string response"
