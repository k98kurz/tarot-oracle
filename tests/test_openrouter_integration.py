"""Test OpenRouter provider integration with mocked API calls."""

import pytest
import json
from unittest.mock import patch, Mock
import requests

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tarot_oracle.oracle import OpenRouterClient
from tarot_oracle.exceptions import (
    AuthenticationError,
    NetworkError,
    RateLimitError,
    ProviderError
)


class TestOpenRouterClient:
    """Test OpenRouter client functionality."""
    
    def test_client_initialization(self):
        """Test basic client initialization."""
        api_key = "test-api-key"
        model = "z-ai/glm-4.5-air:free"
        
        client = OpenRouterClient(api_key=api_key, model=model)
        
        assert client.api_key == api_key
        assert client.model == model
        assert client.base_url == "https://openrouter.ai/api/v1"
    
    def test_client_initialization_default_model(self):
        """Test client initialization with default model."""
        api_key = "test-api-key"
        
        client = OpenRouterClient(api_key=api_key)
        
        assert client.api_key == api_key
        assert client.model == "z-ai/glm-4.5-air:free"
    
    @patch('tarot_oracle.oracle.requests.post')
    def test_successful_response(self, mock_post):
        """Test successful API response."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "This is a test interpretation of your tarot reading."
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        client = OpenRouterClient(api_key="test-key")
        result = client.generate_response("Interpret these cards: Ace of Cups")
        
        assert result == "This is a test interpretation of your tarot reading."
        mock_post.assert_called_once()
        
        # Verify request parameters
        call_args = mock_post.call_args
        assert "Authorization" in call_args[1]["headers"]
        assert call_args[1]["headers"]["Authorization"] == "Bearer test-key"
        assert call_args[1]["json"]["model"] == "z-ai/glm-4.5-air:free"
        assert call_args[1]["json"]["messages"][0]["content"] == "Interpret these cards: Ace of Cups"
    
    @patch('tarot_oracle.oracle.requests.post')
    def test_successful_response_with_model_override(self, mock_post):
        """Test successful response with model override."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Custom model response."
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        client = OpenRouterClient(api_key="test-key")
        result = client.generate_response("Test prompt", model="custom/model")
        
        assert result == "Custom model response."
        
        # Verify model override was used
        call_args = mock_post.call_args
        assert call_args[1]["json"]["model"] == "custom/model"
    
    @patch('tarot_oracle.oracle.requests.post')
    def test_authentication_error(self, mock_post):
        """Test authentication error handling."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response
        
        client = OpenRouterClient(api_key="invalid-key")
        
        with pytest.raises(AuthenticationError) as exc_info:
            client.generate_response("Test prompt")
        
        assert "Invalid OpenRouter API key" in str(exc_info.value)
        assert exc_info.value.context["provider"] == "openrouter"
    
    @patch('tarot_oracle.oracle.requests.post')
    def test_rate_limit_error(self, mock_post):
        """Test rate limit error handling."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "60"}
        mock_post.return_value = mock_response
        
        client = OpenRouterClient(api_key="test-key")
        
        with pytest.raises(RateLimitError) as exc_info:
            client.generate_response("Test prompt")
        
        assert "OpenRouter API rate limit exceeded" in str(exc_info.value)
        assert exc_info.value.context["provider"] == "openrouter"
        assert exc_info.value.context["retry_after"] == 60
        assert "60 seconds" in str(exc_info.value)
    
    @patch('tarot_oracle.oracle.requests.post')
    def test_rate_limit_error_without_retry_after(self, mock_post):
        """Test rate limit error without Retry-After header."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {}
        mock_post.return_value = mock_response
        
        client = OpenRouterClient(api_key="test-key")
        
        with pytest.raises(RateLimitError) as exc_info:
            client.generate_response("Test prompt")
        
        assert exc_info.value.context.get("retry_after") is None
    
    @patch('tarot_oracle.oracle.requests.post')
    def test_network_timeout_error(self, mock_post):
        """Test network timeout error handling."""
        mock_post.side_effect = requests.exceptions.Timeout("Request timed out")
        
        client = OpenRouterClient(api_key="test-key")
        
        with pytest.raises(NetworkError) as exc_info:
            client.generate_response("Test prompt", timeout=10)
        
        assert "OpenRouter API request timed out after 10 seconds" in str(exc_info.value)
        assert exc_info.value.context["provider"] == "openrouter"
        assert exc_info.value.context["timeout"] == 10
    
    @patch('tarot_oracle.oracle.requests.post')
    def test_network_connection_error(self, mock_post):
        """Test network connection error handling."""
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        client = OpenRouterClient(api_key="test-key")
        
        with pytest.raises(NetworkError) as exc_info:
            client.generate_response("Test prompt")
        
        assert "OpenRouter API request failed" in str(exc_info.value)
        assert exc_info.value.context["provider"] == "openrouter"
    
    @patch('tarot_oracle.oracle.requests.post')
    def test_invalid_response_format(self, mock_post):
        """Test handling of invalid response format."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"invalid": "format"}
        mock_post.return_value = mock_response
        
        client = OpenRouterClient(api_key="test-key")
        
        with pytest.raises(NetworkError) as exc_info:
            client.generate_response("Test prompt")
        
        assert "Invalid response format from OpenRouter" in str(exc_info.value)
        assert exc_info.value.context["provider"] == "openrouter"
    
    @patch('tarot_oracle.oracle.requests.post')
    def test_empty_response_content(self, mock_post):
        """Test handling of empty response content."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": ""
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        client = OpenRouterClient(api_key="test-key")
        result = client.generate_response("Test prompt")
        
        assert result is None
    
    @patch('tarot_oracle.oracle.requests.post')
    def test_none_response_content(self, mock_post):
        """Test handling of None response content."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": None
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        client = OpenRouterClient(api_key="test-key")
        result = client.generate_response("Test prompt")
        
        assert result is None
    
    @patch('tarot_oracle.oracle.requests.post')
    def test_unexpected_http_status(self, mock_post):
        """Test handling of unexpected HTTP status codes."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        mock_post.return_value = mock_response
        
        client = OpenRouterClient(api_key="test-key")
        
        with pytest.raises(NetworkError) as exc_info:
            client.generate_response("Test prompt")
        
        assert "OpenRouter API returned status 500" in str(exc_info.value)
        assert "Internal server error" in str(exc_info.value)
        assert exc_info.value.context["provider"] == "openrouter"
    
    @patch('tarot_oracle.oracle.requests.post')
    def test_request_headers(self, mock_post):
        """Test that correct headers are sent with requests."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}]
        }
        mock_post.return_value = mock_response
        
        client = OpenRouterClient(api_key="test-key", model="test-model")
        client.generate_response("Test prompt")
        
        call_args = mock_post.call_args
        headers = call_args[1]["headers"]
        
        assert headers["Authorization"] == "Bearer test-key"
        assert headers["Content-Type"] == "application/json"
        assert headers["HTTP-Referer"] == "https://github.com/tarot-oracle/tarot-oracle"
        assert headers["X-Title"] == "Tarot Oracle"
    
    @patch('tarot_oracle.oracle.requests.post')
    def test_request_payload_structure(self, mock_post):
        """Test that request payload has correct structure."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}]
        }
        mock_post.return_value = mock_response
        
        client = OpenRouterClient(api_key="test-key")
        client.generate_response("Test prompt", model="custom/model", timeout=45)
        
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        
        assert payload["model"] == "custom/model"
        assert payload["max_tokens"] == 2048
        assert payload["temperature"] == 0.7
        assert len(payload["messages"]) == 1
        assert payload["messages"][0]["role"] == "user"
        assert payload["messages"][0]["content"] == "Test prompt"
    
    @patch('tarot_oracle.oracle.requests.post')
    def test_custom_timeout_parameter(self, mock_post):
        """Test custom timeout parameter is passed through."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}]
        }
        mock_post.return_value = mock_response
        
        client = OpenRouterClient(api_key="test-key")
        client.generate_response("Test prompt", timeout=60)
        
        call_args = mock_post.call_args
        assert call_args[1]["timeout"] == 60


