from flasgger import swag_from



class documentos():
    def inicio(self):
        return {
            'responses': {
                200: {
                    'description': 'Todos os produtos ativos sem filtro',
                }
            }
        }
    
    def produtos(self):
        jsonProdutos = {
            'parameters': [
                {
                    'name': 'filtro',
                    'in': 'query',
                    'type': 'string',
                    'required': False,
                    'description': 'Filtro para os produtos',
                    'example': 'banana'  # Exemplo adicionado
                },
                {
                    'name': 'ordena',
                    'in': 'query',
                    'type': 'string',
                    'required': False,
                    'description': 'Ordem crescente',
                    'example': 'id'  # Exemplo adicionado
                },
                {
                    'name': 'ordenadesc',
                    'in': 'query',
                    'type': 'string',
                    'required': False,
                    'description': 'Ordem decrescente',
                    'example': 'id'  # Exemplo adicionado
                }
            ],
            'responses': {
                200: {
                    'description': 'Detalhes do produto',
                    'examples': {
                        'application/json': {                   
                            "code": 200,
                            "data": {
                                "pagina_atual": 1,
                                "produtos": [
                                {
                                    "created_at": "2024-05-21 20:38:28",
                                    "deleted_at": 'null',
                                    "descricao": "Banana Prata Verde",
                                    "estoque": "995.00",
                                    "fotos": "sem_foto.jpg",
                                    "id": 1,
                                    "medida": "dz",
                                    "produto": "Banana",
                                    "status": 1,
                                    "updated_at": "2024-05-21 20:38:55",
                                    "vlcompra": "5.00",
                                    "vlvenda": "9.99"
                                }
                                ],
                                "total_paginas": 1,
                                "total_produtos": 2
                            },
                            "status": "success"
                        }
                    }
                }
            }
        }
        return jsonProdutos