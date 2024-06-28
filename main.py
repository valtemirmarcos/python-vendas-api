from flask import Flask
from config.db import db, init_app, bcrypt
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from sqlalchemy import Numeric

from rotas.produtos import init_routes_produtos
from rotas.usuarios import init_routes, app  # Import functions and app instance
from rotas.mensagens import init_routes_mensagens
from rotas.vendas import init_route_vendas
from rotas.imgs import init_route_imagens
from flasgger import Swagger, swag_from

app = Flask(__name__)
init_app(app)

swagger = Swagger(app)

init_routes(app)  # Initialize routes using the app instance
init_routes_mensagens(app)
init_routes_produtos(app)
init_route_vendas(app)
init_route_imagens(app)




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)