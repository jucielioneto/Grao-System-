from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for, flash, session
import pandas as pd
import os
import json
from datetime import datetime, timezone
import pytz
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from dotenv import load_dotenv
from config import config
from file_cleanup import cleanup_manager

# Carrega variáveis de ambiente
load_dotenv()

# Determina o ambiente
def get_config():
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])

app = Flask(__name__)
app.config.from_object(get_config())

# Cria diretórios se não existirem
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
mail = Mail(app)

# Inicializa o sistema de limpeza
cleanup_manager.init_app(app)

# Serializer para tokens seguros
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# Função para obter horário de Brasília
def get_brasilia_time():
    brasilia_tz = pytz.timezone('America/Sao_Paulo')
    return datetime.now(brasilia_tz)

# Modelo de usuário
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    # Relacionamentos
    planilhas = db.relationship('Planilha', backref='usuario', lazy=True)
    processamentos = db.relationship('Processamento', backref='usuario', lazy=True)

# Modelo para histórico de planilhas
class Planilha(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_arquivo = db.Column(db.String(255), nullable=False)
    nome_original = db.Column(db.String(255), nullable=False)
    tamanho = db.Column(db.Integer, nullable=False)  # em bytes
    tipo_arquivo = db.Column(db.String(10), nullable=False)  # 'xls' ou 'xlsx'
    data_upload = db.Column(db.DateTime, default=get_brasilia_time)
    status = db.Column(db.String(20), default='ativo')  # 'ativo' ou 'deletado'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relacionamentos
    processamentos = db.relationship('Processamento', backref='planilha', lazy=True)

# Modelo para histórico de processamentos
class Processamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo_processamento = db.Column(db.String(20), nullable=False)  # 'pituba' ou 'hortifruti'
    data_processamento = db.Column(db.DateTime, default=get_brasilia_time)
    produtos_processados = db.Column(db.Integer, default=0)
    arquivos_gerados = db.Column(db.Text)  # JSON com lista de arquivos TXT
    status = db.Column(db.String(20), default='concluido')  # 'processando', 'concluido', 'erro'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    planilha_id = db.Column(db.Integer, db.ForeignKey('planilha.id'), nullable=False)

# Modelo para histórico de arquivos TXT
class ArquivoTXT(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_arquivo = db.Column(db.String(255), nullable=False)
    tamanho = db.Column(db.Integer, nullable=False)  # em bytes
    data_geracao = db.Column(db.DateTime, default=get_brasilia_time)
    tipo_loja = db.Column(db.String(50))  # 'pituba', 'vilas', 'vitoria', 'apipema'
    downloads_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='ativo')  # 'ativo' ou 'deletado'
    processamento_id = db.Column(db.Integer, db.ForeignKey('processamento.id'), nullable=False)
    
    # Relacionamento
    processamento = db.relationship('Processamento', backref='arquivos_txt', lazy=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Formulários
class RegistrationForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired(), Length(min=4, max=150)])
    email = StringField('E-mail', validators=[DataRequired(), Length(min=6, max=150)])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirme a Senha', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrar')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Nome de usuário já existe.')
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('E-mail já cadastrado.')

class LoginForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Length(min=6, max=150)])
    submit = SubmitField('Enviar link de redefinição')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Nova Senha', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirme a Nova Senha', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Redefinir Senha')

# Criação do banco (apenas na primeira execução)
with app.app_context():
    db.create_all()

