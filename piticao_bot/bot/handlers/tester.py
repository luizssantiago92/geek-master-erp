from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from services.supabase_service import adicionar_perfil_teste, salvar_produto
from bot.state import user_states, impersonation_states
from bot.handlers.core import get_menu_por_nivel, NIVEIS

async def handle_tester_messages(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, telegram_id: str, funcionario: dict, nivel_efetivo: int, is_testing: bool) -> bool:
    """Retorna True se a mensagem foi tratada aqui."""
    nivel_real = funcionario['nivel_acesso']

    # Entrando no menu Modo Testador
    if text == "🧑‍💻 Modo Testador" and nivel_real == 5:
        keyboard = [
            ["1️⃣ Quiosque Teste", "2️⃣ Marketing Teste", "3️⃣ Boss Teste"],
            ["🔙 Voltar ao Menu"]
        ]
        await update.message.reply_text("🧑‍💻 **MODO TESTADOR**\n\nEscolha qual interface você deseja simular:\n*(Qualquer ação tomada dentro do modo teste será salva com a tag [TESTE])*", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True), parse_mode="Markdown")
        return True

    # Botões de Simulação
    simulacoes = {
        "1️⃣ Quiosque Teste": 1,
        "2️⃣ Marketing Teste": 3,
        "3️⃣ Boss Teste": 4
    }

    if text in simulacoes and nivel_real == 5:
        nivel_teste = simulacoes[text]
        impersonation_states[telegram_id] = nivel_teste
        nome_exibicao = NIVEIS.get(nivel_teste)
        
        await update.message.reply_text(f"*(SIMULAÇÃO INICIADA)*\nVocê agora está logado como **{nome_exibicao}**.\nTodas as suas ações a partir de agora estão seguras na Sandbox.", parse_mode="Markdown")
        await update.message.reply_text("Sua área de trabalho foi carregada no teclado abaixo.", reply_markup=get_menu_por_nivel(nivel_teste, True))
        return True

    if text == "🔙 Sair do Teste" and is_testing:
        impersonation_states.pop(telegram_id, None)
        await update.message.reply_text("🧪 Teste encerrado. Bem-vindo de volta à conta de Administrador principal.", reply_markup=get_menu_por_nivel(nivel_real, False))
        return True

    return False
