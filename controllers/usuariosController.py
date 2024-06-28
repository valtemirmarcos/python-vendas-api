from config.db import db, bcrypt
from sqlalchemy.exc import SQLAlchemyError
from config.funcoes import (
    jsonSuccess, jsonException,
    listardados, dataHoraAtual, gerarToken, 
    validarToken, textoLimpo, validar_cpf, 
    formatar_cpf, dataAtualPtBR,formatar_telefone,
    formatar_cep, gerarDadosToken, dataExtParaGravacao
)
from models import User, Cliente, Endereco, Favorito
from flask import request
import re
import json
from werkzeug.exceptions import Unauthorized, BadRequest, NotFound
import brazilcep
import os

from datetime import datetime, timezone

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class usuariosController():
    def cadastrar(self):
        data = request.json
        email=data.get('email')
        senha=data.get('password')
        senha_hasheada = bcrypt.generate_password_hash(senha).decode('utf-8')

        confEmail = User.query.filter_by(email=email)
        if confEmail.first():
            raise BadRequest("Email já cadastrado")
        

        novo_usuario = User(
            email=email,
            password=senha_hasheada,
            created_at=dataHoraAtual(),
            updated_at=dataHoraAtual()
        )
        try:
            # Adicionar o novo usuário ao banco de dados
            db.session.add(novo_usuario)
            db.session.commit()
            return jsonSuccess({'message': 'Usuário cadastrado com sucesso', 'dados': confEmail.first().to_dict()})
        except SQLAlchemyError as e:
            # Em caso de erro, desfaz as alterações e retorna um erro
            db.session.rollback()
            raise Unauthorized("Erro ao cadastrar usuário: " + str(e))

    def login(self):
        data = request.json
        email=data.get('email')
        senha=data.get('password')
        
        confEmail = User.query.filter_by(email=email)
        if not confEmail.first():
            raise NotFound("E-mail não existe")

        senha_hash = confEmail.first().password
        check_password = bcrypt.check_password_hash(senha_hash, senha)
        
        if not check_password:
            raise Unauthorized("Senha invalida")     

        dados = confEmail.first()

        dados_usuario = {
            "id":dados.id,
            "email":dados.email
        }
        
        token = gerarToken(dados_usuario)

        return jsonSuccess(token)

    def cadastrarGeral(self):


        idUsuario = self.cadastrarUsuario()
        if idUsuario['id'] is None:
            raise BadRequest(idUsuario['mensagem'])

        idUsuario = idUsuario['id']
        idCliente = self.cadastroCliente(idUsuario)
        if idCliente['id'] is None:
            raise BadRequest(idCliente['mensagem'])

        idCliente = idCliente['id']
        idEndereco = self.cadastroEndereco(idCliente)
        if idEndereco['id'] is None:
            raise BadRequest(idEndereco['mensagem'])

        dados = self.mostrarCadastrados(idUsuario)
        return jsonSuccess({"mensagem":"Usuario cadastrado com sucesso","dados":dados})
        
    def mostrarCadastrados(self, idUsuario):
        try:
            usuario = User.query.filter_by(id=idUsuario).first()
            cliente = usuario.cliente
            # primeiro_endereco = cliente.enderecos[0]
            endereco = [pendereco for pendereco in cliente.enderecos if pendereco.status == 'C']
            if endereco:
                id_endereco = endereco[0].id
                cep = endereco[0].cep
                logradouro = endereco[0].logradouro
                numero = endereco[0].numero
                referencia = endereco[0].referencia
                cidade = endereco[0].cidade
                uf = endereco[0].uf
                complemento = " " if endereco[0].complemento is None else endereco[0].complemento
            else:
                id_endereco = None
                cep = None
                logradouro = None
                numero = None
                referencia = None
                cidade = None
                uf = None
                complemento = None

            dados = {
                'id_usuario':usuario.id,
                'id_cliente':cliente.id,
                'id_endereco':id_endereco,
                'email':usuario.email,
                'nome': cliente.nome_completo,
                'cpf': formatar_cpf(cliente.cpf),
                'dt_nascimento': cliente.dt_nascimento,
                'fone': formatar_telefone(cliente.fone),
                'cep': cep,
                'logradouro':logradouro,
                'numero':numero,
                'referencia':referencia,
                'cidade':cidade,
                'uf':uf,
                'complemento':complemento
            }
            return dados

        except SQLAlchemyError as e:
            return {'codigo': 1, 'mensagem': "falha ao exibir os dados", 'id': None}

    def cadastroEndereco(self, idCliente):
        data = request.json
        cep = textoLimpo(data.get('cep'))
        buscaEndereco = Endereco.query.filter_by(cliente_id=idCliente, status='C')
        if buscaEndereco.first():
            updateEndereco = buscaEndereco.first()
            updateEndereco.cep = cep
            updateEndereco.logradouro = data.get('logradouro')
            updateEndereco.numero = data.get('numero')
            updateEndereco.referencia = data.get('referencia')
            updateEndereco.cidade = data.get('cidade')
            updateEndereco.uf = data.get('uf')
            updateEndereco.updated_at = dataHoraAtual()
            updateEndereco.titulo = data.get('titulo') if 'titulo' in data and data['titulo'] is not None else "Cadastro"
            try:
                db.session.commit()
                return {'codigo': 1, 'mensagem': "Endereco atualizado com sucesso", 'id': updateEndereco.id}
            except SQLAlchemyError as e:
                db.session.rollback()
                return {'codigo':0,'id':None,'erro':str(e)} 
        else:
            try:
                endereco = Endereco(
                    cliente_id = idCliente,
                    logradouro = data.get('logradouro'),
                    titulo=data.get('titulo') if 'titulo' in data and data['titulo'] is not None else "Cadastro",
                    numero = data.get('numero'),
                    cep = cep,
                    referencia = data.get('referencia'),
                    cidade = data.get('cidade'),
                    uf = data.get('uf'),
                    status = data.get('status') if 'status' in data and data['status'] is not None else "C",
                    created_at = dataHoraAtual(),
                    updated_at = dataHoraAtual()
                )
                db.session.add(endereco)
                db.session.commit()
                return {'codigo': 1, 'mensagem': "Endereco inserido com sucesso", 'id': endereco.id}
            except SQLAlchemyError as e:
                db.session.rollback()
                buscaCliente = Cliente.query.filter_by(id=idCliente).first()
                if buscaCliente:
                    userId = buscaCliente['user_id']
                    clienteID = buscaCliente['id']
                    User.query.filter_by(id=userId).delete()
                    Cliente.query.filter_by(id=clienteID).delete()

                return {'codigo':0,'id':None,'erro':str(e)} 

    def cadastroCliente(self, idUsuario):
        data = request.json
        cpf = textoLimpo(data.get('cpf'))
        try:
            validar_cpf(cpf)
            # Se o CPF for válido, faça as operações necessárias e retorne uma resposta apropriada
        except Exception as e:
            return {'codigo':0,'mensagem':"cpf invalido",'id':None}

        confCpf = Cliente.query
        # if confCpf.filter_by(cpf=cpf).first():
        #     return {'codigo': 1, 'mensagem': "Cpf ja cadastrado no sistema",'id':None}

        buscaId = confCpf.filter_by(user_id=idUsuario).first()
        if buscaId:
            buscaId.nome_completo = data.get('nome')
            buscaId.dt_nascimento = data.get('dt_nascimento')
            buscaId.cpf = cpf
            buscaId.fone = textoLimpo(data.get('fone'))
            buscaId.updated_at = dataHoraAtual()
            try:
                db.session.commit()
                return {'codigo': 1, 'mensagem': "Cliente atualizado com sucesso", 'id': buscaId.id}
            except SQLAlchemyError as e:
                db.session.rollback()
                return {'codigo':0,'id':None,'erro':str(e)} 
        else:
            try:
                cliente = Cliente(
                    user_id=idUsuario,
                    nome_completo=data.get('nome'),
                    cpf=cpf,
                    dt_nascimento=data.get('dt_nascimento'),
                    fone=textoLimpo(data.get('fone')),
                    created_at=dataHoraAtual(),
                    updated_at=dataHoraAtual()
                )
                # Adicionar o novo usuário ao banco de dados
                db.session.add(cliente)
                db.session.commit()
                return {'codigo':1,'mensagem': "Cliente inserido com sucesso",'id':cliente.id}
            except SQLAlchemyError as e:
                # Em caso de erro, desfaz as alterações e retorna um erro
                delete_user = User.query.filter_by(id=idUsuario).delete()
                db.session.rollback()
                return {'codigo':0,'id':None,'erro':str(e)}    

    def cadastrarUsuario(self):
        data = request.json
        email=data.get('email')
        senha=data.get('password')
        senha_hasheada = bcrypt.generate_password_hash(senha).decode('utf-8')

        confEmail = User.query.filter_by(email=email)
        if confEmail.first():
            return {'codigo':0,'mensagem': "Email já cadastrado",'id':None}

        if len(senha) < 8:
            return {'codigo':0,'mensagem': "A senha deve ter no mínimo 8 caracteres.",'id':None}
        
        # Verificar caracteres especiais
        if not re.search("[a-z]", senha) or not re.search("[A-Z]", senha) or not re.search("[0-9]", senha) or not re.search("[!@#$%^&*]", senha):
            return {'codigo':0,'mensagem': "A senha deve conter pelo menos uma letra maiúscula, uma letra minúscula, um número e um caractere especial.",'id':None}    
        try:
            novo_usuario = User(
                email=email,
                password=senha_hasheada,
                created_at=dataHoraAtual(),
                updated_at=dataHoraAtual()
            )             
            # Adicionar o novo usuário ao banco de dados
            db.session.add(novo_usuario)
            db.session.commit()
            return {'codigo':1,'id':confEmail.first().id}
        except SQLAlchemyError as e:
            # Em caso de erro, desfaz as alterações e retorna um erro
            db.session.rollback()
            return {'codigo':0,'id':None}

    def dadosCadastrados(self):
        dadoToken = gerarDadosToken()
        idUsuario = dadoToken['id']
        dadosCadstrados = self.mostrarCadastrados(idUsuario)
        return jsonSuccess(dadosCadstrados)

    def alterarSenha(self):
        dadoToken = gerarDadosToken()
        data = request.json
        senhaAtual=data.get('senhaAtual')
        novaSenha=data.get('novaSenha')
        confsenha=data.get('confSenha')

        confEmail = User.query.filter_by(id=dadoToken['id'])
        if not confEmail.first():
            raise NotFound("Usuario não existe")

        senha_hash = confEmail.first().password
        check_password = bcrypt.check_password_hash(senha_hash, senhaAtual)
        
        if not check_password:
            raise NotFound("Senha invalida")      

        if len(novaSenha) < 8:
            raise NotFound("A senha deve ter no mínimo 8 caracteres.")
        
        # Verificar caracteres especiais
        if not re.search("[a-z]", novaSenha) or not re.search("[A-Z]", novaSenha) or not re.search("[0-9]", novaSenha) or not re.search("[!@#$%^&*]", novaSenha):
            raise NotFound("A senha deve conter pelo menos uma letra maiúscula, uma letra minúscula, um número e um caractere especial.")

        if novaSenha!=confsenha:
            raise NotFound("Senhas não conferem")  

        senha_hasheada = bcrypt.generate_password_hash(novaSenha).decode('utf-8')

        update = confEmail.first()
        if(update):
            update.password = senha_hasheada
            update.updated_at = dataHoraAtual()
            try:
                db.session.commit()
                resposta = {'codigo': 1, 'mensagem': "senha alterada com sucesso"}
            except SQLAlchemyError as e:
                db.session.rollback()
                resposta = {'codigo':0,'id':None,'erro':str(e)} 
                

        return jsonSuccess(resposta)

    def favoritosGravar(self):
        
        if not request.json:
            raise NotFound('Requisição inválida. Os dados devem ser enviados no formato JSON.')
        
        if 'produto_id' not in request.json:
            raise NotFound('O campo "produto_id" é obrigatório na solicitação.')       
        
        dadoToken = gerarDadosToken()
        
        data = request.json
        
        produtoId = data.get('produto_id')
        usuarioId = dadoToken['id']
        buscaFavorito = Favorito.query.filter_by(user_id=usuarioId, produto_id=produtoId)
        if buscaFavorito.first():
            dadoFavorito = buscaFavorito.first()
            dadoFavorito.updated_at = dataHoraAtual()
            dadoFavorito.deleted_at = None
            try:
                db.session.commit()
                return jsonSuccess("readicionado os favoritos!")
            except SQLAlchemyError as e:
                db.session.rollback()
                raise BadRequest("item nao favoritado") 
        else:
            try:
                favorito = Favorito(
                    user_id=usuarioId,
                    produto_id=produtoId,
                    created_at=dataHoraAtual(),
                    updated_at=dataHoraAtual()
                )
                db.session.add(favorito)
                db.session.commit()
                return jsonSuccess("item favoritado com sucesso!")
            except SQLAlchemyError as e:
                db.session.rollback()
                raise BadRequest("item nao favoritado") 

    def favoritosRemover(self):
        if not request.json:
            raise NotFound('Requisição inválida. Os dados devem ser enviados no formato JSON.')
        
        if 'produto_id' not in request.json:
            raise NotFound('O campo "produto_id" é obrigatório na solicitação.')       
        
        dadoToken = gerarDadosToken()
        
        data = request.json
        
        produtoId = data.get('produto_id')
        usuarioId = dadoToken['id']
        buscaFavorito = Favorito.query.filter_by(user_id=usuarioId, produto_id=produtoId)
        if buscaFavorito.first():
            dadoFavorito = buscaFavorito.first()
            dadoFavorito.updated_at = dataHoraAtual()
            dadoFavorito.deleted_at = dataHoraAtual()
            try:
                db.session.commit()
                return jsonSuccess("removido dos favoritos!")
            except SQLAlchemyError as e:
                db.session.rollback()
                raise BadRequest("item nao favoritado") 

    def usuariosFavoritos(self):
        dadoToken = gerarDadosToken()
        usuarioId = dadoToken['id']
        buscaFavoritos = Favorito.query.filter_by(user_id=usuarioId, deleted_at=None).all()
        result = []
        for buscaFavorito in buscaFavoritos:
            produto_data = listardados([buscaFavorito])[0]
            produto = buscaFavorito.produto  # Obter o objeto Produto associado ao Favorito
            produto_data['item'] = {
                'id': produto.id,
                'produto': produto.produto,
                'descricao': produto.descricao,
                'estoque': float(produto.estoque),  # Convertendo para float se for necessário
                'medida': produto.medida,
                'vlcompra': float(produto.vlcompra),  # Convertendo para float se for necessário
                'vlvenda': float(produto.vlvenda),  # Convertendo para float se for necessário
                'status': produto.status,
            }
            foto = [foto.foto for foto in produto.produtosfotos if foto.tipo == 1]
            produto_data['foto'] = foto[0] if foto else f"{os.getenv('API_URL')}/static/imgs/semfoto.jpeg"
            result.append(produto_data)

        return jsonSuccess(result)
    
    def consultaCep(self):
        cep = request.args.get('cep')
        address = brazilcep.get_address_from_cep(cep)
        rua = address['street']
        if '(' in rua:
            arrua = address['street'].split('(')
            rua = arrua[0]
        address['street'] = rua
        return jsonSuccess(address)

    def listarEnderecos(self):
        dadoToken = gerarDadosToken()
        usuarioId = dadoToken['id']
        buscaEnderecos = Endereco.query.filter_by(cliente_id=usuarioId).all()
        result = []
        for buscaEndereco in buscaEnderecos:
            cliente = buscaEndereco.cliente
            dados = listardados([buscaEndereco])[0]
            dados['cliente'] = listardados([cliente])[0]
            result.append(dados)

        return jsonSuccess(result)

    def enviarEmail(self):
        # Configurações do servidor SMTP rhenus
        # smtp_server = 'smtp.office365.com'
        # smtp_port = 587
        # username = 'comunicado@br.rhenus.com'  # Substitua pelo seu email
        # password = 'Rhenus#97531'  # Substitua pela sua senha
        # Configurações do email
        # from_email = 'comunicado@br.rhenus.com'

        # Configurações do servidor SMTP
        smtp_server = os.getenv('SMTP_SERVER')
        smtp_port = os.getenv('SMTP_PORT')
        username = os.getenv('USERNAME')  # Substitua pelo seu email
        password = os.getenv('PASSWORD')  # Substitua pela sua senha

        
        # Configurações do email
        from_email = 'nao-responda@d2p.com.br'
        to_email = request.json.get('email')
        subject = request.json.get('assunto')
        body = request.json.get('conteudo')
        # Criando a mensagem do email
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject

        # Adicionando o corpo do email
        msg.attach(MIMEText(body, 'plain'))

        try:
            # Conectando ao servidor SMTP e enviando o email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()  # Usando TLS para segurança
            server.login(username, password)
            server.sendmail(from_email, to_email, msg.as_string())
            server.quit()

            return jsonSuccess("enviado com sucesso")
        except Exception as e:
            return jsonException({'mensagem':"falha ao enviar",'erro':e})
       