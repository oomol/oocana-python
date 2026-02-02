import unittest
from unittest.mock import Mock, MagicMock, patch


class TestMainframeCallbacks(unittest.TestCase):
    """Test Mainframe callback management methods."""

    def setUp(self):
        """Create a Mainframe instance with mocked MQTT client."""
        from oocana import Mainframe

        self.mainframe = Mainframe("mqtt://localhost:1883")

        # Manually set up mock client without calling connect()
        self.mock_mqtt_client = MagicMock()
        self.mock_mqtt_client.is_connected.return_value = True
        self.mainframe.client = self.mock_mqtt_client

    def test_add_report_callback_adds_callable(self):
        """Test add_report_callback adds a callable function."""
        callback = Mock()
        self.mainframe.add_report_callback(callback)

        # Internal check - callback should be in the set
        self.assertIn(callback, self.mainframe._Mainframe__report_callbacks)

    def test_add_report_callback_rejects_non_callable(self):
        """Test add_report_callback raises ValueError for non-callable."""
        with self.assertRaises(ValueError):
            self.mainframe.add_report_callback("not a function")

    def test_remove_report_callback_removes_existing(self):
        """Test remove_report_callback removes existing callback."""
        callback = Mock()
        self.mainframe.add_report_callback(callback)
        self.mainframe.remove_report_callback(callback)

        self.assertNotIn(callback, self.mainframe._Mainframe__report_callbacks)

    def test_remove_report_callback_logs_warning_for_missing(self):
        """Test remove_report_callback logs warning for non-existent callback."""
        callback = Mock()
        # Should not raise, just log warning
        self.mainframe.remove_report_callback(callback)

    def test_add_session_callback_adds_callable(self):
        """Test add_session_callback adds a callable function."""
        callback = Mock()
        session_id = "test_session"
        self.mainframe.add_session_callback(session_id, callback)

        self.assertIn(session_id, self.mainframe._Mainframe__session_callbacks)
        self.assertIn(callback, self.mainframe._Mainframe__session_callbacks[session_id])

    def test_add_session_callback_rejects_non_callable(self):
        """Test add_session_callback raises ValueError for non-callable."""
        with self.assertRaises(ValueError):
            self.mainframe.add_session_callback("session", "not a function")

    def test_add_session_callback_subscribes_once(self):
        """Test add_session_callback only subscribes once for same session."""
        callback1 = Mock()
        callback2 = Mock()
        session_id = "test_session"

        self.mainframe.add_session_callback(session_id, callback1)
        subscribe_count = self.mock_mqtt_client.message_callback_add.call_count

        self.mainframe.add_session_callback(session_id, callback2)
        # Should not subscribe again
        self.assertEqual(self.mock_mqtt_client.message_callback_add.call_count, subscribe_count)

    def test_remove_session_callback_removes_existing(self):
        """Test remove_session_callback removes existing callback."""
        callback = Mock()
        session_id = "test_session"
        self.mainframe.add_session_callback(session_id, callback)
        self.mainframe.remove_session_callback(session_id, callback)

        # After removing last callback, session_id should be removed from dict
        self.assertNotIn(session_id, self.mainframe._Mainframe__session_callbacks)

    def test_remove_session_callback_unsubscribes_on_last(self):
        """Test remove_session_callback unsubscribes when last callback removed."""
        callback = Mock()
        session_id = "test_session"
        self.mainframe.add_session_callback(session_id, callback)

        # Reset mock to track unsubscribe call
        self.mock_mqtt_client.reset_mock()

        self.mainframe.remove_session_callback(session_id, callback)
        self.mock_mqtt_client.unsubscribe.assert_called_once()

    def test_add_request_response_callback_adds_callable(self):
        """Test add_request_response_callback adds a callable function."""
        callback = Mock()
        session_id = "test_session"
        request_id = "test_request"
        self.mainframe.add_request_response_callback(session_id, request_id, callback)

        self.assertIn(request_id, self.mainframe._Mainframe__request_response_callbacks)
        self.assertIn(callback, self.mainframe._Mainframe__request_response_callbacks[request_id])

    def test_add_request_response_callback_rejects_non_callable(self):
        """Test add_request_response_callback raises ValueError for non-callable."""
        with self.assertRaises(ValueError):
            self.mainframe.add_request_response_callback("session", "request", "not a function")

    def test_remove_request_response_callback_removes_existing(self):
        """Test remove_request_response_callback removes existing callback."""
        callback = Mock()
        session_id = "test_session"
        request_id = "test_request"
        self.mainframe.add_request_response_callback(session_id, request_id, callback)
        self.mainframe.remove_request_response_callback(session_id, request_id, callback)

        # After removing last callback, request_id should be removed
        self.assertNotIn(request_id, self.mainframe._Mainframe__request_response_callbacks)

    def test_remove_request_response_callback_unsubscribes_on_last(self):
        """Test remove_request_response_callback unsubscribes when last callback removed."""
        callback = Mock()
        session_id = "test_session"
        request_id = "test_request"
        self.mainframe.add_request_response_callback(session_id, request_id, callback)

        self.mock_mqtt_client.reset_mock()

        self.mainframe.remove_request_response_callback(session_id, request_id, callback)
        self.mock_mqtt_client.unsubscribe.assert_called_once()

    def test_multiple_callbacks_same_session(self):
        """Test multiple callbacks can be added for same session."""
        callback1 = Mock()
        callback2 = Mock()
        session_id = "test_session"

        self.mainframe.add_session_callback(session_id, callback1)
        self.mainframe.add_session_callback(session_id, callback2)

        self.assertEqual(len(self.mainframe._Mainframe__session_callbacks[session_id]), 2)

    def test_remove_one_callback_keeps_others(self):
        """Test removing one callback keeps other callbacks intact."""
        callback1 = Mock()
        callback2 = Mock()
        session_id = "test_session"

        self.mainframe.add_session_callback(session_id, callback1)
        self.mainframe.add_session_callback(session_id, callback2)
        self.mainframe.remove_session_callback(session_id, callback1)

        self.assertIn(callback2, self.mainframe._Mainframe__session_callbacks[session_id])
        self.assertNotIn(callback1, self.mainframe._Mainframe__session_callbacks[session_id])


if __name__ == "__main__":
    unittest.main()
