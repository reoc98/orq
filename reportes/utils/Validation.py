import json
# import yaml
import jsonschema
import logging
import re
from jsonschema import validate, FormatChecker

class Validation:
    @classmethod
    def schema_validation(cls, schema, document):
        response = {
            "code": 0,
            "message": ""
        }
        try:
            validate(
                schema=schema,
                instance=document,
                format_checker=FormatChecker()
            )
            response["message"] = "the schama is valid"
        except Exception as ex:
            response_split = str(ex).split('\n')
            is_empty_property = ex.message.find("''") > -1
         
            
            if len(ex.relative_path) > 0 and is_empty_property:
                # error = re.sub("'(.)*'", ex.relative_path[0], str(ex.message))
                error = re.sub("''", ex.relative_path[0], str(ex.message))
            else:
                error = str(ex.message)
            
            response["code"] = -1
            response["message"] = error
            
            raise ValueError(error)
        return response

    @classmethod
    def read_json_file(cls, path: str):
        data = {}
        try:
            with open(path) as lfile:
                data = json.load(lfile)
        except jsonschema.exceptions.ValidationError as ex:
            exit(1)
        return data
    
    @classmethod
    def json_validator(cls, data):   
        try:
            return json.loads(data)
            
        except Exception as error:
            raise ValueError("El formato no corresponde al requerido.")
        