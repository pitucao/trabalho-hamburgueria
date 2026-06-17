from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)


ARQUIVO_BANCO = 'usuarios.json'

# ler usuários 
def carregar_usuarios():
    if not os.path.exists(ARQUIVO_BANCO):
        return {}   
    with open(ARQUIVO_BANCO, 'r') as arquivo:
        return json.load(arquivo)

# salvar novo usuário 
def salvar_usuario(usuario, senha):
    usuarios = carregar_usuarios()
    usuarios[usuario] = str(senha)
    with open(ARQUIVO_BANCO, 'w') as arquivo:
        json.dump(usuarios, arquivo, indent=4)






@app.route('/painel')
def painel():
    return render_template('painel.html')


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('username')
        senha = request.form.get('password')
        
        usuarios_cadastrados = carregar_usuarios()
        
        # Se o login estiver correto...
        if usuario in usuarios_cadastrados and usuarios_cadastrados[usuario] == str(senha):
            # REDIRECIONA para a função 'painel' que foi criada no Passo 1
            return redirect(url_for('painel'))
            
        return "Usuário ou senha incorretos. Tente novamente."

    return render_template('index.html')


@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        novo_usuario = request.form.get('username')
        nova_senha = request.form.get('password')
        confirmacao = request.form.get('confirm_password')
        
        if nova_senha != confirmacao:
            return "As senhas não coincidem!"
            
        # Carrega os usuários para ver se o nome já existe
        usuarios_cadastrados = carregar_usuarios()
        if novo_usuario in usuarios_cadastrados:
            return "Este usuário já existe!"
            
        # Salva permanentemente no arquivo JSON
        salvar_usuario(novo_usuario, nova_senha)
        
        return redirect(url_for('login'))

    return render_template('registrar.html')

if __name__ == '__main__':
    app.run(debug=True)