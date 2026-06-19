import asyncio
import os
import sys
from dotenv import load_dotenv
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton

# Adiciona o diretório pai (raiz do bot) ao PYTHONPATH para importar os serviços
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.supabase_service import get_todos_funcionarios

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def main():
    if not TELEGRAM_BOT_TOKEN:
        print("Erro: TELEGRAM_BOT_TOKEN não encontrado.")
        return

    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    funcionarios = get_todos_funcionarios()
    
    if not funcionarios:
        print("Nenhum funcionário encontrado no banco de dados.")
        return

    # Tenta ler as notas de atualização
    notas_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "latest_release_notes.txt")
    
    tem_notas_visuais = False
    
    try:
        with open(notas_file, "r", encoding="utf-8") as f:
            notas = f.read().strip()
            if notas:
                tem_notas_visuais = True
    except FileNotFoundError:
        pass

    sucessos = 0
    falhas = 0

    print(f"Iniciando broadcast de atualização para {len(funcionarios)} usuários...")

    for f in funcionarios:
        if not f.get("ativo", True):
            continue
            
        telegram_id = f["telegram_id"]
        nome = f["nome"]
        
        # Monta a mensagem base
        if tem_notas_visuais:
            mensagem = f"Olá {nome}! 🐶\n\n🔄 *O Piticão recebeu uma Nova Atualização!*\nImplementamos melhorias e algumas coisas mudaram na forma de usar o sistema."
            keyboard = [[InlineKeyboardButton("🔍 Saber Mais (O que mudou?)", callback_data="saber_mais_att")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
        else:
            mensagem = f"Olá {nome}! 🐶\n\n🔄 *Atualização do Sistema:*\nO ERP Project acabou de ser atualizado com melhorias técnicas de estabilidade e performance. Nenhuma função mudou de lugar!"
            reply_markup = None
            
        try:
            await bot.send_message(chat_id=telegram_id, text=mensagem, parse_mode="Markdown", reply_markup=reply_markup)
            sucessos += 1
            print(f"[OK] Enviado para {nome} ({telegram_id})")
        except Exception as e:
            falhas += 1
            print(f"[ERRO] Falha ao enviar para {nome} ({telegram_id}): {e}")
            
    print("\n--- RESUMO DO DEPLOY ---")
    print(f"Mensagens enviadas com sucesso: {sucessos}")
    print(f"Falhas (usuário bloqueou o bot, etc): {falhas}")

if __name__ == "__main__":
    asyncio.run(main())
