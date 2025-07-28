# Guia de Deploy - Grão System no Railway

## 📋 Checklist de Preparação

### ✅ Arquivos Criados/Modificados
- [x] `requirements.txt` - Dependências atualizadas
- [x] `Procfile` - Configuração do Railway
- [x] `runtime.txt` - Versão do Python
- [x] `config.py` - Configurações de ambiente
- [x] `app.py` - Modificado para produção
- [x] `.gitignore` - Arquivos excluídos
- [x] `README.md` - Documentação
- [x] `railway.json` - Configuração Railway
- [x] `init_db.py` - Inicialização do banco
- [x] `migrate_db.py` - Migração de dados

### 🗂️ Arquivos Excluídos do Git
- [x] `__pycache__/` - Cache Python
- [x] `instance/` - Banco SQLite local
- [x] `uploads/` - Arquivos de upload
- [x] `txts/` - Arquivos gerados

## 🚀 Passos para Deploy

### 1. Preparar o Repositório
```bash
# Remover arquivos desnecessários
rm -rf __pycache__
rm -rf instance/
rm -rf uploads/
rm -rf txts/

# Adicionar ao Git
git add .
git commit -m "Preparação para deploy no Railway"
git push origin main
```

### 2. Configurar Railway

#### 2.1 Criar Projeto
1. Acesse [railway.app](https://railway.app)
2. Clique em "New Project"
3. Selecione "Deploy from GitHub repo"
4. Conecte seu repositório

#### 2.2 Adicionar Banco PostgreSQL
1. No projeto Railway, clique em "New"
2. Selecione "Database" → "PostgreSQL"
3. Aguarde a criação (Railway configurará `DATABASE_URL` automaticamente)

#### 2.3 Configurar Variáveis de Ambiente
No painel do Railway, vá em "Variables" e adicione:

```env
FLASK_ENV=production
SECRET_KEY=sua_chave_secreta_muito_segura_aqui_123456789
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=seu_email@gmail.com
MAIL_PASSWORD=sua_senha_de_app_do_gmail
MAIL_DEFAULT_SENDER=seu_email@gmail.com

# Configurações de Limpeza Automática
MAX_DISK_USAGE_PERCENT=80
MAX_FILE_AGE_DAYS=30
MIN_FREE_SPACE_MB=100
```

### 3. Configurar E-mail (Opcional)

Para usar redefinição de senha:

1. **Gmail:**
   - Ative verificação em duas etapas
   - Gere senha de app
   - Configure `MAIL_USERNAME` e `MAIL_PASSWORD`

2. **Outros provedores:**
   - Ajuste `MAIL_SERVER`, `MAIL_PORT` conforme necessário

### 4. Deploy

1. O Railway detectará automaticamente que é uma aplicação Python
2. O deploy será iniciado automaticamente
3. Aguarde a conclusão do build

### 5. Inicializar Banco de Dados

Após o deploy, execute no terminal do Railway:

```bash
python init_db.py
```

Isso criará:
- Todas as tabelas necessárias
- Usuário administrador padrão:
  - **Usuário:** `admin`
  - **Senha:** `admin123`

### 6. Migrar Dados (Opcional)

Se você tem dados no SQLite local:

1. Execute localmente: `python migrate_db.py`
2. Siga as instruções para migrar dados para PostgreSQL

### 7. Testar Sistema de Limpeza

Após o deploy, teste o sistema de limpeza:

```bash
# Ver estatísticas de armazenamento
curl -X GET https://seu-app.railway.app/storage_stats

# Executar limpeza manual
curl -X POST https://seu-app.railway.app/cleanup
```

Ou execute localmente:
```bash
python test_cleanup.py
```

## 🔧 Configurações Importantes

### Variáveis de Ambiente

| Variável | Obrigatória | Descrição |
|----------|-------------|-----------|
| `FLASK_ENV` | ✅ | Deve ser `production` |
| `SECRET_KEY` | ✅ | Chave secreta do Flask |
| `DATABASE_URL` | ✅ | Configurada automaticamente pelo Railway |
| `MAIL_*` | ❌ | Apenas se usar redefinição de senha |
| `MAX_DISK_USAGE_PERCENT` | ❌ | Uso máximo de disco (padrão: 80%) |
| `MAX_FILE_AGE_DAYS` | ❌ | Idade máxima dos arquivos (padrão: 30 dias) |
| `MIN_FREE_SPACE_MB` | ❌ | Espaço livre mínimo (padrão: 100 MB) |

### Estrutura de Arquivos no Railway

```
/
├── app.py              # Aplicação principal
├── config.py           # Configurações
├── requirements.txt    # Dependências
├── Procfile           # Comando de execução
├── runtime.txt        # Versão Python
├── templates/         # Templates HTML
├── static/           # Arquivos estáticos
├── uploads/          # Criado automaticamente
└── txts/             # Criado automaticamente
```

## 🐛 Solução de Problemas

### Erro de Build
- Verifique se todas as dependências estão em `requirements.txt`
- Confirme a versão do Python em `runtime.txt`

### Erro de Banco de Dados
- Verifique se o PostgreSQL foi criado
- Confirme se `DATABASE_URL` está configurada
- Execute `python init_db.py`

### Erro de Upload
- Verifique se os diretórios `uploads/` e `txts/` existem
- Confirme permissões de escrita

### Erro de E-mail
- Verifique configurações SMTP
- Confirme senha de app do Gmail
- Teste com e-mail válido

## 📞 Suporte

Se encontrar problemas:

1. Verifique os logs no Railway
2. Confirme todas as variáveis de ambiente
3. Teste localmente com as mesmas configurações
4. Verifique se o banco PostgreSQL está ativo

## 🔒 Segurança

### Após o Deploy
1. ✅ Altere a senha do usuário admin
2. ✅ Configure uma SECRET_KEY forte
3. ✅ Use HTTPS (Railway fornece automaticamente)
4. ✅ Configure backup do banco PostgreSQL

### Monitoramento
- Railway fornece logs automáticos
- Configure alertas para downtime
- Monitore uso de recursos 