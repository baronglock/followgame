#!/usr/bin/env python3
"""
Setup inicial para o Fight Club Game
Instala dependências e configura o ambiente
"""

import subprocess
import sys
import os

def install_requirements():
    """Instala as dependências necessárias"""
    print("📦 Instalando dependências...")
    
    requirements = [
        'selenium',
        'pygame', 
        'requests',
        'pandas'  # Para visualizar o banco de dados facilmente
    ]
    
    for package in requirements:
        print(f"  Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    print("✅ Dependências instaladas!")

def create_folders():
    """Cria as pastas necessárias"""
    print("\n📁 Criando estrutura de pastas...")
    
    folders = ['profiles', 'backups']
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"  ✅ Pasta '{folder}' criada")
        else:
            print(f"  ⏭️ Pasta '{folder}' já existe")

def check_chromedriver():
    """Verifica se o ChromeDriver está disponível"""
    print("\n🔍 Verificando ChromeDriver...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        
        # Tenta criar uma instância do driver
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        driver.quit()
        print("  ✅ ChromeDriver funcionando!")
        return True
    except Exception as e:
        print("  ❌ ChromeDriver não encontrado!")
        print("  📥 Baixe em: https://chromedriver.chromium.org/")
        print("  📂 Coloque o arquivo na pasta do projeto ou no PATH do sistema")
        return False

def check_database():
    """Verifica o banco de dados"""
    print("\n🗄️ Verificando banco de dados...")
    
    db_file = 'scraped_users.db'
    
    if os.path.exists(db_file):
        import sqlite3
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            print(f"  ✅ Banco de dados existe com {count} seguidores")
        except:
            print("  ⚠️ Banco de dados existe mas está vazio")
        
        conn.close()
    else:
        print("  📝 Banco de dados será criado na primeira execução")

def main():
    print("="*60)
    print("🎮 FIGHT CLUB GAME - Setup Inicial")
    print("="*60)
    
    # 1. Instalar dependências
    try:
        install_requirements()
    except Exception as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        print("💡 Tente: python -m pip install --upgrade pip")
        sys.exit(1)
    
    # 2. Criar pastas
    create_folders()
    
    # 3. Verificar ChromeDriver
    chromedriver_ok = check_chromedriver()
    
    # 4. Verificar banco de dados
    check_database()
    
    # Resumo final
    print("\n" + "="*60)
    print("📊 RESUMO DA INSTALAÇÃO")
    print("="*60)
    
    if chromedriver_ok:
        print("✅ Setup completo! Você pode executar:")
        print("\n  Para coletar seguidores:")
        print("  > python smart_scraper.py")
        print("\n  Para jogar:")
        print("  > python main.py")
    else:
        print("⚠️ Setup parcialmente completo!")
        print("❌ Você precisa instalar o ChromeDriver antes de usar o scraper")
        print("✅ Mas você já pode jogar se tiver o arquivo users.json")
    
    print("\n📖 Veja SETUP_INSTRUCTIONS.md para mais detalhes")
    print("="*60)

if __name__ == "__main__":
    main()