# Garante que as pastas existem
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
if not os.path.exists(app.config['OUTPUT_FOLDER']):
    os.makedirs(app.config['OUTPUT_FOLDER'])

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Conta criada com sucesso! Faça login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Usuário ou senha inválidos.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('login'))

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password_request():
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = s.dumps(user.email, salt='reset-senha')
            link = url_for('reset_password_token', token=token, _external=True)
            # Temporariamente desabilitado o envio de e-mail
            print(f"Link de redefinição gerado: {link}")
            # msg = Message('Redefinição de senha - Grão System', recipients=[user.email])
            # msg.body = f'Olá,\n\nPara redefinir sua senha, clique no link abaixo:\n{link}\n\nSe não foi você, ignore este e-mail.'
            # mail.send(msg)
            flash(f'Link de redefinição gerado! Copie este link: {link}', 'info')
        else:
            flash('E-mail não encontrado no sistema.', 'danger')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password_token(token):
    try:
        email = s.loads(token, salt='reset-senha', max_age=3600)  # 1 hora de validade
    except Exception:
        flash('O link de redefinição é inválido ou expirou.', 'danger')
        return redirect(url_for('reset_password_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first()
        if user:
            user.password_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            db.session.commit()
            flash('Senha redefinida com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

# Proteger rotas principais
@app.route('/')
@login_required
def index():
    section = request.args.get('section', 'pituba')
    return render_template('index.html', initial_section=section)

@app.route('/planilhas')
@login_required
def planilhas():
    # Busca planilhas do banco de dados
    planilhas = Planilha.query.filter_by(
        user_id=current_user.id, 
        status='ativo'
    ).order_by(Planilha.data_upload.desc()).all()
    
    arquivos_planilhas = []
    for planilha in planilhas:
        arquivos_planilhas.append({
            'id': planilha.id,
            'nome': planilha.nome_arquivo,
            'nome_original': planilha.nome_original,
            'tamanho': planilha.tamanho,
            'data_upload': planilha.data_upload,
            'tamanho_formatado': f"{(planilha.tamanho / 1024):.1f} KB",
            'tipo': planilha.tipo_arquivo,
            'processamentos_count': len(planilha.processamentos),
            'usuario': planilha.usuario.username
        })
    
    return render_template('planilhas.html', arquivos=arquivos_planilhas)

@app.route('/txts')
@login_required
def txts():
    # Busca arquivos TXT do banco de dados
    arquivos_txt_db = ArquivoTXT.query.filter_by(status='ativo').order_by(ArquivoTXT.data_geracao.desc()).all()
    
    arquivos_txt = []
    for arquivo in arquivos_txt_db:
        # Obtém o usuário através do processamento
        usuario_nome = 'N/A'
        if arquivo.processamento and arquivo.processamento.usuario:
            usuario_nome = arquivo.processamento.usuario.username
        
        arquivos_txt.append({
            'id': arquivo.id,
            'nome': arquivo.nome_arquivo,
            'tamanho': arquivo.tamanho,
            'data_geracao': arquivo.data_geracao,
            'tamanho_formatado': f"{(arquivo.tamanho / 1024):.1f} KB",
            'tipo_loja': arquivo.tipo_loja,
            'downloads_count': arquivo.downloads_count,
            'processamento_tipo': arquivo.processamento.tipo_processamento if arquivo.processamento else 'N/A',
            'usuario': usuario_nome
        })
    
    return render_template('txts.html', arquivos=arquivos_txt)

@app.route('/visualizar_planilha/<int:planilha_id>')
@login_required
def visualizar_planilha(planilha_id):
    planilha = Planilha.query.filter_by(id=planilha_id, user_id=current_user.id, status='ativo').first()
    if not planilha:
        return jsonify({'error': 'Planilha não encontrada'}), 404
    
    try:
        caminho_arquivo = os.path.join(app.config['UPLOAD_FOLDER'], planilha.nome_arquivo)
        if not os.path.exists(caminho_arquivo):
            return jsonify({'error': 'Arquivo físico não encontrado'}), 404
        
        # Lê a planilha
        df = pd.read_excel(caminho_arquivo)
        print(f"Colunas da planilha: {df.columns.tolist()}")
        print(f"Primeiras linhas: {df.head().to_dict()}")
        produtos_processados = []
        # --- PITUBA ---
        if 'Embalagem' in df.columns and 'Loja Destino' in df.columns:
            print("Processando como planilha Pituba")
            planilha_amaralina = df[df['Loja Destino'].astype(str).str.strip().str.upper() == 'CD01 AMARALINA'].copy()
            print(f"Linhas filtradas: {len(planilha_amaralina)}")
            for idx, row in planilha_amaralina.iterrows():
                embalagem = str(row.get('Embalagem', ''))
                quantidade = row.get('Quantidade', 0)
                produto = row.get('Produto', '')
                descricao = row.get('Descrição', produto)
                if '/' in embalagem:
                    try:
                        fator = int(embalagem.split('/')[-1])
                    except:
                        fator = 1
                else:
                    fator = 1
                if embalagem != 'CX/0001' and fator > 1:
                    nova_quantidade = quantidade * fator
                else:
                    nova_quantidade = quantidade
                produtos_processados.append({
                    'codigo': str(produto),
                    'nome': descricao if pd.notna(descricao) else str(produto),
                    'quantidade': nova_quantidade,
                    'loja_destino': 'CD01 AMARALINA'
                })
            tipo_proc = 'pituba'
        # --- HORTIFRUTI ---
        elif 'PEDIDO HORTI - GRÃO' in df.columns or any(col.startswith('Pedido') for col in df.columns):
            print("Processando como planilha Hortifruti")
            # Lê novamente pulando a primeira linha (header=1)
            df_hort = pd.read_excel(caminho_arquivo, header=1)
            # Renomeia a coluna B para 'Nome do Produto' se necessário
            if df_hort.columns[1] != 'Nome do Produto':
                df_hort.columns.values[1] = 'Nome do Produto'
            lojas = {
                'Pedido Pituba': 'pituba',
                'Pedido Vitoria': 'vitoria',
                'Pedido Vilas': 'vilas',
                'Pedido Apipema': 'apipema'
            }
            for idx, row in df_hort.iterrows():
                codigo = row.get('Cod.', '')
                nome_produto = row.get('Nome do Produto', '')
                if pd.isna(codigo):
                    continue
                quantidades = {}
                for coluna_loja, nome_loja in lojas.items():
                    quantidade = row.get(coluna_loja, 0)
                    if pd.notna(quantidade):
                        quantidades[nome_loja] = int(quantidade)
                    else:
                        quantidades[nome_loja] = 0
                produtos_processados.append({
                    'codigo': str(int(codigo)),
                    'nome': str(nome_produto) if pd.notna(nome_produto) else str(int(codigo)),
                    'quantidades': quantidades
                })
            tipo_proc = 'hortifruti'
        # --- DESCONHECIDO ---
        else:
            print("Tipo de planilha desconhecido, mostrando dados básicos")
            for idx, row in df.iterrows():
                produtos_processados.append({
                    'linha': idx + 1,
                    'dados': row.to_dict()
                })
            tipo_proc = 'desconhecido'
        print(f"Total de produtos processados: {len(produtos_processados)}")
        return jsonify({
            'nome_arquivo': planilha.nome_original,
            'tipo_processamento': tipo_proc,
            'produtos': produtos_processados,
            'total_produtos': len(produtos_processados)
        })
    except Exception as e:
        print(f"Erro ao processar planilha: {str(e)}")
        return jsonify({'error': f'Erro ao processar planilha: {str(e)}'}), 500

@app.route('/visualizar_txt/<int:txt_id>')
@login_required
def visualizar_txt(txt_id):
    arquivo_txt = ArquivoTXT.query.filter_by(id=txt_id, status='ativo').first()
    if not arquivo_txt:
        return jsonify({'error': 'Arquivo TXT não encontrado'}), 404
    
    try:
        caminho_arquivo = os.path.join(app.config['OUTPUT_FOLDER'], arquivo_txt.nome_arquivo)
        if not os.path.exists(caminho_arquivo):
            return jsonify({'error': 'Arquivo físico não encontrado'}), 404
        
        # Lê o arquivo TXT
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
        
        print(f"Arquivo TXT: {arquivo_txt.nome_arquivo}")
        print(f"Total de linhas lidas: {len(linhas)}")
        
        # Processa as linhas - mostra apenas dados essenciais
        produtos = []
        for i, linha in enumerate(linhas, 1):
            linha = linha.strip()
            if linha:
                partes = linha.split(';')
                if len(partes) >= 2:
                    produtos.append({
                        'codigo': partes[0],
                        'quantidade': partes[1],
                        'linha_completa': linha
                    })
        
        print(f"Total de produtos processados: {len(produtos)}")
        
        return jsonify({
            'nome_arquivo': arquivo_txt.nome_arquivo,
            'tipo_loja': arquivo_txt.tipo_loja,
            'produtos': produtos,
            'total_produtos': len(produtos)
        })
        
    except Exception as e:
        print(f"Erro ao ler arquivo TXT: {str(e)}")
        return jsonify({'error': f'Erro ao ler arquivo TXT: {str(e)}'}), 500

@app.route('/deletar_planilha/<int:planilha_id>')
@login_required
def deletar_planilha(planilha_id):
    planilha = Planilha.query.filter_by(id=planilha_id, user_id=current_user.id).first()
    if planilha:
        # Marca como deletado no banco
        planilha.status = 'deletado'
        db.session.commit()
        
        # Remove arquivo físico se existir
        caminho = os.path.join(app.config['UPLOAD_FOLDER'], planilha.nome_arquivo)
        if os.path.exists(caminho):
            os.remove(caminho)
        
        flash('Planilha deletada com sucesso!', 'success')
    else:
        flash('Planilha não encontrada.', 'danger')
    return redirect(url_for('planilhas'))

@app.route('/deletar_txt/<int:txt_id>')
@login_required
def deletar_txt(txt_id):
    arquivo_txt = ArquivoTXT.query.get(txt_id)
    if arquivo_txt:
        # Marca como deletado no banco
        arquivo_txt.status = 'deletado'
        db.session.commit()
        
        # Remove arquivo físico se existir
        caminho = os.path.join(app.config['OUTPUT_FOLDER'], arquivo_txt.nome_arquivo)
        if os.path.exists(caminho):
            os.remove(caminho)
        
        flash('Arquivo TXT deletado com sucesso!', 'success')
    else:
        flash('Arquivo não encontrado.', 'danger')
    return redirect(url_for('txts'))

@app.route('/uploads/<nome_arquivo>')
@login_required
def download_planilha(nome_arquivo):
    caminho = os.path.join(app.config['UPLOAD_FOLDER'], nome_arquivo)
    if os.path.exists(caminho):
        return send_file(caminho, as_attachment=True)
    else:
        return 'Arquivo não encontrado.', 404

@app.route('/storage_stats')
@login_required
def storage_stats():
    """Rota para ver estatísticas de armazenamento"""
    stats = cleanup_manager.get_storage_stats()
    return jsonify(stats)

@app.route('/cleanup', methods=['POST'])
@login_required
def perform_cleanup():
    """Rota para executar limpeza manual"""
    try:
        removed_files, freed_space = cleanup_manager.perform_cleanup(db, Planilha, ArquivoTXT)
        return jsonify({
            'success': True,
            'removed_files': removed_files,
            'freed_space_mb': freed_space / (1024 * 1024),
            'message': f'Limpeza concluída: {removed_files} arquivos removidos, {freed_space / (1024*1024):.2f} MB liberados'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/baixar/<nome_arquivo>')
@login_required
def baixar(nome_arquivo):
    # Busca no banco de dados
    arquivo_txt = ArquivoTXT.query.filter_by(nome_arquivo=nome_arquivo, status='ativo').first()
    if arquivo_txt:
        # Incrementa contador de downloads
        arquivo_txt.downloads_count += 1
        db.session.commit()
    
    caminho = os.path.join(app.config['OUTPUT_FOLDER'], nome_arquivo)
    if os.path.exists(caminho):
        return send_file(caminho, as_attachment=True)
    else:
        return 'Arquivo não encontrado.', 404

@app.route('/processar', methods=['POST'])
@login_required
def processar():
    if 'files[]' not in request.files:
        return 'Nenhum arquivo enviado.'
    files = request.files.getlist('files[]')
    if not files or files[0].filename == '':
        return 'Nenhum arquivo selecionado.'
    
    # Executa limpeza automática antes do processamento
    try:
        cleanup_manager.perform_cleanup(db, Planilha, ArquivoTXT)
    except Exception as e:
        print(f"Erro na limpeza automática: {e}")
    
    section = request.form.get('section', 'pituba')
    if section == 'hortifruti':
        return processar_hortifruti(files)
    else:
        return processar_pituba(files)

def processar_hortifruti(files):
    if len(files) != 1:
        return jsonify({'error': 'Sistema Hortifruti aceita apenas um arquivo por vez.'})
    arquivo = files[0]
    
    # Salva planilha no banco de dados
    nome_arquivo = f"{get_brasilia_time().strftime('%Y%m%d_%H%M%S')}_{arquivo.filename}"
    caminho_arquivo = os.path.join(app.config['UPLOAD_FOLDER'], nome_arquivo)
    arquivo.save(caminho_arquivo)
    
    # Cria registro da planilha
    planilha = Planilha(
        nome_arquivo=nome_arquivo,
        nome_original=arquivo.filename,
        tamanho=os.path.getsize(caminho_arquivo),
        tipo_arquivo=arquivo.filename.split('.')[-1].lower(),
        user_id=current_user.id
    )
    db.session.add(planilha)
    db.session.commit()
    try:
        # Tenta diferentes métodos de leitura para suportar vários formatos
        try:
            # Primeiro tenta com openpyxl (para .xlsx)
            df = pd.read_excel(caminho_arquivo, header=1, engine='openpyxl')
        except:
            try:
                # Tenta com xlrd (para .xls antigos)
                df = pd.read_excel(caminho_arquivo, header=1, engine='xlrd')
            except:
                # Última tentativa sem especificar engine
                df = pd.read_excel(caminho_arquivo, header=1)
        
        # Renomeia a coluna B para 'Nome do Produto' se necessário
        if len(df.columns) > 1 and df.columns[1] != 'Nome do Produto':
            df.columns.values[1] = 'Nome do Produto'
        print('Colunas lidas:', df.columns.tolist())
    except Exception as e:
        print('Erro ao ler arquivo:', e)
        return jsonify({'error': f'Erro ao ler arquivo: {str(e)}'})
    data_hoje = get_brasilia_time().strftime("%Y%m%d")
    lojas = {
        'Pedido Pituba': 'pituba',
        'Pedido Vitoria': 'vitoria',
        'Pedido Vilas': 'vilas',
        'Pedido Apipema': 'apipema'
    }
    arquivos_gerados = []
    produtos_processados = []
    produtos_unicos = {}
    for coluna_loja, nome_loja in lojas.items():
        if coluna_loja in df.columns:
            nome_arquivo = f"{nome_loja}-{data_hoje}.txt"
            caminho_saida = os.path.join(app.config['OUTPUT_FOLDER'], nome_arquivo)
            print(f'Gerando arquivo: {nome_arquivo}')
            with open(caminho_saida, 'w') as f:
                for _, row in df.iterrows():
                    if pd.notna(row['Cod.']) and pd.notna(row[coluna_loja]):
                        linha = f"{int(row['Cod.'])};{int(row[coluna_loja])}\n"
                        f.write(linha)
                        codigo_produto = str(int(row['Cod.']))
                        nome_produto = str(row['Nome do Produto']) if pd.notna(row['Nome do Produto']) else codigo_produto
                        quantidade = int(row[coluna_loja])
                        if codigo_produto not in produtos_unicos:
                            produtos_unicos[codigo_produto] = {
                                'codigo': codigo_produto,
                                'nome': nome_produto,
                                'quantidades': {},
                                'arquivo_origem': arquivo.filename
                            }
                        produtos_unicos[codigo_produto]['quantidades'][nome_loja] = quantidade
            arquivos_gerados.append(nome_arquivo)
        else:
            print(f'Coluna não encontrada na planilha: {coluna_loja}')
    
    # Cria registro de processamento
    processamento = Processamento(
        tipo_processamento='hortifruti',
        produtos_processados=len(produtos_unicos),
        arquivos_gerados=json.dumps(arquivos_gerados),
        user_id=current_user.id,
        planilha_id=planilha.id
    )
    db.session.add(processamento)
    db.session.commit()
    
    # Salva arquivos TXT no banco
    for nome_arquivo in arquivos_gerados:
        caminho_txt = os.path.join(app.config['OUTPUT_FOLDER'], nome_arquivo)
        if os.path.exists(caminho_txt):
            arquivo_txt = ArquivoTXT(
                nome_arquivo=nome_arquivo,
                tamanho=os.path.getsize(caminho_txt),
                tipo_loja=nome_arquivo.split('-')[0],
                processamento_id=processamento.id
            )
            db.session.add(arquivo_txt)
    
    db.session.commit()
    
    for produto in produtos_unicos.values():
        produtos_processados.append(produto)
    print('Produtos processados:', produtos_processados)
    print('Arquivos gerados:', arquivos_gerados)
    return jsonify({
        'produtos': produtos_processados,
        'total_produtos': len(produtos_processados),
        'arquivos_gerados': arquivos_gerados,
        'section': 'hortifruti',
        'lojas': list(lojas.values())
    })

def processar_pituba(files):
    produtos_processados = []
    data_hoje = get_brasilia_time().strftime("%Y%m%d")
    nome_arquivo_txt = f"pituba-{data_hoje}.txt"
    caminho_saida = os.path.join(app.config['OUTPUT_FOLDER'], nome_arquivo_txt)
    # Limpa o arquivo TXT antes de começar
    open(caminho_saida, 'w').close()
    
    planilhas_processadas = []
    for arquivo in files:
        # Salva planilha no banco de dados
        nome_arquivo = f"{get_brasilia_time().strftime('%Y%m%d_%H%M%S')}_{arquivo.filename}"
        caminho_arquivo = os.path.join(app.config['UPLOAD_FOLDER'], nome_arquivo)
        arquivo.save(caminho_arquivo)
        
        # Cria registro da planilha
        planilha = Planilha(
            nome_arquivo=nome_arquivo,
            nome_original=arquivo.filename,
            tamanho=os.path.getsize(caminho_arquivo),
            tipo_arquivo=arquivo.filename.split('.')[-1].lower(),
            user_id=current_user.id
        )
        db.session.add(planilha)
        db.session.commit()
        planilhas_processadas.append(planilha)
        try:
            # Tenta diferentes métodos de leitura para suportar vários formatos
            try:
                # Primeiro tenta com openpyxl (para .xlsx)
                df = pd.read_excel(caminho_arquivo, engine='openpyxl')
            except:
                try:
                    # Tenta com xlrd (para .xls antigos)
                    df = pd.read_excel(caminho_arquivo, engine='xlrd')
                except:
                    # Última tentativa sem especificar engine
                    df = pd.read_excel(caminho_arquivo)
        except Exception as e:
            print(f'Erro ao ler o arquivo {arquivo.filename}: {e}')
            continue
        # Multiplicação da embalagem e padronização
        for idx, row in df.iterrows():
            embalagem = str(row.get('Embalagem', ''))
            quantidade = row.get('Quantidade', 0)
            if '/' in embalagem:
                try:
                    fator = int(embalagem.split('/')[-1])
                except:
                    fator = 1
            else:
                fator = 1
            if embalagem != 'CX/0001' and fator > 1:
                nova_quantidade = quantidade * fator
                df.at[idx, 'Quantidade'] = nova_quantidade
                df.at[idx, 'Embalagem'] = 'CX/0001'
            else:
                df.at[idx, 'Embalagem'] = 'CX/0001'
        # Filtra apenas CD01 AMARALINA
        planilha_amaralina = df[df['Loja Destino'].astype(str).str.strip().str.upper() == 'CD01 AMARALINA']
        # Gera colunas auxiliares
        planilha_amaralina['numero_produto'] = planilha_amaralina['Produto'].astype(str)
        planilha_amaralina['quantidade_numero'] = planilha_amaralina['Quantidade'].astype(str)
        # Gera TXT (acrescenta ao arquivo consolidado)
        with open(caminho_saida, 'a') as f:
            for _, row in planilha_amaralina.iterrows():
                linha = f"{row['numero_produto']};{row['quantidade_numero']}\n"
                f.write(linha)
                produto = {
                    'codigo': row['numero_produto'],
                    'nome': row['Descrição'] if 'Descrição' in row and pd.notna(row['Descrição']) else row['numero_produto'],
                    'quantidade': int(row['quantidade_numero']),
                    'arquivo_origem': arquivo.filename
                }
                produtos_processados.append(produto)
    
    # Cria registro de processamento (usa a primeira planilha como referência)
    if planilhas_processadas:
        processamento = Processamento(
            tipo_processamento='pituba',
            produtos_processados=len(produtos_processados),
            arquivos_gerados=json.dumps([nome_arquivo_txt]),
            user_id=current_user.id,
            planilha_id=planilhas_processadas[0].id
        )
        db.session.add(processamento)
        db.session.commit()
        
        # Salva arquivo TXT no banco
        if os.path.exists(caminho_saida):
            arquivo_txt = ArquivoTXT(
                nome_arquivo=nome_arquivo_txt,
                tamanho=os.path.getsize(caminho_saida),
                tipo_loja='pituba',
                processamento_id=processamento.id
            )
            db.session.add(arquivo_txt)
            db.session.commit()
    
    print('Produtos processados:', produtos_processados)
    print('Arquivo TXT gerado:', nome_arquivo_txt)
    return jsonify({
        'produtos': produtos_processados,
        'total_produtos': len(produtos_processados),
        'arquivo_txt': nome_arquivo_txt,
        'section': 'pituba'
    })

if __name__ == '__main__':
    # Cria as tabelas do banco de dados se não existirem
    with app.app_context():
        db.create_all()
    
    # Determina se está em produção ou desenvolvimento
    if os.environ.get('FLASK_ENV') == 'production':
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    else:
        app.run(debug=True)
