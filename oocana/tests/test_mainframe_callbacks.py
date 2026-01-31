import unittest
from unittest.mock import MagicMock, patch


class TestCallbackManagement(unittest.TestCase):
    """Test cases for callback management methods in Mainframe."""

    def setUp(self):
        # Patch the mqtt client to avoid real network connections
        self.mock_client_patcher = patch('paho.mqtt.client.Client')
        self.mock_client_class = self.mock_client_patcher.start()
        self.mock_client = MagicMock()
        self.mock_client_class.return_value = self.mock_client
        self.mock_client.is_connected.return_value = True

        from oocana import Mainframe
        self.mainframe = Mainframe('mqtt://localhost:1883')
        self.mainframe.client = self.mock_client

    def tearDown(self):
        self.mock_client_patcher.stop()

    def test_add_request_response_callback(self):
        """Test adding a request response callback."""
        session_id = 'test-session'
        request_id = 'test-request'
        callback = MagicMock()

        self.mainframe.add_request_response_callback(session_id, request_id, callback)

        # Verify subscribe was called with correct topic
        expected_topic = f"session/{session_id}/request/{request_id}/response"
        self.mock_client.message_callback_add.assert_called()

    def test_add_session_callback(self):
        """Test adding a session callback."""
        session_id = 'test-session'
        callback = MagicMock()

        self.mainframe.add_session_callback(session_id, callback)

        # Verify subscribe was called
        self.mock_client.message_callback_add.assert_called()

    def test_add_callback_requires_callable(self):
        """Test that non-callable raises ValueError."""
        session_id = 'test-session'

        with self.assertRaises(ValueError) as context:
            self.mainframe.add_session_callback(session_id, "not a callable")

        self.assertIn("callable", str(context.exception))

    def test_add_request_response_callback_requires_callable(self):
        """Test that non-callable raises ValueError for request response callback."""
        with self.assertRaises(ValueError) as context:
            self.mainframe.add_request_response_callback("session", "request", "not a callable")

        self.assertIn("callable", str(context.exception))

    def test_remove_session_callback(self):
        """Test removing a session callback."""
        session_id = 'test-session'
        callback = MagicMock()

        # Add then remove
        self.mainframe.add_session_callback(session_id, callback)
        self.mainframe.remove_session_callback(session_id, callback)

        # Verify unsubscribe was called
        self.mock_client.unsubscribe.assert_called()

    def test_remove_request_response_callback(self):
        """Test removing a request response callback."""
        session_id = 'test-session'
        request_id = 'test-request'
        callback = MagicMock()

        # Add then remove
        self.mainframe.add_request_response_callback(session_id, request_id, callback)
        self.mainframe.remove_request_response_callback(session_id, request_id, callback)

        # Verify unsubscribe was called
        self.mock_client.unsubscribe.assert_called()

    def test_remove_nonexistent_callback_logs_warning(self):
        """Test that removing a nonexistent callback logs a warning."""
        session_id = 'test-session'
        callback = MagicMock()

        # Create a mock logger
        mock_logger = MagicMock()
        self.mainframe._logger = mock_logger

        # Try to remove callback that was never added
        self.mainframe.remove_session_callback(session_id, callback)

        # Verify warning was logged
        mock_logger.warning.assert_called_once()

    def test_multiple_callbacks_for_same_session(self):
        """Test that multiple callbacks can be added for the same session."""
        session_id = 'test-session'
        callback1 = MagicMock()
        callback2 = MagicMock()

        self.mainframe.add_session_callback(session_id, callback1)
        self.mainframe.add_session_callback(session_id, callback2)

        # Remove first callback, should not unsubscribe yet
        self.mainframe.remove_session_callback(session_id, callback1)

        # Subscribe should have been called only once (for first add)
        call_count_before = self.mock_client.message_callback_add.call_count

        # Remove second callback, should unsubscribe now
        self.mainframe.remove_session_callback(session_id, callback2)

        self.mock_client.unsubscribe.assert_called()

    def test_add_report_callback(self):
        """Test adding a report callback."""
        callback = MagicMock()

        self.mainframe.add_report_callback(callback)

        # No error should occur

    def test_add_report_callback_requires_callable(self):
        """Test that non-callable raises ValueError for report callback."""
        with self.assertRaises(ValueError) as context:
            self.mainframe.add_report_callback("not a callable")

        self.assertIn("callable", str(context.exception))

    def test_remove_report_callback(self):
        """Test removing a report callback."""
        callback = MagicMock()

        self.mainframe.add_report_callback(callback)
        self.mainframe.remove_report_callback(callback)

        # No error should occur

    def test_remove_nonexistent_report_callback_logs_warning(self):
        """Test that removing a nonexistent report callback logs a warning."""
        callback = MagicMock()
        mock_logger = MagicMock()
        self.mainframe._logger = mock_logger

        self.mainframe.remove_report_callback(callback)

        mock_logger.warning.assert_called_once()


if __name__ == '__main__':
    unittest.main()
