# from config.banco import jsonify, db, datetime, os
import jwt
import re
import datetime as ndatetime
from datetime import datetime, timezone
from flask import request, make_response
import time
from werkzeug.exceptions import Unauthorized, BadRequest, NotFound
from flask import Flask, jsonify
import os

def jsonSuccess(dados):
    data = {
        "data": dados,
        "status": "success",
        "code": 200
    }
    return jsonify(data)

def jsonException(erro):
    return jsonify({
        "error": str(erro),
        "status": "Exception",
        "code": 500
    })

def jsonError(erro, codigo):
    data = {
        "data": erro,
        "status": "NOT_FOUND",
        "code": codigo
    }
    return jsonify(data)

def jsonErrorNovo(erro, codigo):
    data = {
        "data": erro,
        "status": "NOT_FOUND",
        "code": codigo
    }
    return data

def jsonResposta(mensagem, codigo, status):
    data = {
        "data": mensagem,
        "status": status,
        "code": codigo
    }
    return jsonify(data)

def listardados(dados):
    dados_listados = []
    for dado in dados:
        dado_listado = {}
        for column in dado.__table__.columns:
            if isinstance(getattr(dado, column.name), datetime):  # Verifica se o campo é do tipo db.DateTime
                dado_listado[column.name] = getattr(dado, column.name).strftime("%Y-%m-%d %H:%M:%S")  # Formata como desejado
            else:
                dado_listado[column.name] = getattr(dado, column.name)
        dados_listados.append(dado_listado)
    return dados_listados


def dataHoraAtual():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def dataHoraAtualPtBR():
    return datetime.now().strftime('%d/%m/%Y %H:%M:%S')

def dataAtualPtBR(data):
    temhora = False
    if ' ' in data:
        temhora = True
    if temhora:
        data = data.strftime('%Y-%m-%d')  # Converte o datetime.date para string antes de dividir
    data_split = data.split()  # Divide a string no formato YYYY-MM-DD
    if temhora:
        data = data_split[0]  # Extrai a parte da data se houver hora
    data_obj = datetime.strptime(data, '%Y-%m-%d')  # Converte a string para um objeto datetime
    data_formatada = data_obj.strftime('%d/%m/%Y')  # Formata a data no formato desejado
    return data_formatada

def dataAtualPtBRB(data):
    # Verificar se 'data' é um objeto datetime
    if isinstance(data, datetime):
        data_str = data.strftime('%Y-%m-%d')
    else:
        data_str = data
    
    # Converter a string para um objeto datetime
    data_obj = datetime.strptime(data_str, '%Y-%m-%d')
    # Formatar a data no formato desejado
    data_formatada = data_obj.strftime('%d/%m/%Y')
    return data_formatada

