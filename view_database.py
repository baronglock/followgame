#!/usr/bin/env python3
"""
Visualizador do Banco de Dados de Seguidores
Mostra todos os seguidores coletados de forma organizada
"""

import sqlite3
import os
from datetime import datetime

def view_database():
    """Visualiza o conteúdo do banco de dados"""
    
    db_file = 'scraped_users.db'
    
    # Verifica se o banco existe
    if not os.path.exists(db_file):
        print("❌ Banco de dados não encontrado!")
        print("📝 Execute o smart_scraper.py primeiro para criar o banco")
        return
    
    # Conecta ao banco
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    try:
        # Estatísticas gerais
        cursor.execute("SELECT COUNT(*) FROM users")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE has_picture = 1")
        with_pics = cursor.fetchone()[0]
        
        print("="*80)
        print("🗄️  BANCO DE DADOS DE SEGUIDORES")
        print("="*80)
        print(f"📊 Total de seguidores: {total}")
        print(f"📸 Com fotos baixadas: {with_pics}")
        print(f"❌ Sem fotos: {total - with_pics}")
        print("="*80)
        
        # Menu de opções
        while True:
            print("\n📋 OPÇÕES:")
            print("1. Ver todos os seguidores")
            print("2. Ver apenas com fotos")
            print("3. Ver apenas sem fotos")
            print("4. Buscar seguidor específico")
            print("5. Ver últimos adicionados")
            print("6. Exportar para CSV")
            print("0. Sair")
            
            choice = input("\nEscolha uma opção: ").strip()
            
            if choice == "0":
                break
                
            elif choice == "1":
                cursor.execute("""
                    SELECT username, has_picture, scraped_at 
                    FROM users 
                    ORDER BY scraped_at DESC
                """)
                print_results(cursor.fetchall(), "TODOS OS SEGUIDORES")
                
            elif choice == "2":
                cursor.execute("""
                    SELECT username, has_picture, scraped_at 
                    FROM users 
                    WHERE has_picture = 1
                    ORDER BY scraped_at DESC
                """)
                print_results(cursor.fetchall(), "SEGUIDORES COM FOTOS")
                
            elif choice == "3":
                cursor.execute("""
                    SELECT username, has_picture, scraped_at 
                    FROM users 
                    WHERE has_picture = 0
                    ORDER BY scraped_at DESC
                """)
                print_results(cursor.fetchall(), "SEGUIDORES SEM FOTOS")
                
            elif choice == "4":
                search = input("Digite o username para buscar: ").strip()
                cursor.execute("""
                    SELECT username, profile_pic_url, profile_pic_path, has_picture, scraped_at
                    FROM users 
                    WHERE username LIKE ?
                """, (f"%{search}%",))
                
                results = cursor.fetchall()
                if results:
                    print(f"\n🔍 Encontrados {len(results)} resultados:")
                    for row in results:
                        print(f"\n  👤 Username: {row[0]}")
                        print(f"  📸 Tem foto: {'✅' if row[3] else '❌'}")
                        print(f"  📁 Arquivo: {row[2] or 'N/A'}")
                        print(f"  🔗 URL: {row[1][:50] + '...' if row[1] else 'N/A'}")
                        print(f"  📅 Coletado: {row[4]}")
                else:
                    print("❌ Nenhum seguidor encontrado")
                    
            elif choice == "5":
                limit = input("Quantos últimos? (default 20): ").strip()
                limit = int(limit) if limit.isdigit() else 20
                
                cursor.execute(f"""
                    SELECT username, has_picture, scraped_at 
                    FROM users 
                    ORDER BY scraped_at DESC 
                    LIMIT {limit}
                """)
                print_results(cursor.fetchall(), f"ÚLTIMOS {limit} ADICIONADOS")
                
            elif choice == "6":
                export_to_csv(conn)
                
            else:
                print("❌ Opção inválida!")
                
    except sqlite3.Error as e:
        print(f"❌ Erro ao acessar banco: {e}")
        
    finally:
        conn.close()

def print_results(results, title):
    """Imprime resultados formatados"""
    if not results:
        print("❌ Nenhum resultado encontrado")
        return
        
    print(f"\n{'='*80}")
    print(f"📋 {title} ({len(results)} total)")
    print(f"{'='*80}")
    print(f"{'#':<5} {'Username':<30} {'Foto':<6} {'Data de Coleta':<20}")
    print("-"*80)
    
    for i, (username, has_pic, scraped_at) in enumerate(results[:50], 1):  # Limita a 50 para não poluir
        pic_status = "✅" if has_pic else "❌"
        date = scraped_at[:19] if scraped_at else "N/A"
        print(f"{i:<5} {username:<30} {pic_status:<6} {date:<20}")
    
    if len(results) > 50:
        print(f"\n... e mais {len(results) - 50} seguidores")
    
    input("\nPressione Enter para continuar...")

def export_to_csv(conn):
    """Exporta o banco para CSV"""
    try:
        import pandas as pd
        
        query = "SELECT * FROM users ORDER BY scraped_at DESC"
        df = pd.read_sql_query(query, conn)
        
        filename = f"followers_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False)
        
        print(f"✅ Exportado para {filename}")
        print(f"📊 Total de {len(df)} seguidores exportados")
        
    except ImportError:
        print("❌ Pandas não instalado. Execute: pip install pandas")
    except Exception as e:
        print(f"❌ Erro ao exportar: {e}")

if __name__ == "__main__":
    view_database()