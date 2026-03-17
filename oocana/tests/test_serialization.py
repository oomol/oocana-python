import unittest
from unittest.mock import MagicMock, patch
import tempfile
import os
import json


class TestCompressionSuffix(unittest.TestCase):
    """Test cases for compression_suffix function."""

    def setUp(self):
        # Create a temporary directory for the mock context
        self.temp_dir = tempfile.mkdtemp()
        self.mock_context = MagicMock()
        self.mock_context.pkg_data_dir = self.temp_dir

    def tearDown(self):
        # Clean up temporary files
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_compression_suffix_no_options(self):
        """Test that .pkl is returned when no compression options exist."""
        from oocana.oocana.serialization import compression_suffix

        result = compression_suffix(self.mock_context)
        self.assertEqual(result, ".pkl")

    def test_compression_suffix_zip(self):
        """Test compression suffix for zip method."""
        from oocana.oocana.serialization import compression_suffix, COMPRESSION_OPTIONS_FILE

        with open(os.path.join(self.temp_dir, COMPRESSION_OPTIONS_FILE), "w") as f:
            json.dump({"method": "zip"}, f)

        result = compression_suffix(self.mock_context)
        self.assertEqual(result, ".zip")

    def test_compression_suffix_gzip(self):
        """Test compression suffix for gzip method."""
        from oocana.oocana.serialization import compression_suffix, COMPRESSION_OPTIONS_FILE

        with open(os.path.join(self.temp_dir, COMPRESSION_OPTIONS_FILE), "w") as f:
            json.dump({"method": "gzip"}, f)

        result = compression_suffix(self.mock_context)
        self.assertEqual(result, ".gz")

    def test_compression_suffix_bz2(self):
        """Test compression suffix for bz2 method."""
        from oocana.oocana.serialization import compression_suffix, COMPRESSION_OPTIONS_FILE

        with open(os.path.join(self.temp_dir, COMPRESSION_OPTIONS_FILE), "w") as f:
            json.dump({"method": "bz2"}, f)

        result = compression_suffix(self.mock_context)
        self.assertEqual(result, ".bz2")

    def test_compression_suffix_zstd(self):
        """Test compression suffix for zstd method."""
        from oocana.oocana.serialization import compression_suffix, COMPRESSION_OPTIONS_FILE

        with open(os.path.join(self.temp_dir, COMPRESSION_OPTIONS_FILE), "w") as f:
            json.dump({"method": "zstd"}, f)

        result = compression_suffix(self.mock_context)
        self.assertEqual(result, ".zst")

    def test_compression_suffix_xz(self):
        """Test compression suffix for xz method."""
        from oocana.oocana.serialization import compression_suffix, COMPRESSION_OPTIONS_FILE

        with open(os.path.join(self.temp_dir, COMPRESSION_OPTIONS_FILE), "w") as f:
            json.dump({"method": "xz"}, f)

        result = compression_suffix(self.mock_context)
        self.assertEqual(result, ".xz")

    def test_compression_suffix_tar(self):
        """Test compression suffix for tar method."""
        from oocana.oocana.serialization import compression_suffix, COMPRESSION_OPTIONS_FILE

        with open(os.path.join(self.temp_dir, COMPRESSION_OPTIONS_FILE), "w") as f:
            json.dump({"method": "tar"}, f)

        result = compression_suffix(self.mock_context)
        self.assertEqual(result, ".tar")

    def test_compression_suffix_null_method(self):
        """Test that .pkl is returned when method is null."""
        from oocana.oocana.serialization import compression_suffix, COMPRESSION_OPTIONS_FILE

        with open(os.path.join(self.temp_dir, COMPRESSION_OPTIONS_FILE), "w") as f:
            json.dump({"method": None}, f)

        result = compression_suffix(self.mock_context)
        self.assertEqual(result, ".pkl")

    def test_compression_suffix_missing_method_key(self):
        """Test that .pkl is returned when method key is missing (no KeyError)."""
        from oocana.oocana.serialization import compression_suffix, COMPRESSION_OPTIONS_FILE

        # Write a dict without the 'method' key
        with open(os.path.join(self.temp_dir, COMPRESSION_OPTIONS_FILE), "w") as f:
            json.dump({"other_key": "value"}, f)

        # Should not raise KeyError
        result = compression_suffix(self.mock_context)
        self.assertEqual(result, ".pkl")

    def test_compression_suffix_unknown_method(self):
        """Test that .pkl is returned for unknown compression method."""
        from oocana.oocana.serialization import compression_suffix, COMPRESSION_OPTIONS_FILE

        with open(os.path.join(self.temp_dir, COMPRESSION_OPTIONS_FILE), "w") as f:
            json.dump({"method": "unknown_method"}, f)

        result = compression_suffix(self.mock_context)
        self.assertEqual(result, ".pkl")


class TestCompressionOptions(unittest.TestCase):
    """Test cases for compression_options function."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.mock_context = MagicMock()
        self.mock_context.pkg_data_dir = self.temp_dir

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_compression_options_returns_none_when_no_file(self):
        """Test that None is returned when options file doesn't exist."""
        from oocana.oocana.serialization import compression_options

        result = compression_options(self.mock_context)
        self.assertIsNone(result)

    def test_compression_options_returns_dict_when_file_exists(self):
        """Test that options are returned when file exists."""
        from oocana.oocana.serialization import compression_options, COMPRESSION_OPTIONS_FILE

        expected = {"method": "gzip"}
        with open(os.path.join(self.temp_dir, COMPRESSION_OPTIONS_FILE), "w") as f:
            json.dump(expected, f)

        result = compression_options(self.mock_context)
        self.assertEqual(result, expected)

    def test_compression_options_handles_invalid_json(self):
        """Test that None is returned for invalid JSON."""
        from oocana.oocana.serialization import compression_options, COMPRESSION_OPTIONS_FILE

        with open(os.path.join(self.temp_dir, COMPRESSION_OPTIONS_FILE), "w") as f:
            f.write("not valid json")

        result = compression_options(self.mock_context)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
