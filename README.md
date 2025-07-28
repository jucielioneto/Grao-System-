# Grão System

Sistema de processamento de planilhas para geração de arquivos TXT para diferentes lojas.

## Funcionalidades

- Upload e processamento de planilhas Excel (.xls, .xlsx, .xlsm)
- Suporte a múltiplos formatos de planilha (openpyxl, xlrd)
- Geração de arquivos TXT para diferentes lojas (Pituba, Hortifruti)
- Sistema de autenticação de usuários
- Histórico de processamentos
- Download de arquivos gerados
- **Sistema de limpeza automática de arquivos antigos**
- **Monitoramento de espaço em disco**
- **Limpeza manual via API**

## Deploy no Railway

### Pré-requisitos

1. Conta no Railway (https://railway.app)
2. Repositório Git com o código

### Passos para Deploy

1. **Conecte seu repositório ao Railway**
   - Acesse railway.app
   - Clique em "New Project"
   - Selecione "Deploy from GitHub repo"
   - Conecte seu repositório

2. **Configure as variáveis de ambiente**
   No painel do Railway, vá em "Variables" e configure:

   ```
   FLASK_ENV=production
   SECRET_KEY=sua_chave_secreta_muito_segura_aqui
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=true
   MAIL_USERNAME=seu_email@gmail.com
   MAIL_PASSWORD=sua_senha_de_app
   MAIL_DEFAULT_SENDER=seu_email@gmail.com
   ```

3. **Adicione um banco PostgreSQL**
   - No Railway, clique em "New"
   - Selecione "Database" → "PostgreSQL"
   - O Railway automaticamente configurará a variável `DATABASE_URL`

4. **Deploy**
   - O Railway detectará automaticamente que é uma aplicação Python
   - O deploy será iniciado automaticamente

### Configuração de E-mail

Para usar o sistema de redefinição de senha:

1. Configure uma conta Gmail
2. Ative a verificação em duas etapas
3. Gere uma senha de app
4. Configure as variáveis `MAIL_USERNAME` e `MAIL_PASSWORD`

### Estrutura do Projeto

```
├── app.py              # Aplicação principal
├── config.py           # Configurações
├── requirements.txt    # Dependências Python
├── Procfile           # Configuração para Railway
├── runtime.txt        # Versão do Python
├── templates/         # Templates HTML
├── static/           # Arquivos estáticos (CSS, JS, imagens)
├── uploads/          # Arquivos enviados (excluído do Git)
└── txts/             # Arquivos gerados (excluído do Git)
```

### Variáveis de Ambiente

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `FLASK_ENV` | Ambiente da aplicação | `production` |
| `SECRET_KEY` | Chave secreta do Flask | `chave_super_secreta` |
| `DATABASE_URL` | URL do banco PostgreSQL | `postgresql://...` |
| `MAIL_USERNAME` | E-mail para envio | `seu_email@gmail.com` |
| `MAIL_PASSWORD` | Senha do e-mail | `senha_de_app` |
| `MAX_DISK_USAGE_PERCENT` | Uso máximo de disco (%) | `80` |
| `MAX_FILE_AGE_DAYS` | Idade máxima dos arquivos (dias) | `30` |
| `MIN_FREE_SPACE_MB` | Espaço livre mínimo (MB) | `100` |

### Desenvolvimento Local

1. Clone o repositório
2. Instale as dependências: `pip install -r requirements.txt`
3. Configure as variáveis de ambiente
4. Execute: `python app.py`

### Sistema de Limpeza Automática

O sistema inclui um gerenciador automático de arquivos que:

- **Monitora o uso de disco** em tempo real
- **Remove arquivos antigos** automaticamente quando necessário
- **Limpa registros do banco** de arquivos inexistentes
- **Executa limpeza** antes de cada processamento

#### Configurações de Limpeza:
- `MAX_DISK_USAGE_PERCENT`: Uso máximo de disco (padrão: 80%)
- `MAX_FILE_AGE_DAYS`: Idade máxima dos arquivos (padrão: 30 dias)
- `MIN_FREE_SPACE_MB`: Espaço livre mínimo (padrão: 100 MB)

#### APIs de Limpeza:
- `GET /storage_stats`: Ver estatísticas de armazenamento
- `POST /cleanup`: Executar limpeza manual

### Notas Importantes

- Os arquivos de upload e saída são armazenados localmente no Railway
- O banco de dados é PostgreSQL fornecido pelo Railway
- A aplicação usa Gunicorn como servidor WSGI em produção
- Todas as configurações sensíveis devem estar em variáveis de ambiente
- **Sistema de limpeza automática mantém o espaço em disco otimizado** 