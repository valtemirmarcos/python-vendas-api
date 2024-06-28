from flasgger import swag_from
from config.docs import documentos
app = None

def init_routes_produtos(flask_app):
    global app
    app = flask_app
    from controllers.produtosController import produtosController
    produtos_ctrl = produtosController()

    # Define uma rota para o caminho raiz ('/')
    swagger = documentos()

    @app.route('/')
    @swag_from(swagger.inicio())
    def index():
        return produtos_ctrl.inicio()

    @app.route('/produtos')
    @swag_from(swagger.produtos())
    def produtos_ativos():
        return produtos_ctrl.produtosAtivos()

    @app.route('/produtos/<int:produto_id>')
    def buscar_produto(produto_id):
        return produtos_ctrl.buscarProduto(produto_id)

    @app.route('/produtos/cadastrar', methods=['POST'])
    def cadastrar_produtos():
        return produtos_ctrl.cadastrarProdutos()

    @app.route('/produtos/alterar', methods=['POST'])
    def alterar_produtos():
        return produtos_ctrl.alterarProdutos()

    @app.route('/produtos/sdelete', methods=['POST'])
    def sdelete_produtos():
        return produtos_ctrl.sdeleteProdutos()

    @app.route('/produtos/upload/<int:produto_id>', methods=['POST'])
    def upload_produtos(produto_id):
        return produtos_ctrl.uploadProdutos(app, produto_id)

