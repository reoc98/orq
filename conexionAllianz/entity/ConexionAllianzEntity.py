from utils.Validations import Validations, Response
class ConexionAllianzEntity:
    def keyRules(self, p):
        rules = {
            "receive_request": {
                "num_siniestro": [int(), 1,50],
                "fecha_aviso_siniestro": [int(), 1,8,1],
                "hora_ocurrencia": [int(), 1,4],
                "fecha_ocurrencia": [int(), 1,8,1],
                "fecha_protocolo": [int(), 1,8,1],
                "mediador": [str(), 1,100],
                "aplica": [int(), 1,10],
                "numero_poliza": [int(), 1,50],
                "sucursal": [str(), 1,50],
                "cod_campo_culpa": [str(), 1,10],
                "campo_culpa": [str(), 1,50],
                "dep_ocurrencia": [str(), 1,2],
                "ciu_ocurrencia": [str(), 1,5],
                "cod_dane_circulacion": [str(), 1,5],
                "cod_ciudad_circulacion": [str(), 1,5],
                "ciudad_circul_habitual": [str(), 1,50],
                "cod_campo_mediador": [int(), 1,10],
                "cod_campo_sucursal": [int(), 1,10],
                "cod_fasecolda": [int(), 1,10],
                "fecha_anul_revl": [int(), 0,8,1],
                "fecha_emision": [int(), 1,8,1],
                "fecha_fin_vigencia_poliza": [int(), 1,8,1],
                "fecha_ini_vigencia_poliza": [int(), 1,8,1],
                "marca": [str(), 1,50],
                "mod_year_fabricacion": [int(), 1,4],
                "clase": [str(), 1,50],
                "num_chasis": [str(), 1,50],
                "num_motor": [str(), 1,50],
                "num_serie_vehiculo": [str(), 1,50],
                "tipo": [str(), 1,50],
                "valor_accesorios": [int(), 1,50],
                "valor_asegurado": [int(), 1,50],
                "valor_blindaje": [int(), 1,50],
                "valor_sist_gas": [int(), 1,50],
                "version": [str(), 1,50],
                "garantias": [list(), 1,0],
                "figuras_personas": [list(), 1,0],
                "recibos": [list(), 1,0],
                "figuras_vehiculo": [list(), 1,0]
            },
            "garantias":{
                "capital": [int(), 1,50],
                "franquicia": [int(), 1,50],
                "id_cobertura": [str(), 1,10],
                "nombre_cobertura": [str(), 1,50]
            },
            "figuras_personas": {
                "tipo_figura": [str(), 1,50],
                "nombre_figura": [str(), 0,100],
                "tipo_doc_figura": [str(), 0,50],
                "num_doc_figura": [int(), 0,50],
                "lista_restrictiva": [str(), 0,5],
                "tipo_interviniente": [str(), 0,50],
                "num_pagos": [int(), 0,10],
                "siniestros_persona_fasecolda": [int(), 0,10],
                "coexistencia_fasecolda_personas": [int(), 0,10]
            },
            "recibos": {
                "estado_recibo": [str(), 0, 2],
                "fecha_efecto": [int(), 1,8,1],
                "fecha_estado_recibo": [int(), 0,6,1],
                "fecha_limite_pago": [int(), 1,8,1],
                "fecha_termino": [int(), 1,8,1],
                "num_recibo": [int(), 1,50],
                "prima": [int(), 1,50]
            },
            "figuras_vehiculo": {
                "tipo_figura": [str(), 1,50],
                "Vetos": [str(), 0,5],
                "siniestros_placa_fasecolda": [int(), 0,10],
                "coexistencia_fasecolda_vehiculo": [int(), 0,10],
                "placa": [str(), 0,50]
            },
            "get_tokens_orquestador":{
                "username": [str(), 1,0],
                "password": [str(), 1,0]
            }
        }
        if p in rules:
            return rules[p]
        
    def validaList(self, datos):
        validate = Validations()
        val = True
        response = {}
        for key,value in datos.items():
            keysRule = self.keyRules(key)
            for  v in value:
                if len(v) == 0:
                    continue
                respuesta = validate.validateInput(v, keysRule)
                if respuesta["statusCode"] != 200:
                    val = False
                    response = respuesta
                    break
        return {
            "validate" : val,
            "response" : response
        }

    # validamos que el interviniente no este repetido
    def validaInterviniente(self, datos):
        
        # obtenemos el tipo de figura
        figuras_personas = datos.get("figuras_personas",[])
        resp = Response()
        val = True
        cont = 1
        notTypeKeys = []
        # obtenemos la lista de los tipo de figura
        listado_id = [man["num_doc_figura"] for man in figuras_personas if man["tipo_figura"] == "Interviniente" and "num_doc_figura" in man]
        # recorremos el tipo de figura para saber si esta repetido
        for row in figuras_personas:
            if row["tipo_figura"] == "Interviniente" and "num_doc_figura" in row:
                if row["num_doc_figura"] is not None and row["num_doc_figura"] != "" and row["num_doc_figura"] != 0:
                    if listado_id.count(row["num_doc_figura"]) > 1:
                        notTypeKeys.append(f"{cont} - El documento {row['num_doc_figura']} de tipo interviniente está repetido.")
                        cont += 1
                        # se elimina de la lista para que no se repita
                        for n in range(listado_id.count(row["num_doc_figura"])):
                            del listado_id[int(listado_id.index(row["num_doc_figura"]))]

        # validamos si hubo algun repetido
        if len(notTypeKeys) > 0:
            val = False
            if len(notTypeKeys) > 1:
                message = notTypeKeys
                statusCode = 400
            else:
                message = notTypeKeys[0][4:]
                statusCode = 400
        else:
            message = "proceso exitoso"
            statusCode = 200

        return {
            "validate" : val,
            "response" : resp.armadoBody(message, statusCode)
        } 
    
    # validamos que las figura de tipo Condutor y Asegurado solo haya una figura de estos tipo
    def validar_cantidad_tipo_figura(self, datos, nom_tipo_figura):
        figuras = datos.get(nom_tipo_figura,[])
        cant_asegurados = 0
        cant_condutores = 0

        for figura in figuras:
            if figura["tipo_figura"] == "Asegurado":
                cant_asegurados += 1
                
            if figura["tipo_figura"] == "Conductor":
                cant_condutores += 1
                
        if cant_asegurados > 1:
            return f"Existe más de un Asegurado en el paramentro de '{nom_tipo_figura}'."
        
        elif cant_condutores > 1:
            return f"Existe más de un Conductor en el paramentro de '{nom_tipo_figura}'."
        
        else:
            return True
             