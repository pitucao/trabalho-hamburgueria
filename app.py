import json
import os
import datetime
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)

# CHAVE SECRETA: Necessária para criptografar os dados da sessão
app.secret_key = 'chave_secreta_hamburgueria_123'

# Caminhos dos arquivos de banco de dados
ARQUIVO_USUARIOS = 'usuarios.json'
ARQUIVO_PEDIDOS = 'pedidos.json'

# Banco de dados de ingredientes dinâmicos (inicializado com os itens padrão)
ingredientes_banco = {
    'pao': 'Pão de Brioche',
    'carne': 'Blend Bovino 150g',
    'queijo': 'Queijo Prato Derretido',
    'salada': 'Alface, tomate e cebola'
}

def carregar_usuarios():
    """Carrega o dicionário de usuários do arquivo JSON."""
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
    """Salva o dicionário de usuários no arquivo JSON."""
    with open(ARQUIVO_USUARIOS, 'w', encoding='utf-8') as f:
        json.dump(usuarios, f, indent=4, ensure_ascii=False)

# ==========================================
# ROTA DE LOGIN
# ==========================================
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

# ==========================================
# ROTA DE CADASTRO (RESTAURADA)
# ==========================================
@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        usuario = request.form.get('username').strip()
        senha = request.form.get('password')
        
        if not usuario or not senha:
            return "Preencha todos os campos."
            
        usuarios_cadastrados = carregar_usuarios()
        
        # Verificar duplicadas
        if usuario in usuarios_cadastrados:
            return "Este nome de usuário já está cadastrado."
            
        # usuario é cliente por padrão
        usuarios_cadastrados[usuario] = {
            "senha": str(senha),
            "role": "cliente"
        }
        
        salvar_usuarios(usuarios_cadastrados)
        return redirect(url_for('login'))
        
    return render_template('registrar.html')

# ==========================================
# ROTA DO CARDÁPIO / CHECKOUT (CLIENTE)
# ==========================================
@app.route('/cardapio', methods=['GET', 'POST'])
def cardapio():
    global ingredientes_banco
    
    if 'usuario_logado' not in session:
        return redirect(url_for('login'))
        
    cliente_atual = session['usuario_logado']
    
    if request.method == 'POST':
        endereco_entrega = request.form.get('endereco')
        
        hamburguer_customizado = []
        for chave, nome_completo in ingredientes_banco.items():
            if request.form.get(chave):
                hamburguer_customizado.append(nome_completo)
        
        if not hamburguer_customizado:
            hamburguer_customizado = ["Apenas o prato (Sem ingredientes!)"]
            
        novo_recibo = {
            "cliente": cliente_atual,
            "data_hora": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "ingredientes": hamburguer_customizado,
            "endereco": endereco_entrega
        }
        
        pedidos_existentes = []
        if os.path.exists(ARQUIVO_PEDIDOS):
            try:
                with open(ARQUIVO_PEDIDOS, 'r', encoding='utf-8') as f:
                    pedidos_existentes = json.load(f)
                    if not isinstance(pedidos_existentes, list):
                        pedidos_existentes = []
            except json.JSONDecodeError:
                pedidos_existentes = []
        
        pedidos_existentes.append(novo_recibo)
        with open(ARQUIVO_PEDIDOS, 'w', encoding='utf-8') as f:
            json.dump(pedidos_existentes, f, indent=4, ensure_ascii=False)
            
        return render_template('cardapio.html', 
                               ingredientes=ingredientes_banco, 
                               resumo=hamburguer_customizado, 
                               endereco=endereco_entrega)

    return render_template('cardapio.html', ingredientes=ingredientes_banco, resumo=None, endereco=None)

# ==========================================
# ROTA PRIVILEGIADA (PAINEL DO CHEFE)
# ==========================================
@app.route('/chefe', methods=['GET', 'POST'])
def painel_chefe():
    global ingredientes_banco
    
    if 'usuario_logado' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        chave = request.form.get('chave_ingrediente').lower().strip()
        nome_completo = request.form.get('nome_ingrediente').strip()
        
        if chave and nome_completo:
            ingredientes_banco[chave] = nome_completo
            
    return render_template('chefe.html', ingredientes=ingredientes_banco)

# ==========================================
# ROTA DE LOGOUT (SAIR)
# ==========================================
@app.route('/logout')
def logout():
    session.pop('usuario_logado', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)