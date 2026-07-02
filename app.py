import json
import os
import datetime
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'chave_secreta_hamburgueria_123'

ARQUIVO_USUARIOS = 'usuarios.json'
ARQUIVO_PEDIDOS = 'pedidos.json'

# Banco de dados de ingredientes estruturado corretamente com dicionários internos
ingredientes_banco = {
    'pao_brioche': {'nome': 'Pão de Brioche', 'preco': 4.50},
    'pao_australiano': {'nome': 'Pão Australiano', 'preco': 5.00},
    'carne_bovina': {'nome': 'Blend Bovino 150g', 'preco': 12.00},
    'carne_frango': {'nome': 'Filé de Frango Grelhado', 'preco': 9.50},
    'queijo_prato': {'nome': 'Queijo Prato Derretido', 'preco': 3.50},
    'queijo_cheddar': {'nome': 'Cheddar Cremoso', 'preco': 5.00},
    'salada': {'nome': 'Alface, Tomate e Cebola', 'preco': 2.00},
    'bacon': {'nome': 'Bacon Crispy', 'preco': 4.50},
    'picles': {'nome': 'Picles Artesanal', 'preco': 2.50}
}

def carregar_usuarios():
    if not os.path.exists(ARQUIVO_USUARIOS):
        with open(ARQUIVO_USUARIOS, 'w', encoding='utf-8') as f:
            json.dump({}, f)
        return {}
    try:
        with open(ARQUIVO_USUARIOS, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def salvar_usuarios(usuarios):
    with open(ARQUIVO_USUARIOS, 'w', encoding='utf-8') as f:
        json.dump(usuarios, f, indent=4, ensure_ascii=False)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('username')
        senha = request.form.get('password')
        usuarios_cadastrados = carregar_usuarios()
        
        if usuario in usuarios_cadastrados:
            dados_usuario = usuarios_cadastrados[usuario]
            if isinstance(dados_usuario, str):
                senha_correta = (dados_usuario == str(senha))
                eh_admin = False
            else:
                senha_correta = (dados_usuario['senha'] == str(senha))
                eh_admin = (dados_usuario.get('role') == 'admin')
            
            if senha_correta:
                session['usuario_logado'] = usuario
                if eh_admin:
                    return redirect(url_for('painel_chefe'))
                return redirect(url_for('cardapio'))
                
        return "Usuário ou senha incorretos. Tente novamente."
    return render_template('index.html')

@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        usuario = request.form.get('username').strip()
        senha = request.form.get('password')
        if not usuario or not senha:
            return "Preencha todos os campos."
            
        usuarios_cadastrados = carregar_usuarios()
        if usuario in usuarios_cadastrados:
            return "Este nome de usuário já está cadastrado."
            
        usuarios_cadastrados[usuario] = {"senha": str(senha), "role": "cliente"}
        salvar_usuarios(usuarios_cadastrados)
        return redirect(url_for('login'))
    return render_template('registrar.html')

@app.route('/cardapio', methods=['GET', 'POST'])
def cardapio():
    global ingredientes_banco
    if 'usuario_logado' not in session:
        return redirect(url_for('login'))
        
    cliente_atual = session['usuario_logado']
    
    if request.method == 'POST':
        endereco_entrega = request.form.get('endereco')
        forma_pagamento = request.form.get('pagamento')
        pao_escolhido = request.form.get('pao_selecionado')
        
        hamburguer_customizado = []
        valor_total = 0.0
        
        if pao_escolhido in ingredientes_banco:
            hamburguer_customizado.append(ingredientes_banco[pao_escolhido]['nome'])
            valor_total += ingredientes_banco[pao_escolhido]['preco']
        
        for chave, dados in ingredientes_banco.items():
            if chave != 'pao_brioche' and chave != 'pao_australiano':
                if request.form.get(chave):
                    hamburguer_customizado.append(dados['nome'])
                    valor_total += dados['preco']
        
        if not hamburguer_customizado:
            return render_template('cardapio.html', ingredientes=ingredientes_banco, resumo=None, total=0.0, pagamento=None, endereco=None, erro="Selecione pelo menos um ingrediente.")
            
        novo_recibo = {
            "cliente": cliente_atual,
            "data_hora": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "ingredientes": hamburguer_customizado,
            "total": round(valor_total, 2),
            "forma_pagamento": forma_pagamento,
            "endereco": endereco_entrega
        }
        
        pedidos_existentes = []
        if os.path.exists(ARQUIVO_PEDIDOS):
            try:
                with open(ARQUIVO_PEDIDOS, 'r', encoding='utf-8') as f:
                    pedidos_existentes = json.load(f)
            except json.JSONDecodeError:
                pedidos_existentes = []
        
        pedidos_existentes.append(novo_recibo)
        with open(ARQUIVO_PEDIDOS, 'w', encoding='utf-8') as f:
            json.dump(pedidos_existentes, f, indent=4, ensure_ascii=False)
            
        return render_template('cardapio.html', 
                               ingredientes=ingredientes_banco, 
                               resumo=hamburguer_customizado, 
                               total=valor_total,
                               pagamento=forma_pagamento,
                               endereco=endereco_entrega,
                               erro=None)

    return render_template('cardapio.html', ingredientes=ingredientes_banco, resumo=None, total=0.0, pagamento=None, endereco=None, erro=None)

@app.route('/chefe', methods=['GET', 'POST'])
def painel_chefe():
    global ingredientes_banco
    if 'usuario_logado' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        chave = request.form.get('chave_ingrediente').lower().strip().replace(" ", "_")
        nome_completo = request.form.get('nome_ingrediente').strip()
        preco = request.form.get('preco_ingrediente')
        
        # Garante que o novo ingrediente seja adicionado como dicionário contendo nome e preço
        if chave and nome_completo and preco:
            try:
                ingredientes_banco[chave] = {
                    'nome': nome_completo,
                    'preco': float(preco)
                }
            except ValueError:
                return "Preço inválido. Use pontos para os centavos."
            
    return render_template('chefe.html', ingredientes=ingredientes_banco)

@app.route('/logout')
def logout():
    session.pop('usuario_logado', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)