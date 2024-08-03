import simplejson as sjson
import json
import math

def test_json():
    data = {
        "name": "John",
        "age": 30,
        "city": "New York"
    }

    # use the json module
    json_data = json.dumps(data)
    assert json_data == '{"name": "John", "age": 30, "city": "New York"}'

    # use the simplejson module
    sjson_data = sjson.dumps(data)
    assert sjson_data == '{"name": "John", "age": 30, "city": "New York"}'

    # use the json module
    json_data = json.loads(json_data)
    assert json_data == data

    # use the simplejson module
    sjson_data = sjson.loads(sjson_data)
    assert sjson_data == data

def test_none_in_json():
    data = {
        "name": "John",
        "age": None,
        "city": "New York"
    }

    # use the json module
    json_data = json.dumps(data)
    assert json_data == '{"name": "John", "age": null, "city": "New York"}'

    # use the simplejson module
    sjson_data = sjson.dumps(data)
    assert sjson_data == '{"name": "John", "age": null, "city": "New York"}'

    # use the json module
    json_data = json.loads(json_data)
    assert json_data == data

    # use the simplejson module
    sjson_data = sjson.loads(sjson_data)
    assert sjson_data == data

def test_nan_in_json():
    data = {
        "name": "John",
        "age": float('nan'),
        "city": "New York"
    }

    # use the json module
    json_data = json.dumps(data)
    assert json_data == '{"name": "John", "age": NaN, "city": "New York"}'

    # use the simplejson module
    sjson_data = sjson.dumps(data, ignore_nan=True)
    assert sjson_data == '{"name": "John", "age": null, "city": "New York"}'

    # use the json module
    json_data = json.loads(json_data)
    assert math.isnan(json_data['age'])

    # use the simplejson module
    sjson_data = sjson.loads(sjson_data)
    assert sjson_data.get('age') is None