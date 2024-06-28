from datetime import datetime
from main import db  
from sqlalchemy import Numeric
from config.db import db, bcrypt
from config.funcoes import dataHoraAtual

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    deleted_at = db.Column(db.DateTime)

    cliente = db.relationship('Cliente',uselist=False, back_populates='user')
    pedidoitens = db.relationship('PedidoItem', back_populates='user')
    produtosfavoritos = db.relationship('Favorito', back_populates='user')
    pedidos = db.relationship('Pedido', back_populates='user')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            # Adicione outros campos se desejar
        }

    def soft_delete(self):
        self.deleted_at = dataHoraAtual()
        self.updated_at = dataHoraAtual()

    def restaurar(self):
        self.deleted_at = None
        self.updated_at = dataHoraAtual()    

    def __repr__(self):
        return '<User %r>' % self.email

class Cliente(db.Model):
    __tablename__ = 'clientes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    nome_completo = db.Column(db.String(120),nullable=False)
    cpf = db.Column(db.String(20),nullable=False)
    dt_nascimento = db.Column(db.Date,nullable=False)
    fone = db.Column(db.String(30))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    deleted_at = db.Column(db.DateTime)

    user = db.relationship('User',uselist=False, back_populates='cliente')
    enderecos = db.relationship('Endereco', back_populates='cliente')

    def soft_delete(self):
        self.deleted_at = dataHoraAtual()
        self.updated_at = dataHoraAtual()

    def restaurar(self):
        self.deleted_at = None
        self.updated_at = dataHoraAtual()    
    
    def __repr__(self):
        return '<Cliente %r>' % self.nome_completo

class Endereco(db.Model):
    __tablename__ = 'enderecos'

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'),unique=False, nullable=True)
    titulo=db.Column(db.String(120), default='cadastro')
    logradouro = db.Column(db.String(120))
    numero = db.Column(db.String(10))
    cep = db.Column(db.String(10))
    complemento = db.Column(db.String(120))
    referencia = db.Column(db.String(120))
    cidade = db.Column(db.String(120))
    uf = db.Column(db.String(10))
    status = db.Column(db.String(1))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    deleted_at = db.Column(db.DateTime)

    cliente = db.relationship('Cliente', back_populates='enderecos')
    pedido = db.relationship('Pedido',uselist=False, back_populates='endereco')

    def soft_delete(self):
        self.deleted_at = dataHoraAtual()
        self.updated_at = dataHoraAtual()

    def restaurar(self):
        self.deleted_at = None
        self.updated_at = dataHoraAtual()    

    def __repr__(self):
        return '<Endereco %r>' % self.logradouro

class Produto(db.Model):
    __tablename__ = 'produtos'

    id = db.Column(db.Integer, primary_key=True)
    produto = db.Column(db.String(120), nullable=False)
    descricao  = db.Column(db.String(250))
    estoque = db.Column(Numeric(10, 2), default=0)
    medida = db.Column(db.String(50))
    vlcompra = db.Column(Numeric(10, 2), default=0)
    vlvenda = db.Column(Numeric(10, 2), default=0)
    status = db.Column(db.Integer, unique=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime)

    produtosfotos = db.relationship('ProdutoFoto', back_populates='produto')
    pedidoitens = db.relationship('PedidoItem', back_populates='produto')
    produtosfavoritos = db.relationship('Favorito', back_populates='produto')

    def soft_delete(self):
        self.deleted_at = dataHoraAtual()
        self.updated_at = dataHoraAtual()

    def restaurar(self):
        self.deleted_at = None
        self.updated_at = dataHoraAtual()

    @classmethod
    def ativo(cls):
        return cls.query.filter(cls.deleted_at.is_(None))

    @classmethod
    def statusAtivo(cls):
        return cls.query.filter_by(status=1)

    @classmethod
    def itemAtivo(cls, idItem):
        return cls.query.filter_by(id=idItem).filter(cls.deleted_at.is_(None))

    def __repr__(self):
        return '<Produto %r>' % self.produto

class ProdutoFoto(db.Model):
    __tablename__ = 'produtos_fotos'

    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'),unique=False, nullable=False)
    foto = db.Column(db.String(250), nullable=False)
    # 1 para capa 0 para as demais
    tipo = db.Column(db.Integer,default=0,nullable=False) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    deleted_at = db.Column(db.DateTime)

    produto = db.relationship('Produto', back_populates='produtosfotos')

    def soft_delete(self):
        self.deleted_at = dataHoraAtual()
        self.updated_at = dataHoraAtual()

    def restaurar(self):
        self.deleted_at = None
        self.updated_at = dataHoraAtual()    

    @classmethod
    def ativo(cls):
        return cls.query.filter(cls.deleted_at.is_(None))
        

    def __repr__(self):
        return '<ProdutoFoto %r>' % self.foto

class Favorito(db.Model):
    __tablename__ = 'produtos_favoritos'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),unique=False, nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'),unique=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    deleted_at = db.Column(db.DateTime)

    user = db.relationship('User', back_populates='produtosfavoritos')
    produto = db.relationship('Produto', back_populates='produtosfavoritos')

    def soft_delete(self):
        self.deleted_at = dataHoraAtual()
        self.updated_at = dataHoraAtual()

    def restaurar(self):
        self.deleted_at = None
        self.updated_at = dataHoraAtual()    

    def __repr__(self):
        return '<Favorito %r>' % self.id

class PedidoItem(db.Model):
    __tablename__ = 'pedidos_itens'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),unique=False, nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'),unique=False, nullable=False)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'),nullable=True)
    quantidade = db.Column(Numeric(10, 2), default=0)   
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    deleted_at = db.Column(db.DateTime)

    user = db.relationship('User', back_populates='pedidoitens')
    produto = db.relationship('Produto', back_populates='pedidoitens')
    pedido = db.relationship('Pedido', back_populates='pedidoitem')

    def soft_delete(self):
        self.deleted_at = dataHoraAtual()
        self.updated_at = dataHoraAtual()

    def restaurar(self):
        self.deleted_at = None
        self.updated_at = dataHoraAtual()    

    def __repr__(self):
        return '<PedidoItem %r>' % self.id

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),unique=False, nullable=False)
    endereco_id = db.Column(db.Integer, db.ForeignKey('enderecos.id'),unique=False, nullable=False)
    valor_total = db.Column(Numeric(10, 2), default=0)
    valor_frete = db.Column(Numeric(10, 2), default=0)
    status = db.Column(db.Integer, nullable=False)
    tipo_pagamento = db.Column(db.String(50), nullable=False)
    obs = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    deleted_at = db.Column(db.DateTime)

    user = db.relationship('User', back_populates='pedidos')
    pedidoitem = db.relationship('PedidoItem',back_populates='pedido')
    endereco = db.relationship('Endereco', back_populates='pedido')

    def __repr__(self):
        return '<Pedido %r>' % self.id