def dataSHoraAtualPtBR(data):
    # Tentar converter a string para um objeto datetime, tratando data e hora
    try:
        data_obj = datetime.strptime(data, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        # Caso falhe, tentar converter apenas a data
        data_obj = datetime.strptime(data, '%Y-%m-%d')
    
    # Formatar a data no formato desejado
    data_formatada = data_obj.strftime('%d/%m/%Y')
    return data_formatada

def dataAtual():
    return datetime.now().strftime('%Y-%m-%d')


def horaAtual():
    return datetime.now().strftime('%H:%M:%S')

def gerarToken(dados):
    SECRET_KEY = os.getenv("SECRET_KEY")
    expiracao = ndatetime.datetime.utcnow() + ndatetime.timedelta(hours=24)
    # expiracao = ndatetime.datetime.utcnow() + ndatetime.timedelta(minutes=10)
    dados['expiracao'] = int(expiracao.timestamp())
    token = jwt.encode(dados, SECRET_KEY, algorithm='HS256')
    return token

def tempoRestante(token, expiracao):
    agora = datetime.datetime.utcnow()
    tempo_restante = expiracao - agora
    return max(tempo_restante, datetime.timedelta(0))
    

def validarToken(token):
    try:
        SECRET_KEY = os.getenv("SECRET_KEY")
        data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        expiracao = data['expiracao']
        
        agora = int(ndatetime.datetime.utcnow().timestamp())
        restante = expiracao-agora
        data['tempotoken'] = restante
        if restante <= 0:
            raise Unauthorized('Token de acesso inválido!')

        current_user = data
        return current_user
    except jwt.InvalidTokenError:
        raise Unauthorized('Token de acesso inválido!')


def gerarDadosToken():
    auth_header = request.headers.get('Authorization')
    if auth_header is None or not auth_header.startswith('Bearer '):
        raise NotFound("token nao informado!")
    token = auth_header.split(' ')[1]
    
    dadoToken = validarToken(token)

    return dadoToken

def textoLimpo(texto):
    padrao = re.compile(r'[^a-zA-Z0-9]')
    texto_filtrado = padrao.sub('', texto)
    return texto_filtrado

def validar_cpf(cpf):
    # Remove caracteres especiais do CPF
    cpf = re.sub(r'[^0-9]', '', cpf)

    # Verifica se o CPF possui 11 dígitos
    if len(cpf) != 11:
        raise {'codigo':0,'mensagem':"O CPF deve conter 11 dígitos."}

    # Verifica se todos os dígitos do CPF são iguais
    if cpf == cpf[0] * 11:
        raise {'codigo':0,'mensagem':"CPF inválido."}

    # Calcula o primeiro dígito verificador
    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)
    resto = soma % 11
    if resto < 2:
        digito_verificador1 = 0
    else:
        digito_verificador1 = 11 - resto

    # Verifica o primeiro dígito verificador
    if digito_verificador1 != int(cpf[9]):
        raise {'codigo':0,'mensagem':"CPF inválido."}

    # Calcula o segundo dígito verificador
    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)
    resto = soma % 11
    if resto < 2:
        digito_verificador2 = 0
    else:
        digito_verificador2 = 11 - resto

    # Verifica o segundo dígito verificador
    if digito_verificador2 != int(cpf[10]):
        raise {'codigo':0,'mensagem':"CPF inválido."}

    # Se todas as verificações passaram, o CPF é válido
    return True

def formatar_cpf(cpf):
    # Remove caracteres não numéricos do CPF
    cpf = ''.join(filter(str.isdigit, cpf))

    # Insere os pontos e traço no CPF formatado
    cpf_formatado = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

    return cpf_formatado

def formatar_telefone(telefone):
    # Remove todos os caracteres não numéricos do telefone
    telefone = ''.join(filter(str.isdigit, telefone))

    # Verifica se o telefone possui o código de área
    if len(telefone) == 11:
        telefone_formatado = f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"
    elif len(telefone) == 10:
        telefone_formatado = f"({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}"
    else:
        # Se o número não tiver o código de área, apenas adiciona traço
        telefone_formatado = f"{telefone[:-4]}-{telefone[-4:]}"

    return telefone_formatado

def formatar_cep(cep):
    # Remove caracteres não numéricos do CEP
    cep = ''.join(filter(str.isdigit, cep))

    # Insere o hífen no CEP formatado
    cep_formatado = f"{cep[:5]}-{cep[5:]}"

    return cep_formatado

def formatar_para_reais(valor):
    # Converte o valor para string com 2 casas decimais
    valor_str = f"{valor:,.2f}"
    
    # Substitui vírgula por ponto e ponto por vírgula
    valor_str = valor_str.replace(',', 'v').replace('.', ',').replace('v', '.')
    
    # Adiciona o símbolo de moeda
    valor_formatado = f"R$ {valor_str}"
    
    return valor_formatado

def formatarptbr(valor):
    # Converte o valor para string com 2 casas decimais
    valor_str = f"{valor:,.2f}"
    
    # Substitui vírgula por ponto e ponto por vírgula
    valor_str = valor_str.replace(',', 'v').replace('.', ',').replace('v', '.')
    
    # Adiciona o símbolo de moeda
    valor_formatado = f"{valor_str}"
    
    return valor_formatado


def dataExtParaGravacao(date_obj):
    data_string = str(date_obj)
    data_datetime = datetime.strptime(data_string, "%a, %d %b %Y %H:%M:%S %Z")
    data_formatada = data_datetime.strftime("%Y-%m-%d")
    return jsonSuccess(data_formatada) 