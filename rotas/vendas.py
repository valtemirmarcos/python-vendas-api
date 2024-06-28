app = None

def init_route_vendas(flask_app):
    global app
    app = flask_app
    
    from controllers.vendasController import vendasController
    vendas_ctl = vendasController()

    @app.route('/vendas/gerar', methods=['POST'])
    def gerar_vendas():
        return vendas_ctl.gerarVendas()

    @app.route('/vendas/pedidos', methods=['GET'])
    def listar_pedidos():
        return vendas_ctl.vendasPedidos()

    @app.route('/vendas/pedidos/itens/<int:pedido_id>')
    def buscar_pedido_item(pedido_id):
        return vendas_ctl.buscarPedidoItem(pedido_id)

    @app.route('/vendas/calcularFrete', methods=['POST'])
    def frete_vendas():
        return vendas_ctl.freteVendas()