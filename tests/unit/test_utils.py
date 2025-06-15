"""
Unit tests for utility functions in app.models (e.g., generate_slug).
"""
import pytest
from app.models import generate_slug

def test_generate_slug_basic():
    """Test basic slug generation"""
    assert generate_slug("Hello World") == "hello-world"
    assert generate_slug("Test Case") == "test-case"

def test_generate_slug_special_characters():
    """Test slug generation with special characters"""
    assert generate_slug("Hello! World@") == "hello-world"
    assert generate_slug("Test & Case") == "test-case"
    assert generate_slug("Test-Case") == "test-case"

def test_generate_slug_multiple_spaces():
    """Test slug generation with multiple spaces"""
    assert generate_slug("Hello   World") == "hello-world"
    assert generate_slug("Test    Case") == "test-case"

def test_generate_slug_leading_trailing_spaces():
    """Test slug generation with leading and trailing spaces"""
    assert generate_slug(" Hello World ") == "hello-world"
    assert generate_slug("  Test Case  ") == "test-case"

def test_generate_slug_multiple_hyphens():
    """Test slug generation with multiple hyphens"""
    assert generate_slug("Hello--World") == "hello-world"
    assert generate_slug("Test---Case") == "test-case"

def test_generate_slug_empty():
    """Test slug generation with empty string"""
    assert generate_slug("") == ""

def test_generate_slug_numbers():
    """Test slug generation with numbers"""
    assert generate_slug("Test 123") == "test-123"
    assert generate_slug("123 Test") == "123-test" 