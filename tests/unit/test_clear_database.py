"""
Unit tests for database clearing utility in app.utils.clear_database.
"""
import pytest
from unittest.mock import patch, MagicMock
from app.utils.clear_database import clear_database

def test_clear_database_success():
    """Test that clear_database executes all steps without error."""
    with patch('app.utils.clear_database.engine') as mock_engine:
        mock_conn = MagicMock()
        mock_engine.begin.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = [("table1",), ("table2",)]
        clear_database()
        assert mock_conn.execute.call_count >= 4  # disables, gets tables, truncates, reenables


def test_clear_database_exception():
    """Test that clear_database raises on error."""
    with patch('app.utils.clear_database.engine') as mock_engine:
        mock_conn = MagicMock()
        mock_engine.begin.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.side_effect = Exception("fail")
        with pytest.raises(Exception):
            clear_database() 