class TestOpenRouterIntegration:
    """Test OpenRouter integration scenarios."""
    
    @patch('tarot_oracle.oracle.requests.post')
    def test_tarot_interpretation_scenario(self, mock_post):
        """Test realistic tarot interpretation scenario."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": """The Ace of Cups in this position suggests new emotional beginnings and opportunities for emotional fulfillment. This card indicates that you are entering a period of heightened intuition and spiritual awareness. The overflowing cup symbolizes abundance of love and creative energy flowing into your life."""
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        client = OpenRouterClient(api_key="test-key")
        prompt = "Please interpret this tarot card: Ace of Cups in the position of 'Current Situation'"
        result = client.generate_response(prompt)
        
        assert result is not None
        assert "Ace of Cups" in result
        assert "emotional" in result.lower()
        mock_post.assert_called_once()
    
    @patch('tarot_oracle.oracle.requests.post')
    def test_multiple_card_reading_scenario(self, mock_post):
        """Test interpretation of multiple card reading."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": """This three-card reading reveals a journey of transformation. The Tower represents a sudden change or revelation that has occurred. The Star offers hope and healing in the present moment, guiding you toward your true purpose. The World signifies successful completion and achievement in your future path."""
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        client = OpenRouterClient(api_key="test-key")
        prompt = """
        Please interpret this three-card reading:
        Past: The Tower
        Present: The Star  
        Future: The World
        """
        result = client.generate_response(prompt)
        
        assert result is not None
        assert "Tower" in result
        assert "Star" in result
        assert "World" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])