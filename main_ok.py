from config.banco import app,db,jsonify
import rotas.produtos
import rotas.usuarios
import rotas.mensagens
import rotas.vendas


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
