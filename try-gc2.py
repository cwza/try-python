import gc
import sys
from gevent.pywsgi import WSGIServer
import fastjsonschema
import simplejson as json

EMPTY_BYTES_SIZE = sys.getsizeof(b'')
def allocate_bytes(size):
    bytes_len = (size - EMPTY_BYTES_SIZE)
    return b'x' * bytes_len


from flask import Flask
app = Flask(__name__)
from memory_profiler import profile as mprofile

def generate_json_schemas(n=1):
    json_schemas = []
    for i in range(n):
        json_schema = """
{
    "title": "FooReq1",
    "type": "object",
    "properties": {
        "attr1": {
            "title": "Attr1",
            "type": "integer"
        },
        "attr2": {
            "$ref": "#/definitions/FooReq2"
        }
    },
    "required": [
        "attr1",
        "attr2"
    ],
    "definitions": {
        "FooReq2": {
            "title": "FooReq2",
            "type": "object",
            "properties": {
                "attr1": {
                    "title": "Attr1",
                    "type": "string"
                }
            },
            "required": [
                "attr1"
            ]
        }
    }
}
"""
        json_schemas.append(json_schema)
    return json_schemas

def generate_large_code(n=1, with_new_class=False):
    last = ""
    for i in range(n):
        code = f"""
a{i} = 'aaaaaaaaaaaaaaaaaaaaaaaaaa'
"""
        if with_new_class:
            code += f"""
class Foo{i}():
    pass
"""
        last += code
#     last += """
# EMPTY_BYTES_SIZE = sys.getsizeof(b'')
# def allocate_bytes(size):
#     bytes_len = (size - EMPTY_BYTES_SIZE)
#     return b'x' * bytes_len
# aa = allocate_bytes(50*1024*1024)
# """
    return last

@mprofile
def exec_large_codes():
    for i in range(100):
        data = {'xxx': 'xxx'}
        code = generate_large_code(100, False)
        # print(code)
        # xxx = compile(code, "", "exec")
        # exec(xxx)
        exec(code, {}, {'data': data})
    pass

@mprofile
def validate_by_fastjsonschema():
    json_schemas = generate_json_schemas(100)
    for json_schema in json_schemas:
        data = {"attr1": 1, "attr2": {"attr1": 1}}
        json_schema_dict = json.loads(json_schema)

        # generated_code = fastjsonschema.compile_to_code(json_schema_dict)
        # print(generated_code)

        validate = fastjsonschema.compile(json_schema_dict)
        validate(data)
    pass

@mprofile
def validate_by_self_code():
    json_schemas = generate_json_schemas(100)
    for json_schema in json_schemas:
        data = {"attr1": 1, "attr2": {"attr1": 1}}
        json_schema_dict = json.loads(json_schema)

        # generated_code = fastjsonschema.compile_to_code(json_schema_dict)
        # print(generated_code)
        # return
        # _, code_generator = fastjsonschema._factory(json_schema_dict, {}, {})
        # generated_code = code_generator.global_state_code + '\n' + code_generator.func_code + '\n' + 'validate(data)'
        code = """
def validate___definitions_fooreq2(data):
    # # if not isinstance(data, (dict)):
    # #     raise JsonSchemaException("data must be object", value=data, name="data", definition={'title': 'FooReq2', 'type': 'object', 'properties': {'attr1': {'title': 'Attr1', 'type': 'string'}}, 'required': ['attr1']}, rule='type')
    # data_is_dict = isinstance(data, dict)
    # if data_is_dict:
    #     data_len = len(data)
    #     # if not all(prop in data for prop in ['attr1']):
    #     #     raise JsonSchemaException("data must contain ['attr1'] properties", value=data, name="data", definition={'title': 'FooReq2', 'type': 'object', 'properties': {'attr1': {'title': 'Attr1', 'type': 'string'}}, 'required': ['attr1']}, rule='required')
    #     data_keys = set(data.keys())
    #     if "attr1" in data_keys:
    #         data_keys.remove("attr1")
    #         data__attr1 = data["attr1"]
    #         # if not isinstance(data__attr1, (str)):
    #         #     raise JsonSchemaException("data.attr1 must be string", value=data__attr1, name="data.attr1", definition={'title': 'Attr1', 'type': 'string'}, rule='type')
    return data
def validate(data):
    if not isinstance(data, (dict)):
        raise JsonSchemaException("data must be object", value=data, name="data", definition={'title': 'FooReq1', 'type': 'object', 'properties': {'attr1': {'title': 'Attr1', 'type': 'integer'}, 'attr2': {'$ref': '#/definitions/FooReq2'}}, 'required': ['attr1', 'attr2'], 'definitions': {'FooReq2': {'title': 'FooReq2', 'type': 'object', 'properties': {'attr1': {'title': 'Attr1', 'type': 'string'}}, 'required': ['attr1']}}}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['attr1', 'attr2']):
            raise JsonSchemaException("data must contain ['attr1', 'attr2'] properties", value=data, name="data", definition={'title': 'FooReq1', 'type': 'object', 'properties': {'attr1': {'title': 'Attr1', 'type': 'integer'}, 'attr2': {'$ref': '#/definitions/FooReq2'}}, 'required': ['attr1', 'attr2'], 'definitions': {'FooReq2': {'title': 'FooReq2', 'type': 'object', 'properties': {'attr1': {'title': 'Attr1', 'type': 'string'}}, 'required': ['attr1']}}}, rule='required')
        data_keys = set(data.keys())
        if "attr1" in data_keys:
            data_keys.remove("attr1")
            data__attr1 = data["attr1"]
            if not isinstance(data__attr1, (int)) and not (isinstance(data__attr1, float) and data__attr1.is_integer()) or isinstance(data__attr1, bool):
                raise JsonSchemaException("data.attr1 must be integer", value=data__attr1, name="data.attr1", definition={'title': 'Attr1', 'type': 'integer'}, rule='type')
        if "attr2" in data_keys:
            data_keys.remove("attr2")
            data__attr2 = data["attr2"]
            # validate___definitions_fooreq2(data__attr2)
        return data
validate(data)
"""
        # exec(code, {'data': data})
        exec(code, {'JsonSchemaException': fastjsonschema.JsonSchemaException}, {'data': data})
    pass

@app.route("/")
def hello():
    gc.disable()
    # exec_large_codes()
    # validate_by_fastjsonschema()
    validate_by_self_code()
    # gc.collect()
    # print(gc.garbage)
    return "Hello, World!"

@app.route("/gc")
def garbage_collect():
    gc.collect()
    return 'manually gc'

http_server = WSGIServer(('0.0.0.0', 6001), app)
http_server.serve_forever()
