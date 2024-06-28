from config.funcoes import jsonSuccess, listardados, dataHoraAtual, jsonResposta
from werkzeug.exceptions import Unauthorized, BadRequest, NotFound, UnsupportedMediaType

def init_routes_mensagens(flask_app):
    global app
    app = flask_app

    @app.errorhandler(NotFound)
    def handle_NotFound(error):
        response = jsonResposta(str(error),404,"NotFound") 
        return response

    @app.errorhandler(Unauthorized)
    def handle_unauthorized(error):
        response = jsonResposta(str(error),401,"Unauthorized") 
        return response

    @app.errorhandler(BadRequest)
    def handle_unauthorized(error):
        response = jsonResposta(str(error),400,"BadRequest") 
        return response

    @app.errorhandler(UnsupportedMediaType)
    def handle_UnsupportedMediaType(error):
        response = jsonResposta(str("Requisição inválida. Os dados devem ser enviados no formato JSON."),415,"UnsupportedMediaType") 
        return response