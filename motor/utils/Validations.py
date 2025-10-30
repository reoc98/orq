import json
# import yaml
import jsonschema
import logging
import re
from jsonschema import validate, FormatChecker

class Validations:
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
    def type(cls, data, type_data):
        """
        Validar tipo de dato
        :param: data
            dato a validar
        :param: type_data
            tipo de dato a validar
        :return: bool
            True si el tipo de dato es el mismo, False si no
        """
        return isinstance(data, type_data)
    @classmethod
    def length(cls, data, length):
        """
        Validar longitud de dato
        :param: data
            dato a validar
        :param: length
            longitud a validar
        :return: bool
            True si el tipo de dato es el mismo, False si no
        """
        return len(data) == length
    @classmethod
    def min_length(cls, data, length):
        """
        Validar longitud minima de dato
        :param: data
            dato a validar
        :param: length
            longitud a validar
        :return: bool
            True si el tipo de dato es el mismo, False si no
        """
        return len(data) >= length
    @classmethod
    def max_length(cls, data, length):
        """
        Validar longitud maxima de dato
        :param: data
            dato a validar
        :param: length
            longitud a validar
        :return: bool
            True si el tipo de dato es el mismo, False si no
        """
        return len(data) <= length
    
    @classmethod
    def range_length(cls, data, min_length, max_length):
        """
        Validar longitud de dato
        :param: data
            dato a validar
        :param: min_length
            longitud minima a validar
        :param: max_length
            longitud maxima a validar
        :return: bool
            True si el tipo de dato es el mismo, False si no
        """
        return cls.min_length(data, min_length) and cls.max_length(data, max_length)

    @classmethod
    def regex(cls, data, regex):
        """
        Validar longitud de dato
        :param: data
            dato a validar
        :param: regex
            expresion regular a validar
        :return: bool
            True si el tipo de dato es el mismo, False si no
        """
        return re.match(regex, data) is not None
    
    @classmethod
    def is_email(cls, data):
        """
        Validar longitud de dato
        :param: data
            dato a validar
        :return: bool
            True si el tipo de dato es el mismo, False si no
        """
        return cls.regex(data, '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}')
    
    @classmethod
    def is_password(cls, password: str):
        """
        Validar que la contraseña cumpla con los requisitos
            * Longitud mínima 8
            * Debe tener números
            * Debe tener un carácter especial
            * Debe tener mayúsculas
            * Debe tener minúsculas
        
        :param: password
            dato a validar
        :return: bool
            True si la contraseña cumple con los requisitos, False si no
        """
        return cls.regex(
            password, 
            '^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[$@$!%*?&#.$($)$-$_])[A-Za-z\d$@$!%*?&#.$($)$-$_]{8,}$'
        )
    
    @classmethod
    def is_number(cls, data):
        """
        Validar tipo de dato
        :param: data
            dato a validar
        :return: bool
            True si el tipo de dato es el mismo, False si no
        """
        return cls.type(data, int) or cls.type(data, float)
    
    @classmethod
    def is_integer(cls, data):
        """
        Validar tipo de dato
        :param: data
            dato a validar
        :return: bool
            True si el tipo de dato es el mismo, False si no
        """
        return cls.type(data, int)
    
    @classmethod
    def is_string(cls, data):
        """
        Validar tipo de dato
        :param: data
            dato a validar
        :return: bool
            True si el tipo de dato es el mismo, False si no
        """
        return cls.type(data, str)
    
    @classmethod
    def is_int_str(cls, data):
        """
        Validar tipo de dato
        :param: data
            dato a validar
        :return: bool
            True si el tipo de dato es el mismo, False si no
        """
        return int(data) if cls.string(data) else False
    
    @classmethod
    def is_boolean(cls, data):
        """
        Validar tipo de dato
        :param: data
            dato a validar
        :return: bool
            True si el tipo de dato es el mismo, False si no
        """
        return cls.type(data, bool)
    
    @classmethod
    def is_boolean_string(cls, data):
        """
        Validar tipo de dato
        :param: data
            dato a validar
        :return: bool
            True si el tipo de dato es el mismo, False si no
        """
        return data == 'true' or data == 'false'
    
    @classmethod
    def is_boolean_number(cls, data):
        """
        Validar tipo de dato
        :param: data
            dato a validar
        :return: bool
            True si el tipo de dato es el mismo, False si no
        """
        return data == 0 or data == 1
    
    @classmethod
    def is_boolean_string_or_number(cls, data):
        """
        Validar tipo de dato
        :param: data
            dato a validar
        :return: bool
            True si el tipo de dato es el mismo, False si no
        """
        return cls.boolean_string(data) or cls.boolean_number(data)
    
    @classmethod
    def is_list(cls, data):
        """
        Validar tipo de dato
        :param: data
            dato a validar
        :return: bool
            True si el tipo de dato es el mismo, False si no
        """
        
        return cls.type(data, list)

    @classmethod
    def json_validator(cls, data):   
        try:
            return json.loads(data)
            
        except Exception as error:
            raise ValueError("El formato no corresponde al requerido.")
        
    @classmethod
    def get_token_header(cls, data_header):   
        try:
            
            token = data_header.get("authorization", False)
            if not(token):
                raise Exception()
            
            return token
            
        except Exception as error:
            raise ValueError("El formato Header no corresponde al requerido.")
