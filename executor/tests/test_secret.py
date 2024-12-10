import unittest
from python_executor.secret import replace_secret, SECRET_FILE
from oocana import InputHandleDef
import json

SECRET_VALUE = "aaa_bbb"
SECRET_DAT = {
    "aaa": {
        "id": "019390cf-2a42-73dd-89ed-474ade0df7f5",
        "secretName": "aaa",
        "createdAt": 1733301316162,
        "secretType": "Custom",
        "secrets": [
            {
                "secretKey": "AccessKey_ID",
                "value": SECRET_VALUE,
            },
        ],
    },
}
ORIGIN_VALUE = "Custom,aaa,AccessKey_ID"

class TestSecret(unittest.TestCase):


    @classmethod
    def setUpClass(cls) -> None:

        import os.path
        if not os.path.exists(os.path.dirname(SECRET_FILE)):
            os.makedirs(os.path.dirname(SECRET_FILE), exist_ok=True)

        # write SECRET_DAT to file
        with open(SECRET_FILE, "w") as f:
            f.write(json.dumps(SECRET_DAT))

        return super().setUpClass()
    
    @classmethod
    def tearDownClass(cls) -> None:
        import os
        os.remove(SECRET_FILE)
        return super().tearDownClass()

    def test_replace_secret(self):
        v = replace_secret({
            "s": ORIGIN_VALUE
        }, {
            "s": InputHandleDef(handle="s", json_schema={
                # "type": "string",
                "contentMediaType": "oomol/secret"
            }, value=None)
        }, None)
        self.assertEqual(v.get("s"), SECRET_VALUE)

    def test_replace_object_nested_secret(self):
        v = replace_secret({
            "s": {
                "s": ORIGIN_VALUE
            }
        }, {
            "s": InputHandleDef(handle="s", json_schema={
                "type": "object",
                "properties": {
                    "s": {
                        "type": "string",
                        "contentMediaType": "oomol/secret"
                    }
                }
            }, value=None)
        }, None)
        self.assertEqual(v.get("s").get("s"), SECRET_VALUE)

    def test_replace_array_nested_secret(self):
        v = replace_secret({
            "s": [
                ORIGIN_VALUE
            ]
        }, {
            "s": InputHandleDef(handle="s", json_schema={
                "type": "array",
                "items": {
                    "type": "string",
                    "contentMediaType": "oomol/secret"
                }
            }, value=None)
        }, None)
        self.assertEqual(v.get("s")[0], SECRET_VALUE)

if __name__ == '__main__':
    unittest.main()