import json
import requests
from requests.auth import HTTPBasicAuth
from clases.Database import Database
from models.RequestsOrquestadorModel import RequestsOrquestadorModel as requestsOrq
from models.ServiceInif import ServiceInif as ServiceInifModel
from models.TipoDocumento import TipoDocumento
from utils.Aws import Aws
from utils.Services import Services

class ServiceInif:
    def __init__(self, id_request_orq, figure):
        self.id_request_orq = id_request_orq
        self.figure = figure

    def run_service(self):
        secrets = Aws.get_secret()
        inif_url = secrets['inif_url']
        
        document_type = self.get_document_type(self.figure['tipo_doc_figura'])
        if not document_type:
            raise Exception("Tipo de documento no encontrado.")
        
        body = [
            {
                'identity': f'{document_type.codigo}{self.figure["num_doc_figura"]}',
            }
        ]
        token = self.get_bearer_token(secrets)
        
        request = {
            'url': inif_url,
            'method': 'POST',
            'body': body,
            'headers': {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
        }
        print(f"Request to INIF: {request}")
        status_code = None
        response = None
        
        try:
            response = Services.run_request(
                **request
            )
            status_code = response.status_code
            response = response.text
            print(f"Response from INIF: {status_code} - {response}")
        
        except requests.Timeout as e:
            status_code = -504
            response = f"Timeout error: {str(e)}"

        except requests.RequestException as e:
            status_code = -500
            response = f"Request error: {str(e)}"
        
        except Exception as e:
            status_code = -500
            response = f"Unexpected error: {str(e)}"
        
        
        # save response to database
        self.insert(request, response, status_code)

    def get_bearer_token(self, secrets) -> str:
            login_url = secrets['inif_url_login']
            inif_user = secrets['inif_user']
            inif_password = secrets['inif_password']

            try:
                login_req_json = {
                    'url': login_url,
                    'method': 'POST',
                    'headers': {'Content-Type': 'application/json'},
                    'body': {
                        'username': inif_user,
                        'password': inif_password
                    }
                }
                print("Requesting token with JSON body (credentials masked in logs)")
                resp = Services.run_request(**login_req_json)
                token_data = resp.json()
                token = token_data.get("jwtToken")
                if not token:
                    raise Exception(f"No se encontró token en respuesta del login: {resp.text}")
                return token

            except requests.RequestException as e:
                raise Exception(f"Fallo solicitando token: {str(e)}")

    def insert(self, request: dict, response, status_code):
        session = Database('dbw').session
        try:
            status_code = response.status_code if isinstance(response, requests.Response) else status_code
            if isinstance(request, dict) and isinstance(request.get('auth'), HTTPBasicAuth):
                # request['auth'] = b64encode(
                #     f"{request['auth'].username}:{request['auth'].password}".encode('utf-8')
                # ).decode('utf-8')
                request['auth'] = f"{request['auth'].username}:{request['auth'].password}"
            session.add(
                ServiceInifModel({
                    'id_request_orq': self.id_request_orq,
                    'tipo_figura': self.figure.get('tipo_figura'),
                    'figuras': self.figure,
                    'status_code': status_code,
                    'numero_documento': self.figure.get('num_doc_figura'),
                    'request': json.dumps(request),
                    'response': json.dumps(response) if not isinstance(response, str) else response,
                })
            )
            session.commit()
        finally:
            session.close()
            session.invalidate()

    def get_orq_request(self):
        session = Database('dbr').session
        try:
            request_orq = session.query(
                requestsOrq.id,
                requestsOrq.request
            ).filter(
                requestsOrq.id == self.id_request_orq
            ).first()
            
            return request_orq
        finally:
            session.close()
            session.invalidate()
    
    def get_document_type(self, prefijo):
        session = Database('dbr').session
        try:
            
            query = session.query(TipoDocumento.codigo).filter(
                TipoDocumento.estado == 1,
                TipoDocumento.prefijo_request == prefijo
            ).first()
            
            return query
        finally:
            session.invalidate()
            session.close()