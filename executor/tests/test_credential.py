import unittest
from python_executor.credential import replace_credential, CredentialInput, generate_credential_input
from oocana import InputHandleDef
from typing import cast

ORIGIN_VALUE = "Custom,credential_id"

class TestCredential(unittest.TestCase):

    def test_credential_fallback(self):
        """Test credential fallback when not a credential handle"""
        v = replace_credential({
            "c": "aaaa"
        }, {
            "c": InputHandleDef(handle="c", json_schema={
                "contentMediaType": "oomol/credential"
            }, value=None)
        })
        # Should return CredentialInput when parsed successfully
        cred_input = generate_credential_input("aaaa")
        self.assertIsNone(cred_input)
        self.assertIsNone(v.get("c"))

    def test_replace_credential(self):
        """Test basic credential replacement"""
        v = replace_credential({
            "c": f'${{{{OO_CREDENTIAL:{ORIGIN_VALUE}}}}}'
        }, {
            "c": InputHandleDef(handle="c", json_schema={
                "contentMediaType": "oomol/credential"
            }, value=None)
        })
        cred_input = v.get("c")
        self.assertIsInstance(cred_input, CredentialInput)
        self.assertEqual(cred_input.type, "Custom")
        self.assertEqual(cred_input.value, "credential_id")


    def test_credential_without_content_media(self):
        """Test multiple credentials replacement"""
        v = replace_credential({
            "c": f'${{{{OO_CREDENTIAL:{ORIGIN_VALUE}}}}}',
            "a": f'${{{{OO_CREDENTIAL:{ORIGIN_VALUE}}}}}'
        }, {
            "c": InputHandleDef(handle="c", json_schema={
                "contentMediaType": "oomol/credential"
            }, value=None)
        })
        cred_input_c = v.get("c")
        cred_input_a = v.get("a")

        self.assertIsInstance(cred_input_c, CredentialInput)
        self.assertEqual(cred_input_c.type, "Custom")

        # 'a' should remain unchanged since no input_def for it
        self.assertEqual(cred_input_a, f'${{{{OO_CREDENTIAL:{ORIGIN_VALUE}}}}}')

    def test_credential_in_other_string(self):
        """Test credential pattern inside other string (should not be replaced)"""
        no_replace_value = f'${{{{OO_CREDENTIAL:{ORIGIN_VALUE}}}}}_bbb'
        v = replace_credential({
            "c": no_replace_value
        }, {
            "c": InputHandleDef(handle="c", json_schema={
                "contentMediaType": "oomol/credential"
            }, value=None)
        })
        # Should not be replaced because it doesn't match exact format
        self.assertEqual(v.get("c"), None)

    def test_generate_credential_input_valid(self):
        """Test valid credential input generation"""
        result = generate_credential_input("${{OO_CREDENTIAL:AWS,my_credential_id}}")
        self.assertIsInstance(result, CredentialInput)
        result = cast(CredentialInput, result)
        self.assertEqual(result.type, "AWS")
        self.assertEqual(result.value, "my_credential_id")

    def test_generate_credential_input_invalid_format(self):
        """Test invalid credential input format"""
        # Missing prefix
        result = generate_credential_input("AWS,my_credential_id")
        self.assertIsNone(result)

        # Missing suffix
        result = generate_credential_input("${{OO_CREDENTIAL:AWS,my_credential_id")
        self.assertIsNone(result)

        # Wrong prefix
        result = generate_credential_input("${{OO_SECRET:AWS,my_credential_id}}")
        self.assertIsNone(result)

        # Empty content
        result = generate_credential_input("${{OO_CREDENTIAL:}}")
        self.assertIsNone(result)

        # Missing comma
        result = generate_credential_input("${{OO_CREDENTIAL:AWS}}")
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()