from telegram import Update
from telegram.ext import ContextTypes

async def handle_boss_messages(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, telegram_id: str, funcionario: dict, nivel_efetivo: int, is_testing: bool) -> bool:
    """Retorna True se a mensagem foi tratada aqui."""
    
    if text == "📊 Dashboards de Resultados":
        await update.message.reply_text("Aqui geraremos links de acesso rápido aos Dashboards executivos do seu painel Web.")
        return True
        
    if text == "🔐 Aprovações Pendentes":
        await update.message.reply_text("Nenhuma requisição de cancelamento ou desconto pendente no balcão no momento.")
        return True
        
    return False
