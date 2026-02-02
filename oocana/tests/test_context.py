import unittest
from unittest.mock import Mock
import tempfile
import os


class TestContext(unittest.TestCase):
    """Test Context class methods."""

    def setUp(self):
        """Create a Context instance with mocked dependencies."""
        from oocana import BlockInfo

        self.mock_mainframe = Mock()
        self.mock_store = {}
        self.block_info = BlockInfo(
            session_id="test_session",
            job_id="test_job",
            stacks=[{"node_id": "test_node", "flow": "test_flow"}],
            block_path="test/block"
        )
        self.temp_dir = tempfile.mkdtemp()
        self.session_dir = tempfile.mkdtemp()

        # Define outputs with different handle types
        self.outputs_def = {
            "string_output": {
                "handle": "string_output",
                "description": "A string output",
                "json_schema": {"type": "string"},
                "kind": None,
                "nullable": False,
                "is_additional": False,
            },
            "var_output": {
                "handle": "var_output",
                "description": "A var output",
                "json_schema": {"type": "object", "contentMediaType": "oomol/var"},
                "kind": None,
                "nullable": False,
                "is_additional": False,
            },
            "bin_output": {
                "handle": "bin_output",
                "description": "A binary output",
                "json_schema": {"type": "string", "contentMediaType": "oomol/bin"},
                "kind": None,
                "nullable": False,
                "is_additional": False,
            },
        }

        self.inputs_def = {}
        self.inputs = {}

    def _create_context(self):
        """Helper to create a Context instance."""
        from oocana import Context

        return Context(
            inputs=self.inputs,
            blockInfo=self.block_info,
            mainframe=self.mock_mainframe,
            store=self.mock_store,
            inputs_def=self.inputs_def,
            outputs_def=self.outputs_def,
            session_dir=self.session_dir,
            tmp_dir=self.temp_dir,
            package_name="test_package",
            pkg_dir=self.temp_dir,
        )

    def test_finish_without_result(self):
        """Test finish() without result sends BlockFinished message."""
        ctx = self._create_context()
        ctx.finish()

        self.mock_mainframe.send.assert_called_once()
        call_args = self.mock_mainframe.send.call_args
        payload = call_args[0][1]

        self.assertEqual(payload["type"], "BlockFinished")
        self.assertNotIn("result", payload)
        self.assertNotIn("error", payload)

    def test_finish_with_error(self):
        """Test finish() with error sends error message."""
        ctx = self._create_context()
        ctx.finish(error="Test error message")

        self.mock_mainframe.send.assert_called_once()
        call_args = self.mock_mainframe.send.call_args
        payload = call_args[0][1]

        self.assertEqual(payload["type"], "BlockFinished")
        self.assertEqual(payload["error"], "Test error message")

    def test_finish_with_result(self):
        """Test finish() with result sends result message."""
        ctx = self._create_context()
        ctx.finish(result={"string_output": "test value"})

        self.mock_mainframe.send.assert_called_once()
        call_args = self.mock_mainframe.send.call_args
        payload = call_args[0][1]

        self.assertEqual(payload["type"], "BlockFinished")
        self.assertEqual(payload["result"], {"string_output": "test value"})

    def test_finish_error_takes_priority(self):
        """Test finish() with both error and result only sends error."""
        ctx = self._create_context()
        ctx.finish(error="Test error", result={"string_output": "test"})

        call_args = self.mock_mainframe.send.call_args
        payload = call_args[0][1]

        self.assertEqual(payload["type"], "BlockFinished")
        self.assertEqual(payload["error"], "Test error")
        self.assertNotIn("result", payload)

    def test_output_sends_message(self):
        """Test output() sends BlockOutput message."""
        ctx = self._create_context()
        ctx.output("string_output", "hello world")

        self.mock_mainframe.send.assert_called_once()
        call_args = self.mock_mainframe.send.call_args
        payload = call_args[0][1]

        self.assertEqual(payload["type"], "BlockOutput")
        self.assertEqual(payload["handle"], "string_output")
        self.assertEqual(payload["output"], "hello world")

    def test_output_undefined_handle_warns(self):
        """Test output() with undefined handle sends warning."""
        ctx = self._create_context()
        ctx.output("undefined_handle", "value")

        # Should call report with warning, not send
        self.mock_mainframe.report.assert_called()
        call_args = self.mock_mainframe.report.call_args
        payload = call_args[0][1]

        self.assertEqual(payload["type"], "BlockWarning")
        self.assertIn("undefined_handle", payload["warning"])

    def test_outputs_sends_batch_message(self):
        """Test outputs() sends BlockOutputs message."""
        ctx = self._create_context()
        ctx.outputs({"string_output": "value1"})

        self.mock_mainframe.send.assert_called_once()
        call_args = self.mock_mainframe.send.call_args
        payload = call_args[0][1]

        self.assertEqual(payload["type"], "BlockOutputs")
        self.assertEqual(payload["outputs"], {"string_output": "value1"})

    def test_send_warning(self):
        """Test send_warning() sends BlockWarning report."""
        ctx = self._create_context()
        ctx.send_warning("Test warning message")

        self.mock_mainframe.report.assert_called_once()
        call_args = self.mock_mainframe.report.call_args
        payload = call_args[0][1]

        self.assertEqual(payload["type"], "BlockWarning")
        self.assertEqual(payload["warning"], "Test warning message")

    def test_error(self):
        """Test error() sends BlockError message."""
        ctx = self._create_context()
        ctx.error("Test error message")

        self.mock_mainframe.send.assert_called_once()
        call_args = self.mock_mainframe.send.call_args
        payload = call_args[0][1]

        self.assertEqual(payload["type"], "BlockError")
        self.assertEqual(payload["error"], "Test error message")

    def test_send_message(self):
        """Test send_message() sends BlockMessage report."""
        ctx = self._create_context()
        ctx.send_message({"custom": "payload"})

        self.mock_mainframe.report.assert_called_once()
        call_args = self.mock_mainframe.report.call_args
        payload = call_args[0][1]

        self.assertEqual(payload["type"], "BlockMessage")
        self.assertEqual(payload["payload"], {"custom": "payload"})

    def test_session_id_property(self):
        """Test session_id property returns correct value."""
        ctx = self._create_context()
        self.assertEqual(ctx.session_id, "test_session")

    def test_job_id_property(self):
        """Test job_id property returns correct value."""
        ctx = self._create_context()
        self.assertEqual(ctx.job_id, "test_job")

    def test_node_id_property(self):
        """Test node_id property returns correct value from stacks."""
        ctx = self._create_context()
        self.assertEqual(ctx.node_id, "test_node")

    def test_tmp_dir_property(self):
        """Test tmp_dir property returns correct value."""
        ctx = self._create_context()
        self.assertEqual(ctx.tmp_dir, self.temp_dir)

    def test_session_dir_property(self):
        """Test session_dir property returns correct value."""
        ctx = self._create_context()
        self.assertEqual(ctx.session_dir, self.session_dir)

    def test_inputs_def_readonly(self):
        """Test inputs_def is read-only."""
        ctx = self._create_context()
        inputs_def = ctx.inputs_def

        with self.assertRaises(TypeError):
            inputs_def["new_key"] = {}  # type: ignore

    def test_outputs_def_readonly(self):
        """Test outputs_def is read-only."""
        ctx = self._create_context()
        outputs_def = ctx.outputs_def

        with self.assertRaises(TypeError):
            outputs_def["new_key"] = {}  # type: ignore

    def tearDown(self):
        """Clean up temporary directories."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        if os.path.exists(self.session_dir):
            shutil.rmtree(self.session_dir)


if __name__ == "__main__":
    unittest.main()
