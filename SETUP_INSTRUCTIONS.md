# 🎮 FIGHT CLUB GAME - Setup Instructions

## 📦 Instalação em PC Novo

### 1. Instalar Python
- Baixe Python 3.8+ de https://python.org
- Durante instalação, marque "Add Python to PATH"

### 2. Instalar Chrome Driver
- Baixe ChromeDriver: https://chromedriver.chromium.org/
- Extraia e coloque no PATH do sistema ou na pasta do projeto

### 3. Instalar Dependências
```bash
# Navegue até a pasta do projeto
cd C:\Users\Gabriel.Glock\Desktop\fightclubgame-main

# Crie ambiente virtual (recomendado)
python -m venv venv

# Ative o ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instale as dependências
pip install selenium pygame requests
```

### 4. Executar o Projeto

#### Para coletar seguidores:
```bash
python smart_scraper.py
```

#### Para jogar:
```bash
python main.py
```

## 📁 Estrutura de Arquivos

```
fightclubgame-main/
├── smart_scraper.py       # Script de coleta do Instagram
├── main.py                # Jogo principal
├── scraped_users.db       # 🗄️ BANCO DE DADOS (SQLite)
├── users.json            # Dados dos seguidores para o jogo
├── followers_data.json   # Dados detalhados dos seguidores
└── profiles/             # Pasta com fotos dos seguidores
    ├── usuario1.jpg
    ├── usuario2.jpg
    └── ...
```

## 🗄️ Banco de Dados

O banco de dados **`scraped_users.db`** é um arquivo SQLite que fica na raiz do projeto.

### Visualizar o Banco de Dados:

#### Opção 1: DB Browser for SQLite (Recomendado)
1. Baixe: https://sqlitebrowser.org/
2. Abra o arquivo `scraped_users.db`
3. Vá na aba "Browse Data" para ver os seguidores

#### Opção 2: Via Python
```python
import sqlite3
import pandas as pd

# Conectar ao banco
conn = sqlite3.connect('scraped_users.db')

# Ver todos os seguidores
df = pd.read_sql_query("SELECT * FROM users", conn)
print(df)

# Ver quantos seguidores tem
count = pd.read_sql_query("SELECT COUNT(*) as total FROM users", conn)
print(f"Total de seguidores no banco: {count['total'][0]}")

conn.close()
```

#### Opção 3: Linha de Comando
```bash
# Instalar sqlite3 (se não tiver)
# Windows: já vem instalado
# Linux: sudo apt-get install sqlite3

# Abrir o banco
sqlite3 scraped_users.db

# Comandos SQL:
.tables                    # Ver tabelas
SELECT COUNT(*) FROM users;  # Contar seguidores
SELECT * FROM users LIMIT 10; # Ver primeiros 10
.quit                      # Sair
```

## 🔄 Comportamento do Scraper

### Primeira Execução (PC Novo):
- Coleta TODOS os seguidores encontrados
- Salva no banco de dados
- Baixa todas as fotos

### Execuções Subsequentes:
- Verifica o banco de dados
- Pula seguidores que já tem foto baixada
- Coleta apenas novos seguidores
- Atualiza o banco incrementalmente

## ⚠️ Notas Importantes

1. **Login Manual**: O script abre o Chrome e você deve fazer login manualmente no Instagram
2. **Limites**: Instagram pode limitar requisições se fizer muitas muito rápido
3. **Backup**: Faça backup do `scraped_users.db` para não perder dados coletados

## 🐛 Troubleshooting

### Erro "chromedriver not found"
- Baixe o ChromeDriver compatível com sua versão do Chrome
- Coloque na pasta do projeto ou no PATH

### Erro "No module named 'selenium'"
- Certifique-se que o venv está ativado
- Execute: `pip install selenium pygame requests`

### Instagram bloqueia login
- Use uma conta real (não nova)
- Espere alguns minutos entre tentativas
- Use delays maiores no script se necessário