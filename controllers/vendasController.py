from config.db import db
from sqlalchemy.exc import SQLAlchemyError
from config.funcoes import jsonSuccess, listardados,gerarDadosToken,dataHoraAtual,dataAtualPtBR, formatarptbr, dataAtualPtBRB, dataSHoraAtualPtBR
from models import Pedido, PedidoItem, Produto
from flask import request
import datetime as datetime
from werkzeug.exceptions import Unauthorized, BadRequest, NotFound, UnsupportedMediaType
# from correios_frete import Freight

class vendasController():

    def gerarVendas(self):
        
        dadoToken = gerarDadosToken()
        
        usuarioId = dadoToken['id']
        
        if not request.json:
            raise UnsupportedMediaType('Requisição inválida. Os dados devem ser enviados no formato JSON.')
        
        if 'endereco_id' not in request.json:
            raise NotFound('faltou selecionar o endereco')    

        if 'pagamento_id' not in request.json:
            raise NotFound('faltou selecionar o tipo de pagamento')   

        if 'itens' not in request.json:
            raise NotFound('nao foram encontrados itens para esta venda')   

        # pedidoID = 1
        # pedidosItens = True
        pedidoID = self.gerarPedido(usuarioId)
        pedidosItens = self.gerarPedidoItens(pedidoID)
        baixarPedido = False
        if pedidosItens:
             baixarPedido = self.baixaPedidos(pedidoID)
        if baixarPedido:
            return jsonSuccess({'mensagem':"Pedido realizada com sucesso","nrPedido":pedidoID})
        else:
            raise BadRequest("Operacao nao completada")
          

    def gerarPedido(self, usuarioId):
        itens = request.json['itens']
        
        total = sum(item['valor_total'] for item in itens)
        observacoes = ', '.join(item['obs'] for item in itens if 'obs' in item)
        
        novo_pedido = Pedido(
            user_id=usuarioId,
            endereco_id=request.json['endereco_id'],
            status=1,
            valor_total=total,
            valor_frete=request.json['valor_frete'],
            tipo_pagamento=request.json['pagamento_id'],
            obs=observacoes,
            created_at=dataHoraAtual(),
            updated_at=dataHoraAtual()
        )
        try:
            db.session.add(novo_pedido)
            db.session.commit()
            return novo_pedido.id
        except SQLAlchemyError as e:
            db.session.rollback()
            raise BadRequest("falha ao cadastrar o Pedido"+str(e))
        return jsonPedido

    def gerarPedidoItens(self, pedidoID):
        dadoToken = gerarDadosToken()
        usuarioId = dadoToken['id']
        itens = request.json['itens']
        pedido_itens = []
        try:
            for item in itens:
                del(item['obs'], item['valor_total'],item['tipo_pagamento'])
                item['created_at']=dataHoraAtual()
                item['updated_at']=dataHoraAtual()
                item['user_id'] = usuarioId
                item['pedido_id'] = pedidoID
                pedido_item = PedidoItem(**item)
                pedido_itens.append(pedido_item)
            
            db.session.bulk_save_objects(pedido_itens)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise BadRequest("Erro ao cadastrar Produto: " + str(e))

    def baixaPedidos(self, pedidoID):
        pedidosItens = PedidoItem.query.filter_by(pedido_id=pedidoID).all()
        if not pedidosItens:
            raise NotFound('Nenhum item encontrado para este pedido.')
        
        for pedidoItem in pedidosItens:
            item = listardados([pedidoItem])[0]
            update_produto = Produto.query.filter_by(id=item['produto_id']).first()
            if(update_produto):
                update_produto.updated_at=dataHoraAtual()
                update_produto.estoque = update_produto.estoque-int(item['quantidade'])
                db.session.commit()
            else:
                raise NotFound('Pedido '+str(pedidoID)+' nao encontrado')

        return True

    def vendasPedidos(self):
        dadoToken = gerarDadosToken()
        usuarioId = str(dadoToken['id'])
        
        result = []
        pedidos = Pedido.query.filter_by(user_id=usuarioId).all()
        if not pedidos:
            raise NotFound('Nenhum pedido encontrado para este usuario.')
        
        for pedido in pedidos:
            dadosPedido = listardados([pedido])[0]
            dadosItensPedido = [listardados([item])[0] for item in pedido.pedidoitem]
            
            for dadoItemPedido in dadosItensPedido:
                produto = next(produto for produto in pedido.pedidoitem if produto.id == dadoItemPedido['id']).produto
                dadoItemPedido['produto'] = listardados([produto])[0]

            frete = dadosPedido['valor_frete'] if dadosPedido['valor_frete'] is not None else 0
            saida = {
                'pedidoId':dadosPedido['id'],
                'nrPedido':str(dadosPedido['id']).zfill(5),
                'data':dataSHoraAtualPtBR(dadosPedido['created_at']),
                'valor_frete':frete,
                'valor_total':float(dadosPedido['valor_total']),
                'total_com_frete':float(dadosPedido['valor_total'])+float(frete),
                "zitensPedido":dadosItensPedido
            }
            result.append(saida)

        return jsonSuccess(result)

    def buscarPedidoItem(self, pedido_id):
        dadoToken = gerarDadosToken()
        usuarioId = dadoToken['id']
        buscarItemPedido = PedidoItem.query.filter_by(pedido_id=pedido_id,user_id=usuarioId).all()
        result = []
        totalPedido = 0
        vlFrete = 0
        if not buscarItemPedido:
            raise NotFound('Nenhum item encontrado para este pedido.')
        for pedidoItem in buscarItemPedido:

            # produto = [recProduto for produto in pedidoItem.produto]
            item = listardados([pedidoItem])[0]
            pedido = listardados([pedidoItem.pedido])[0]
            produto = listardados([pedidoItem.produto])[0]
            totalPedido = pedido['valor_total']
            vlFrete = pedido['valor_frete']
            jsonSaida = {
                'itemID':item['id'],
                'produto':produto['produto'],
                'vlUnitario':formatarptbr(produto['vlvenda']),
                'quantidade':int(item['quantidade']),
                'totalItem':formatarptbr(produto['vlvenda']*item['quantidade'])
            }

            result.append(jsonSaida)
        
        response = {
            'items': result,
            'totalPedido': formatarptbr(totalPedido),
            'totalFrete':formatarptbr(vlFrete),
            'totalGeral':formatarptbr(totalPedido+vlFrete)
        }
        return jsonSuccess(response) 

    def freteVendas(self):
        # freight = Freight(
        #     cep_origem=request.json['cep_origem'],
        #     cep_destino=request.json['cep_destino'],
        #     peso=weighrequest.json['peso'],
        #     formato=1,  # Formato do pacote: 1 para caixa/pacote, 2 para rolo/prisma, 3 para envelope
        #     comprimento=20.0,  # Comprimento do pacote em cm
        #     altura=20.0,  # Altura do pacote em cm
        #     largura=20.0,  # Largura do pacote em cm
        #     diametro=0.0,  # Diâmetro do pacote em cm
        #     mao_propria='N',  # Entrega com mão própria (S ou N)
        #     valor_declarado=0.0,  # Valor declarado do pacote em R$
        #     aviso_recebimento='N'  # Aviso de recebimento (S ou N)
        # )
        # tarifas = freight.calculate()
        return jsonSuccess("ok") 