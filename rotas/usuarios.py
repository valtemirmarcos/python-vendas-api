app = None  # Placeholder for Flask app instance

def init_routes(flask_app):
    global app
    app = flask_app

    from controllers.usuariosController import usuariosController    
    usuarios_ctl = usuariosController()

    @app.route('/usuarios/cadastrar', methods=['POST'])
    def usuarios_cadastrar():
        return usuarios_ctl.cadastrar()

    @app.route('/usuarios/cadastrarGeral', methods=['POST'])
    def usuarios_cadastrar_geral():
        return usuarios_ctl.cadastrarGeral()

    @app.route('/usuarios/dadosCadastrados')
    def usuarios_dados_cadastrados():
        return usuarios_ctl.dadosCadastrados()

    @app.route('/usuarios/favoritos', methods=['GET'])
    def usuarios_favoritos():
        return usuarios_ctl.usuariosFavoritos()

    @app.route('/usuarios/favoritos/gravar', methods=['POST'])
    def usuarios_favoritos_gravar():
        return usuarios_ctl.favoritosGravar()

    @app.route('/usuarios/favoritos/remover', methods=['POST'])
    def usuarios_favoritos_remover():
        return usuarios_ctl.favoritosRemover()

    @app.route('/usuarios/consultaCep', methods=['GET'])
    def usuarios_consulta_cep():
        return usuarios_ctl.consultaCep()

    @app.route('/usuarios/alterarDadosPessoais', methods=['POST'])
    def alterar_dados_pessoais():
        return usuarios_ctl.alterarDadosPessoais()

    @app.route('/usuarios/alterarEndereco', methods=['POST'])
    def alterar_endereco():
        return usuarios_ctl.alterarEndereco()

    @app.route('/login', methods=['POST'])
    def usuarios_login():
        return usuarios_ctl.login()

    @app.route('/login/alterarSenha', methods=['POST'])
    def usuarios_alterar_senha():
        return usuarios_ctl.alterarSenha()

    @app.route('/usuarios/listarEnderecos', methods=['get'])
    def usuarios_listar_enderecos():
        return usuarios_ctl.listarEnderecos()

    @app.route('/enviarEmail', methods=['POST'])
    def enviar_email():
        return usuarios_ctl.enviarEmail()


