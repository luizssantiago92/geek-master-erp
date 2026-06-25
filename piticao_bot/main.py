import os
import logging
from dotenv import load_dotenv
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, filters

from bot.handlers import handle_message, handle_callback, handle_photo

# Configurar logs para vermos se há erros
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

import asyncio

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

async def check_notificacoes(app: Application):
    """
    Roda em background e verifica a tabela notificacoes_bot.
    Se houver notificação não lida, dispara para os Administradores e marca como lida.
    """
    from services.supabase_service import buscar_notificacoes_nao_lidas, marcar_notificacao_lida, get_todos_funcionarios
    
    while True:
        try:
            notificacoes = buscar_notificacoes_nao_lidas()
            if notificacoes:
                funcs = get_todos_funcionarios()
                admins = [f for f in funcs if f.get("nivel_acesso") == 4 and f.get("ativo")]
                
                for n in notificacoes:
                    mensagem = f"🔔 *Alerta do Sistema (Painel Web)*\n\n{n['mensagem']}"
                    for admin in admins:
                        try:
                            await app.bot.send_message(
                                chat_id=admin['telegram_id'], 
                                text=mensagem, 
                                parse_mode='Markdown'
                            )
                        except Exception as e:
                            logger.error(f"Erro ao notificar admin {admin['telegram_id']}: {e}")
                    marcar_notificacao_lida(n['id'])
        except Exception as e:
            logger.error(f"Erro no worker de notificações: {e}")
            
        await asyncio.sleep(10)  # Checa a cada 10 segundos

async def post_init(application: Application):
    # Inicia a thread em background para ser o 'Vigia'
    asyncio.create_task(check_notificacoes(application))

def main():
    if not TELEGRAM_TOKEN:
        print("Erro: TELEGRAM_TOKEN não encontrado no arquivo .env.")
        return

    print("Iniciando o Bot Piticao...")
    
    # Criar a aplicação do bot e registrar o post_init hook
    application = Application.builder().token(TELEGRAM_TOKEN).post_init(post_init).build()

    # Filtros específicos
    from bot.handlers.grupo_handler import processar_mensagem_grupo
    application.add_handler(MessageHandler(filters.ChatType.GROUPS & (filters.TEXT | filters.UpdateType.EDITED_MESSAGE), processar_mensagem_grupo))
    
    application.add_handler(MessageHandler(filters.TEXT | filters.Sticker.ALL, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    # Adicionar o handler para os botões do submenu (Inline Keyboards)
    application.add_handler(CallbackQueryHandler(handle_callback))

    print("Bot está rodando e escutando mensagens... Pressione Ctrl+C para parar.")
    # Inicia o polling (escuta ativa)
    application.run_polling()

if __name__ == "__main__":
    main()
