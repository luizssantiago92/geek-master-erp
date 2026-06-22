from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from services.supabase_service import get_funcionario_by_telegram_id, validar_e_usar_codigo, registrar_master_admin
from bot.state import user_states, impersonation_states, last_interaction
from bot.handlers.core import get_menu_por_nivel, obter_saudacao
from datetime import datetime
import os

# Importa os manipuladores modulares
from bot.handlers.admin import handle_admin_messages
from bot.handlers.boss import handle_boss_messages
from bot.handlers.marketing import handle_marketing_messages
from bot.handlers.quiosque import handle_quiosque_messages
from bot.handlers.tester import handle_tester_messages

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Router principal que delega mensagens para os manipuladores específicos."""
    if not update.message: return

    text = update.message.text or ""
    telegram_id = str(update.message.from_user.id)
    agora = datetime.now()
    
    ultima = last_interaction.get(telegram_id)
    if ultima and (agora - ultima).seconds < 1:
        return
    last_interaction[telegram_id] = agora

    funcionario = get_funcionario_by_telegram_id(telegram_id)
    is_testing = telegram_id in impersonation_states
    nivel_efetivo = impersonation_states.get(telegram_id, funcionario['nivel_acesso'] if funcionario else 0)

    # 1. Onboarding e Comandos Básicos (Não logados)
    if not funcionario:
        if text.startswith('/start'):
            codigo = text.replace('/start', '').strip()
            if codigo:
                # Checa a senha mestra silenciosamente
                if codigo == os.getenv("MASTER_ADMIN_CODE"):
                    if registrar_master_admin(telegram_id, update.message.from_user.full_name):
                        try: await update.message.delete()
                        except: pass
                        await update.message.reply_text("👑 Acesso Master Confirmado! Seu menu foi carregado abaixo:", reply_markup=get_menu_por_nivel(4))
                    return
                
                if codigo.startswith("TST-"):
                    await update.message.reply_text("❌ Códigos de Testador (TST-) só podem ser usados dentro do Menu 'Modo Testador', por um Administrador logado.")
                    return
                sucesso, resultado = validar_e_usar_codigo(telegram_id, update.message.from_user.full_name, codigo)
                if sucesso:
                    func = resultado
                    try: await update.message.delete()
                    except: pass
                    await update.message.reply_text(f"✅ Bem-vindo(a), {func['nome']}! Seu acesso foi confirmado como {func['cargo']}.")
                    await update.message.reply_text("Seu menu foi carregado abaixo:", reply_markup=get_menu_por_nivel(func['nivel_acesso']))
                    return
                else:
                    await update.message.reply_text(resultado)
                    return
        await update.message.reply_text("Olá! Eu sou o Piticão 🐶, o mascote oficial da Geek Master.\nPara acessar o sistema, peça ao seu Administrador para gerar um código de acesso.\n\nSe já tiver um código, use o link que ele te mandou ou digite `/start SEU_CODIGO`.")
        return

    # Verificação de status (Suspenso)
    if not funcionario.get("ativo", True):
        await update.message.reply_text("⛔ Seu acesso está temporariamente suspenso. Procure a administração.")
        return

    estado_atual = user_states.get(telegram_id)

    # Comandos Globais e Comuns a todos
    if text == "/start":
        saudacao = obter_saudacao()
        await update.message.reply_text(f"{saudacao}, {funcionario['nome']}! 🐶 O que vamos fazer hoje?", parse_mode="Markdown", reply_markup=get_menu_por_nivel(nivel_efetivo, is_testing))
        user_states.pop(telegram_id, None)
        return

    if text == "🔙 Voltar ao Menu":
        user_states.pop(telegram_id, None)
        await update.message.reply_text("Retornando ao menu principal...", reply_markup=get_menu_por_nivel(nivel_efetivo, is_testing))
        return



    if text == "🔗 Página de Ajustes":
        from services.supabase_service import gerar_sessao_magica
        token = gerar_sessao_magica(telegram_id, nivel_efetivo)
        if token:
            link = f"http://localhost:5173/admin?token={token}"
            await update.message.reply_text(
                f"🌐 *Acesso Rápido Web*\n\nSeu link de acesso seguro foi gerado!\n"
                f"Como você está rodando o site localmente, o Telegram não permite botões diretos para 'localhost'.\n\n"
                f"Por favor, clique no link abaixo ou copie e cole no seu navegador:\n\n"
                f"{link}\n\n"
                f"_(Link de uso único válido por 24 horas)_", 
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("❌ Erro ao gerar link de acesso. Tente novamente mais tarde.")
        return

    # Delegação para os manipuladores modulares (Roteamento)
    # A ordem aqui define quem processa primeiro (importante para menus com mesmo nome, se houver)
    tratado = False

    if nivel_efetivo >= 4 or (estado_atual and estado_atual.startswith("esperando_nome_codigo_")):
        tratado = await handle_admin_messages(update, context, text, telegram_id, funcionario, nivel_efetivo, is_testing)
        if tratado: return

    if nivel_efetivo >= 3 and not tratado:
        tratado = await handle_boss_messages(update, context, text, telegram_id, funcionario, nivel_efetivo, is_testing)
        if tratado: return

    if nivel_efetivo >= 2 and not tratado:
        tratado = await handle_marketing_messages(update, context, text, telegram_id, funcionario, nivel_efetivo, is_testing)
        if tratado: return

    if (nivel_efetivo >= 1 or is_testing) and not tratado:
        tratado = await handle_quiosque_messages(update, context, text, telegram_id, funcionario, nivel_efetivo, is_testing)
        if tratado: return

    if (nivel_efetivo == 4 or is_testing) and not tratado:
        tratado = await handle_tester_messages(update, context, text, telegram_id, funcionario, nivel_efetivo, is_testing)
        if tratado: return

    # Eco padrão para outras mensagens soltas de usuários registrados (Chat com IA)
    if text and not tratado:
        from services.gemini_service import chat_com_persona
        await context.bot.send_chat_action(chat_id=telegram_id, action='typing')
        resposta = chat_com_persona(text)
        await update.message.reply_text(resposta)
