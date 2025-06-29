"""
Unit tests for database clearing utility in app.utils.reset_database.
"""
import pytest
from unittest.mock import MagicMock, patch
from app.utils.reset_database import reset_database
from app.models.base import Base

@patch('app.utils.reset_database.SessionLocal')
@patch('app.utils.reset_database.Base.metadata')
def test_reset_database_success(mock_metadata, mock_session_local):
    """Test that reset_database performs all steps: drop, create, and add admin."""
    
    # Configure mocks
    mock_db = MagicMock()
    mock_session_local.return_value = mock_db

    # Call the function
    reset_database()

    # Assert that the correct methods were called
    mock_metadata.drop_all.assert_called_once()
    mock_metadata.create_all.assert_called_once()
    mock_session_local.assert_called_once()
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.close.assert_called_once()
    mock_db.rollback.assert_not_called()

@patch('app.utils.reset_database.Base.metadata')
def test_reset_database_exception_on_create(mock_metadata):
    """Test that reset_database handles exceptions during table creation."""
    mock_metadata.create_all.side_effect = Exception("DB creation failed")

    with pytest.raises(Exception, match="DB creation failed"):
        reset_database()
    
    mock_metadata.drop_all.assert_called_once()
    mock_metadata.create_all.assert_called_once()

# We no longer need the old test for clear_database, so I'm replacing it.
# If we wanted to keep both, we would need to adjust the file. 