from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import os

app = Flask(__name__)
# app.config['SECRET_KEY'] = 'chave-secreta'  # Alterar para uma chave segura
app.config['MY_SECRET_KEY'] = os.environ.get('MY_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"

# 📂 Caminho do OneDrive
ONEDRIVE_FOLDER = 'dados'
os.makedirs(ONEDRIVE_FOLDER, exist_ok=True)

# 📄 Nome do arquivo Excel para armazenar respostas
dados_excel = os.path.join(ONEDRIVE_FOLDER, 'dados_formulario.xlsx')

# 📌 Modelo de usuário
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# 📌 Rota de Cadastro
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        senha_hash = generate_password_hash(senha)

        if Usuario.query.filter_by(email=email).first():
            flash("E-mail já cadastrado!", "danger")
            return redirect(url_for("cadastro"))

        novo_usuario = Usuario(nome=nome, email=email, senha=senha_hash)
        db.session.add(novo_usuario)
        db.session.commit()

        flash("Cadastro realizado com sucesso! Faça login.", "success")
        return redirect(url_for("login"))

    return render_template('cadastro.html')

# 📌 Rota de Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.senha, senha):
            login_user(usuario)
            return redirect(url_for("minhas_respostas"))

        flash("Login inválido!", "danger")
        return redirect(url_for("login"))

    return render_template('login.html')


# 📌 Formulário de Respostas (Apenas para usuários logados)
@app.route('/formulario', methods=['GET', 'POST'])
@login_required
def formulario():
    if request.method == 'POST':
        nome_secretaria = request.form.get('nome_secretaria', '')
        nome_responsavel = request.form.get('nome_responsavel', '')
        tipo_acao = request.form.get('tipo_acao', '')
        situacao_problema = request.form.get('situacao_problema', '')
        evento = request.form.get('evento', '')
        niveis_planejamento = request.form.get('nivel_vulnerabilidade1', '')
        municipios_planejamento = ', '.join(request.form.getlist('municipio_section_planejamento'))
        objetivos_planejamento = request.form.get('objetivos_planejamento', '')
        valor_empenhado_planejamento = request.form.get('valor_planejamento', '')
        orcamento_planejamento = request.form.get('orcamento_planejamento', '')
        inicio_planejamento = request.form.get('inicio_planejamento', '')
        termino_planejamento = request.form.get('termino_planejamento', '')
        niveis_andamento = request.form.get('nivel_vulnerabilidade2', '')
        municipios_andamento = ', '.join(request.form.getlist('municipio_section_andamento'))
        descricao_andamento = request.form.get('descricao_andamento', '')
        valor_empenhado_andamento = request.form.get('valor_empenhado_andamento', '')
        inicio_andamento = request.form.get('inicio_andamento', '')
        termino_andamento = request.form.get('termino_andamento', '')
        desafios_andamento = request.form.get('desafios_andamento', '')
        populacao_andamento = request.form.get('informacao_populacao', '')
        secretarias_andamento = ', '.join(request.form.getlist('secretarias_andamento'))
        niveis_realizada = request.form.get('nivel_vulnerabilidade3', '')
        municipios_realizada = ', '.join(request.form.getlist('municipio_section_realizada'))
        descricao_realizada = request.form.get('descricao_realizada', '')
        valor_empenhado_realizada = request.form.get('valor_realizada', '')
        inicio_realizada = request.form.get('inicio_realizada', '')
        termino_realizada = request.form.get('termino_realizada', '')
        secretarias_realizada = ', '.join(request.form.getlist('secretarias_realizada'))

        # 📄 Adicionar as respostas ao Excel
        novo_dado = pd.DataFrame({
            'Usuário': [current_user.email],
            'Nome Secretaria': [nome_secretaria],
            'Nome Responsavel': [nome_responsavel],
            'Tipo Ação': [tipo_acao],
            'Situação Problema': [situacao_problema],
            'Evento': [evento],
            'Niveis Planejamento': [niveis_planejamento],
            'Municipios Planejamento': [municipios_planejamento],
            'Objetivos Planejamento': [objetivos_planejamento],
            'Empenho Planejamento': [valor_empenhado_planejamento],
            'Orcamento Planejamento': [orcamento_planejamento],
            'Inicio Planejamento': [inicio_planejamento],
            'Termino Planejamento': [termino_planejamento],
            'Niveis Andamento': [niveis_andamento],
            'Municipios Andamento': [municipios_andamento],
            'Descricao Andamento': [descricao_andamento],
            'Empenho Andamento': [valor_empenhado_andamento],
            'Inicio Andamento': [inicio_andamento],
            'Termino Andamento': [termino_andamento],
            'Desafios Andamento': [desafios_andamento],
            'Populacao Andamento': [populacao_andamento],
            'Secretarias Andamento': [secretarias_andamento],
            'Niveis Realizada': [niveis_realizada],
            'Municipios Realizada': [municipios_realizada],
            'Descrição Realizada': [descricao_realizada],
            'Empenho Realizada': [valor_empenhado_realizada],
            'Início Realizada': [inicio_realizada],
            'Término Realizada': [termino_realizada],
            'Secretarias Realizada': [secretarias_realizada]
        })

        if os.path.exists(dados_excel):
            df_existente = pd.read_excel(dados_excel)
            df_final = pd.concat([df_existente, novo_dado], ignore_index=True)
        else:
            df_final = novo_dado

        df_final.to_excel(dados_excel, index=False)

        flash("Dados enviados com sucesso!", "success")
        return redirect(url_for("formulario"))

    return render_template('formulario.html')

# 📌 Visualizar respostas do usuário logado
@app.route('/minhas-respostas')
@login_required
def minhas_respostas():
    if os.path.exists(dados_excel):
        df = pd.read_excel(dados_excel)
        df_usuario = df[df['Usuário'] == current_user.email]
        respostas = df_usuario.to_dict(orient="records")
    else:
        respostas = []

    return render_template('minhas_respostas.html', respostas=respostas, nome_usuario=current_user.nome)


# 📌 Editar resposta
@app.route('/editar-resposta/<int:indice>', methods=['GET', 'POST'])
@login_required
def editar_resposta(indice):
    print("Entrou na rota /editar-resposta com método:", request.method)
    if os.path.exists(dados_excel):
        df = pd.read_excel(dados_excel)

        # Verifique se o índice é válido
        if 0 <= indice < len(df):
            resposta = df.iloc[indice]

            # Verifique se o usuário logado tem permissão para editar
            if resposta["Usuário"] != current_user.email:
                flash("Você não tem permissão para editar esta resposta!", "danger")
                return redirect(url_for('minhas_respostas'))

            if request.method == 'POST':
                novo_tipo_acao = request.form.get('tipo_acao') or resposta['Tipo Ação']
                
                # Atualizar sempre o Tipo Ação
                df.at[indice, 'Tipo Ação'] = novo_tipo_acao

                # Limpar colunas dos outros tipos de ação
                planejamento_cols = [
                    'Niveis Planejamento', 'Municipios Planejamento', 'Objetivos Planejamento',
                    'Empenho Planejamento', 'Orçamento Planejamento', 'Inicio Planejamento', 'Termino Planejamento'
                ]
                andamento_cols = [
                    'Niveis Andamento', 'Municipios Andamento', 'Descricao Andamento', 'Empenho Andamento',
                    'Inicio Andamento', 'Termino Andamento', 'Desafios Andamento', 'Populacao Andamento', 'Secretarias Andamento'
                ]
                realizada_cols = [
                    'Niveis Realizada', 'Municipios Realizada', 'Descricao Realizada', 'Empenho Realizada',
                    'Início Realizada', 'Término Realizada', 'Secretarias Realizada'
                ]

                def limpar_colunas(colunas):
                    for col in colunas:
                        if col in df.columns:
                            df.at[indice, col] = ""

                if novo_tipo_acao == "Planejamento":
                    limpar_colunas(andamento_cols)
                    limpar_colunas(realizada_cols)
                elif novo_tipo_acao == "Andamento":
                    limpar_colunas(planejamento_cols)
                    limpar_colunas(realizada_cols)
                elif novo_tipo_acao == "Realizada":
                    limpar_colunas(planejamento_cols)
                    limpar_colunas(andamento_cols)

                df.at[indice, 'Nome Secretaria'] = request.form.get('nome_secretaria') or resposta['Nome Secretaria']
                df.at[indice, 'Situação Problema'] = request.form.get('situacao_problema') or resposta['Situação Problema']
                df.at[indice, 'Evento'] = request.form.get('evento') or resposta['Evento']

                df.to_excel(dados_excel, index=False)
                flash("Resposta editada com sucesso!", "success")
                return redirect(url_for('minhas_respostas'))

            # Se não for POST (ou seja, for GET), renderiza o formulário de edição
            return render_template('editar_resposta.html', resposta=resposta, indice=indice)
    else:
        flash("Arquivo de dados não encontrado!", "danger")
        return redirect(url_for('minhas_respostas'))


# 📌 Excluir resposta
@app.route('/excluir-resposta/<int:indice>', methods=['POST'])
@login_required
def excluir_resposta(indice):
    if os.path.exists(dados_excel):
        df = pd.read_excel(dados_excel)

        # Verifique se o índice é válido
        if 0 <= indice < len(df):
            resposta = df.iloc[indice]

            # Verifique se o usuário logado tem permissão para excluir
            if resposta["Usuário"] != current_user.email:
                flash("Você não tem permissão para excluir esta resposta!", "danger")
                return redirect(url_for('minhas_respostas'))

            df = df.drop(index=indice).reset_index(drop=True)
            df.to_excel(dados_excel, index=False)  # Salvar alterações
            flash("Resposta excluída com sucesso!", "success")
            return redirect(url_for('minhas_respostas'))
        
@app.route('/logout', methods=['POST'])
@login_required  # Garantir que o usuário esteja logado para fazer o logout
def logout():
    logout_user()  # Função do Flask-Login para deslogar o usuário
    flash("Você saiu com sucesso.", "info")  # Mensagem de sucesso ao deslogar
    return redirect(url_for('login'))  # Redireciona para a página de login


# 📌 Rodar o aplicativo
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Cria banco de dados se não existir
    app.run(debug=True)
