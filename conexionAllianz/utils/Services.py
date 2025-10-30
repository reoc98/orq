import os
import shutil
import requests
from utils.Aws import Aws

class Services:
    
    @staticmethod
    def run_request(
        url: str,
        method: str = 'GET',
        body: dict = None,
        headers: dict = None,
        timeout: int = 15,
        auth=None
    ) -> requests.Response:
        """
        Realiza una solicitud HTTP.
        """
        # try:
        print(f"auth: {auth}")
        response = requests.request(
            method=method,
            url=url,
            json=body,
            headers=headers,
            auth=auth,
            timeout=timeout,
        )
        return response
        # except requests.RequestException as e:
        #     raise
            # raise UserException(f"Error en la solicitud a {url}: {e}") from e
        
        
    @classmethod
    def run_request_w_certificate(
        cls,
        url: str,
        method: str = 'GET',
        body: dict = None,
        headers: dict = None,
        cert: str = None,
        verify: bool = True
    ) -> requests.Response:
        """
        Realiza una solicitud HTTP con certificado.
        """
        if cert is None:
            cert = cls.get_certificate_path()
        try:
            response = requests.request(
                method=method,
                url=url,
                json=body,
                headers=headers,
                cert=cert,
                verify=verify,
                timeout=15
            )
            return response
        # except requests.RequestException as e:
        #     raise
            # raise UserException(f"Error en la solicitud a {url}: {e}") from e
        finally:
            if os.path.exists("tmp"):
                print(f"[INFO] Eliminando carpeta temporal: tmp")
                shutil.rmtree("tmp")
    
    @staticmethod
    def get_certificate_path() -> tuple:
        """
        Obtiene la ruta del certificado.
        """

        secrets = Aws.get_secret()
        crt_folder = secrets['certificates_folder']
        crt_key_file = secrets.get('allianz_c_crt')
        key_file = secrets.get('allianz_c_key')
        
        crt_file_path = f"{crt_folder}{crt_key_file}"
        key_file_path = f"{crt_folder}{key_file}"
        
        # crt_file_name = f"tmp/{crt_key_file}"
        # key_file_name = f"tmp/{key_key_file}"
        # tmp_dir = os.path.join(os.getcwd(), "tmp")
        tmp_dir = "/tmp"
        os.makedirs(tmp_dir, exist_ok=True)
        
        crt_file_name = os.path.join(tmp_dir, crt_key_file)
        key_file_name = os.path.join(tmp_dir, key_file)

        os.makedirs(os.path.dirname(crt_file_name), exist_ok=True)
        os.makedirs(os.path.dirname(key_file_name), exist_ok=True)
        
        print(f"Downloading certificate from {crt_file_path} and key from {key_file_path}")
        
        print(f"Downloading certificate from {crt_file_path}")
        print(f"Certificate file will be saved as: {crt_file_name}")
        Aws.download_file_obj(crt_file_path, crt_file_name)
        
        print(f"Downloading key from {key_file_path}")
        print(f"Key file will be saved as: {key_file_name}")
        Aws.download_file_obj(key_file_path, key_file_name)

        return (crt_file_name, key_file_name)