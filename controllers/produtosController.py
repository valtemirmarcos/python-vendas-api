from config.db import db, bcrypt
from sqlalchemy.exc import SQLAlchemyError
from config.funcoes import jsonSuccess, listardados,gerarDadosToken,dataHoraAtual, os, formatarptbr
from models import Produto, ProdutoFoto
from flask import request, send_from_directory, abort
import datetime as datetime
from werkzeug.exceptions import Unauthorized, BadRequest, NotFound
from werkzeug.utils import secure_filename
import os


class produtosController():
    def inicio(self):
        result = []
        produtos = Produto.query.filter_by(status=1).all()
        for produto in produtos:
            produto_data = listardados([produto])[0]
            fotos = [foto.foto for foto in produto.produtosfotos if foto.tipo == 1]
            produto_data['fotos'] = fotos[0] if fotos else f"{os.getenv('API_URL')}/static/imgs/semfoto.jpeg"
            produto_data['vlvenda'] = formatarptbr(produto_data['vlvenda'])
            result.append(produto_data)
        return jsonSuccess(result)

    def produtosAtivos(self):

        page = request.args.get('page', 1, type=int)
        per_page = 15  # Número de produtos por página

        # Consulta os produtos ativos e inclui os dados das fotos associadas a cada produto
        produtos = Produto.query.filter_by(status=1)
        if 'ordena' in request.args:
            produtos = produtos.order_by(getattr(Produto, request.args['ordena']))

        if 'ordenadesc' in request.args:
            produtos = produtos.order_by(getattr(Produto, request.args['ordenadesc']).desc())

        if 'filtro' in request.args:
            filtro = request.args['filtro']
            produtos = produtos.filter(
                (
                    (Produto.produto.like(f'%{filtro}%')) |
                    (Produto.descricao.like(f'%{filtro}%')) |
                    (Produto.medida.like(f'%{filtro}%')) 
                )
            )
        
        produtos_paginados = produtos.paginate(page=page, per_page=per_page, error_out=False)

        result = []
        if produtos_paginados:
            usuario=None
            if 'userId' in request.args and request.args.get("userId")!=None:
                usuario = request.args.get("userId")
            
            for produto in produtos_paginados.items:
                produto_data = listardados([produto])[0]
                fotos = [foto.foto for foto in produto.produtosfotos if foto.tipo == 1]
                produto_data['fotos'] = fotos[0] if fotos else f"{os.getenv('API_URL')}/static/imgs/semfoto.jpeg"
                produto_data['vlvenda'] = float(produto_data['vlvenda'])
                produto_data['estoque'] = float(produto_data['estoque'])
                produto_data['vlvendaReal'] = formatarptbr(produto_data['vlvenda'])
                produto_data['estoqueReal'] = formatarptbr(produto_data['estoque'])
                isfavorito = any(usuario!= None and favorito.produto_id==produto_data['id'] and favorito.deleted_at == None for favorito in produto.produtosfavoritos)
                produto_data['favorito'] = 1 if isfavorito else 0
                result.append(produto_data)
                
            return jsonSuccess({
                'produtos': result,
                'pagina_atual': produtos_paginados.page,
                'total_paginas': produtos_paginados.pages,
                'total_produtos': produtos_paginados.total
            })
        else:
            raise NotFound(unescape("Produto não encontrado"))

    def buscarProduto(self, produto_id):
        # Consulta os produtos ativos e inclui os dados das fotos associadas a cada produto
        produto = Produto.query.filter_by(id=produto_id,status=1).first()
        if produto:
            produto_data = listardados([produto])[0]
            fotos = [foto.foto for foto in produto.produtosfotos]
            produto_data['fotos'] = fotos
            fotoCapa = [foto.foto for foto in produto.produtosfotos if foto.tipo == 1]
            produto_data['fotoCapa'] = fotoCapa[0] if fotos else f"{os.getenv('API_URL')}/static/imgs/semfoto.jpeg"
            produto_data['vlvenda'] = float(produto_data['vlvenda'])
            produto_data['estoque'] = float(produto_data['estoque'])
            produto_data['vlvendaReal'] = formatarptbr(produto_data['vlvenda'])
            produto_data['estoqueReal'] = formatarptbr(produto_data['estoque'])
            return jsonSuccess(produto_data)
        else:
            raise NotFound("Produto não encontrado")
    
    def cadastrarProdutos(self):
        dadoToken = gerarDadosToken()
        dados = request.json

        try:
            produtos = []
            for dado in dados:
                dado['created_at']=dataHoraAtual()
                dado['updated_at']=dataHoraAtual()
                produto = Produto(**dado)
                produtos.append(produto)

            db.session.bulk_save_objects(produtos)
            db.session.commit()
            return jsonSuccess({'message': 'Produto(s) cadastrados com sucesso'})
        except SQLAlchemyError as e:
            db.session.rollback()
            raise BadRequest("Erro ao cadastrar Produto: " + str(e))

    def alterarProdutos(self):
        dadoToken = gerarDadosToken()
        dados = request.json

        try:
            produtos = []
            for dado in dados:
                if 'id' not in dado:
                    raise NotFound('esta faltando o id do produto '+dado['produto'])  

                confProduto = Produto.query.filter_by(id=dado['id'])
                if not confProduto.first():
                    raise NotFound('codigo nao existe do produto '+dado['produto'])
                
                update = confProduto.first()
                if(update):
                    update.updated_at = dataHoraAtual()
                    update.produto = dado['produto']
                    update.descricao = dado['descricao']
                    update.medida = dado['medida']
                    update.vlcompra = dado['vlcompra']
                    update.vlvenda = dado['vlvenda']
                    update.status = dado['status']

                    db.session.commit()
            return jsonSuccess({'message': 'Produto(s) alterados com sucesso'})
        except SQLAlchemyError as e:
            # db.session.rollback()
            raise BadRequest("Erro ao alterar Produto: " + str(e))

    def sdeleteProdutos(self):
        dadoToken = gerarDadosToken()
        dados = request.json
        erros = []
        try:
            produtos = []
            for dado in dados:
                if 'id' not in dado:
                    raise NotFound('esta faltando o id do produto '+dado['produto'])  

                confProduto = Produto.itemAtivo(dado['id'])
                if not confProduto.first():
                    erros.append(str(dado['id']))
                    continue
                
                update = confProduto.first()
                if(update):
                    update.soft_delete()
                    db.session.commit()
            total_elementos = len(erros)
            if total_elementos > 0:
                itens_com_erro = ', '.join(erros)
                return jsonSuccess({'message': 'itens nao existem no banco:'+itens_com_erro})

            return jsonSuccess({'message': 'Produto(s) removidos com sucesso'})
        except SQLAlchemyError as e:
            # db.session.rollback()
            raise BadRequest("Erro ao remover Produto: " + str(e))

    def uploadProdutos(self, app, produto_id):
        dadoToken = gerarDadosToken()

        jsonext = request.form
        if not 'tipo' in jsonext:
            raise BadRequest("faltou selecionar o tipo")
            
        UPLOAD_FOLDER = 'static/imgs'
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        url_api = os.getenv("API_URL")
        # return jsonSuccess(url_api)

        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

        if 'file' not in request.files:
            raise BadRequest("arquivo nao selecionado")

        file = request.files['file']
        if file.filename == '':
            raise BadRequest("nova invalido ou arquivo nao selecionado")
        
        if file and self.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'],filename)
            file.save(filepath)
            if os.path.exists(filepath):
                file_url = f"{url_api}/{UPLOAD_FOLDER}/{filename}"

                dados = {
                    'produto_id':produto_id,
                    'foto':file_url,
                    'tipo':jsonext.get('tipo'),
                }
                self.inserirFotoBanco(dados)
                return jsonSuccess({"message": f"arquivo {filename} inserido com sucesso", "file_url": file_url})

        raise BadRequest("Tipo de arquivo não permitido")

    def allowed_file(self, filename):
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def inserirFotoBanco(self, dados):
        buscarFoto = ProdutoFoto.ativo().filter_by(produto_id=dados['produto_id'], foto=dados['foto'])
        update = buscarFoto.first()
        if update:
            update.updated_at = dataHoraAtual()
            update.tipo=dados['tipo']
            update.foto=dados['foto']
            db.session.commit()
        else:
            nova_foto = ProdutoFoto(
                produto_id=dados['produto_id'],
                foto=dados['foto'],
                tipo=dados['tipo'],
                created_at=dataHoraAtual(),
                updated_at=dataHoraAtual()
            )
            try:
                db.session.add(nova_foto)
                db.session.commit()
            except SQLAlchemyError as e:
                db.session.rollback()
                raise Unauthorized("Erro ao cadastrar foto: " + str(e))