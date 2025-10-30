from clases.Database import Database
from models.PerfilesModel import PerfilesModel
from models.PerfilUsuariosModel import PerfilUsuariosModel
from models.UsuariosModel import UsuariosModel
from sqlalchemy.sql import func
from utils.Response import Response
import math


class Perfiles():
    # Funcion encargada de obtener los perfiles creados
    def get_all(request_body):
        response = Response()
        db = Database('dbr').session
        try:
            #Recibe pagina y limite de filas para la paginación
            limit = int(request_body['NUM_RESULTADOS'])
            page_now = int(request_body['PAGINA_ACTUAL'])

            offset = (page_now - 1) * limit

            #Recibe todos los perfiles activos de la BD
            perfiles = db.query(PerfilesModel.id,
            PerfilesModel.nombre,
            PerfilesModel.descripcion
            ).filter(
                PerfilesModel.estado == 1
            ).limit(limit).offset(offset).all()
            
            perfiles_list = []
            # recorre los resultados obtenidos para crear lista de diccionarios
            for perfil in perfiles:

                #Recibe la cantidad de usuarios asignados por perfil
                result = db.query(
                func.count(PerfilUsuariosModel.id_perfil).label('CONTADOR_USUARIOS'),
                ).outerjoin(
                UsuariosModel, 
                PerfilUsuariosModel.id_usuario == UsuariosModel.id
                ).filter(    
                    PerfilUsuariosModel.id_perfil==perfil.id,
                    UsuariosModel.estado != 0,
                    PerfilUsuariosModel.estado == 1,
                ).first()

                perfiles_list.append(
                    {
                        'ID': perfil.id,
                        'NOMBRE': perfil.nombre, 
                        'ASIGNADOS': result.CONTADOR_USUARIOS,
                        'DESCRIPCION': perfil.descripcion
                    }
                )

            #conteo de cantidad de registros
            registers = db.query(func.count(PerfilesModel.id).label('PAGINAS')).filter(PerfilesModel.estado == 1).first()
            #operacion para obtener numero de paginas a mostrar
            pages = math.ceil(registers.PAGINAS / limit)

            rows = {'PAGINACION':{
                            'PAGINA_ACTUAL':page_now,
                            'TOTAL_PAGINAS':pages,
                            'TOTAL_REGISTROS': registers.PAGINAS,
                            'REGISTROS_POR_PAGINA':limit
                        },
                    'LISTADO': perfiles_list
                    }

            #valida si se recibió algún dato
            if (len(perfiles)):
                return response.armadoBody("Servicio exitoso.", 200, rows)
            else:
                return response.armadoBody("No se encontraron datos.", 400)
        except Exception as error:
            return Response.internal_server_error(str(error))
        
        finally:
            db.invalidate()
            db.close()

    #Funcion encargada de obtener los usuarios que pertenecen a un perfil dado
    def get_one(request_body):
        #Recibe id del perfil para ver usuarios asignados
        var_name = request_body['ID_PERFIL']
        response = Response()
        db = Database('dbr').session
        
        try:
            #Recibe los usuarios que pertenecen al perfil dado
            result = db.query(UsuariosModel.id,
            PerfilesModel.nombre,
            UsuariosModel.nombres,UsuariosModel.apellidos,
            UsuariosModel.codigo_ce
            ).outerjoin(
                PerfilUsuariosModel,
                PerfilUsuariosModel.id_usuario == UsuariosModel.id
            ).outerjoin(
                PerfilesModel,
                PerfilesModel.id == PerfilUsuariosModel.id_perfil
            ).filter(
                PerfilesModel.estado == 1,
                UsuariosModel.estado != 0,
                PerfilUsuariosModel.estado == 1,
                PerfilesModel.id == var_name
            ).group_by(UsuariosModel.id).all()
            
            #valida si se recibió algún dato
            rows = []
            if (len(result)):
                # recorre los resultados obtenidos para crear lista
                for my_data in result:

                    profile_name = my_data.nombre

                    rows.append({'NOMBRES': my_data.nombres,
                    'APELLIDOS': my_data.apellidos, 'CODIGO': my_data.codigo_ce})
                
                data = {
                    'NOMBRE_PERFIL': profile_name,
                    'USUARIOS':rows
                }
            
                return response.armadoBody("Servicio exitoso.", 200, data)
            else:
                return response.armadoBody("No se encontraron datos.", 400)
        except Exception as error:
            return Response.internal_server_error(str(error))
        
        finally:
            db.invalidate()
            db.close()
