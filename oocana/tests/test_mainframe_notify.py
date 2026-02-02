import unittest
from unittest.mock import MagicMock, patch, PropertyMock
import threading
import time
from oocana import Mainframe


class MockMessage:
    """Mock MQTT message for testing."""
    def __init__(self, payload: bytes):
        self.payload = payload


class TestNotifyBlockReady(unittest.TestCase):
    """Test cases for Mainframe.notify_block_ready method."""

    def setUp(self):
        # Patch the mqtt client to avoid real network connections
        self.mock_client_patcher = patch('paho.mqtt.client.Client')
        self.mock_client_class = self.mock_client_patcher.start()
        self.mock_client = MagicMock()
        self.mock_client_class.return_value = self.mock_client
        self.mock_client.is_connected.return_value = True

        self.mainframe = Mainframe('mqtt://localhost:1883')
        self.mainframe.client = self.mock_client

    def tearDown(self):
        self.mock_client_patcher.stop()

    def test_notify_block_ready_receives_response(self):
        """Test that notify_block_ready correctly waits for and returns response."""
        session_id = 'test-session'
        job_id = 'test-job'
        expected_payload = {'inputs': {'key': 'value'}}

        # Simulate message callback being triggered
        def trigger_callback(*args, **kwargs):
            # Get the callback that was registered
            callback = self.mock_client.message_callback_add.call_args[0][1]
            # Create a mock message
            import simplejson
            mock_message = MockMessage(simplejson.dumps(expected_payload).encode())
            # Trigger the callback in a separate thread
            callback(None, None, mock_message)

        # Make subscribe trigger the callback after a short delay
        def delayed_trigger(*args, **kwargs):
            timer = threading.Timer(0.1, trigger_callback)
            timer.start()

        self.mock_client.publish.side_effect = delayed_trigger

        result = self.mainframe.notify_block_ready(session_id, job_id, timeout=5.0)

        self.assertEqual(result, expected_payload)
        self.mock_client.subscribe.assert_called_once()
        self.mock_client.publish.assert_called_once()

    def test_notify_block_ready_timeout(self):
        """Test that notify_block_ready raises TimeoutError on timeout."""
        session_id = 'test-session'
        job_id = 'test-job'

        # Don't trigger any callback, let it timeout
        with self.assertRaises(TimeoutError) as context:
            self.mainframe.notify_block_ready(session_id, job_id, timeout=0.1)

        self.assertIn(session_id, str(context.exception))
        self.assertIn(job_id, str(context.exception))
        # Verify cleanup was called
        self.mock_client.unsubscribe.assert_called()
        self.mock_client.message_callback_remove.assert_called()

    def test_notify_block_ready_unsubscribes_on_success(self):
        """Test that the topic is unsubscribed after successful message receipt."""
        session_id = 'test-session'
        job_id = 'test-job'
        expected_topic = f"inputs/{session_id}/{job_id}"

        def trigger_callback(*args, **kwargs):
            callback = self.mock_client.message_callback_add.call_args[0][1]
            import simplejson
            mock_message = MockMessage(simplejson.dumps({}).encode())
            callback(None, None, mock_message)

        self.mock_client.publish.side_effect = trigger_callback

        self.mainframe.notify_block_ready(session_id, job_id, timeout=5.0)

        # Verify unsubscribe was called with the correct topic
        self.mock_client.unsubscribe.assert_called_with(expected_topic)

    def test_notify_block_ready_publishes_correct_message(self):
        """Test that the correct BlockReady message is published."""
        session_id = 'test-session'
        job_id = 'test-job'

        def trigger_callback(*args, **kwargs):
            callback = self.mock_client.message_callback_add.call_args[0][1]
            import simplejson
            mock_message = MockMessage(simplejson.dumps({}).encode())
            callback(None, None, mock_message)

        self.mock_client.publish.side_effect = trigger_callback

        self.mainframe.notify_block_ready(session_id, job_id, timeout=5.0)

        # Check that publish was called with correct topic and payload
        publish_call = self.mock_client.publish.call_args
        self.assertEqual(publish_call[0][0], f"session/{session_id}")

        import simplejson
        payload = simplejson.loads(publish_call[0][1])
        self.assertEqual(payload['type'], 'BlockReady')
        self.assertEqual(payload['session_id'], session_id)
        self.assertEqual(payload['job_id'], job_id)

    def test_notify_block_ready_no_cpu_spin(self):
        """Test that notify_block_ready does not spin CPU while waiting."""
        session_id = 'test-session'
        job_id = 'test-job'

        start_time = time.time()

        # Use a short timeout to verify it actually waits
        try:
            self.mainframe.notify_block_ready(session_id, job_id, timeout=0.2)
        except TimeoutError:
            pass

        elapsed_time = time.time() - start_time

        # If it was busy-waiting, it would return almost immediately
        # With Event.wait(), it should wait close to the timeout
        self.assertGreaterEqual(elapsed_time, 0.15)


if __name__ == '__main__':
    unittest.main()
