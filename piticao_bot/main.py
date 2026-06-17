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

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

def main():
    if not TELEGRAM_TOKEN:
        print("Erro: TELEGRAM_TOKEN não encontrado no arquivo .env.")
        return

    print("Iniciando o Bot Piticao...")
    
    # Criar a aplicação do bot
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Filtros específicos
    application.add_handler(MessageHandler(filters.TEXT, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    # Adicionar o handler para os botões do submenu (Inline Keyboards)
    application.add_handler(CallbackQueryHandler(handle_callback))

    print("Bot está rodando e escutando mensagens... Pressione Ctrl+C para parar.")
    # Inicia o polling (escuta ativa)
    application.run_polling()

if __name__ == "__main__":
    main()
