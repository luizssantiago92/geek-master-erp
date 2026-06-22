from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from services.supabase_service import supabase, get_todos_funcionarios, gerar_novo_codigo
from bot.state import user_states
from bot.handlers.core import get_menu_por_nivel, NIVEIS
import qrcode
from io import BytesIO

async def handle_admin_messages(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, telegram_id: str, funcionario: dict, nivel_efetivo: int, is_testing: bool) -> bool:
    """Retorna True se a mensagem foi tratada aqui."""
    estado_atual = user_states.get(telegram_id)
    nivel_real = funcionario['nivel_acesso']

    if text == "🛠️ Sistema" and nivel_efetivo == 4:
        keyboard = ReplyKeyboardMarkup([
            ["🎟️ Gerar Código", "👥 Listar Usuários"],
            ["📢 Transmissão Global", "⏸️ Suspender/Ativar"],
            ["🚫 Revogar Acesso", "📊 Resumo do Sistema"],
            ["🔙 Voltar ao Menu"]
        ], resize_keyboard=True)
        await update.message.reply_text("Você acessou o menu de **Sistema**.", reply_markup=keyboard, parse_mode='Markdown')
        return True

    if text == "🎭 Personas" and nivel_efetivo == 4:
        keyboard = ReplyKeyboardMarkup([
            ["🎭 Escolher Persona", "📊 Ranking Personas"],
            ["🔙 Voltar ao Menu"]
        ], resize_keyboard=True)
        await update.message.reply_text("Você acessou o menu de **Personas**.", reply_markup=keyboard, parse_mode='Markdown')
        return True

    if text == "🧪 Modo Testador" and nivel_efetivo == 4:
        keyboard = ReplyKeyboardMarkup([
            ["📦 Estoque Teste", "🧪 Testar Usuários"],
            ["🔙 Voltar ao Menu"]
        ], resize_keyboard=True)
        await update.message.reply_text("Você acessou o **Modo Testador**.", reply_markup=keyboard, parse_mode='Markdown')
        return True

    if text == "🧪 Testar Usuários" and nivel_real == 4:
        keyboard = [
            [InlineKeyboardButton("🔑 Inserir TST- (Simular Novo Acesso)", callback_data="teste_onboarding")]
        ]
        perfis = funcionario.get('perfis_teste', [])
        for p in perfis:
            keyboard.append([InlineKeyboardButton(f"Perfil {NIVEIS.get(p)}", callback_data=f"teste_nivel_{p}")])
        await update.message.reply_text("🧪 **Testar Usuários - Perfis Criados**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return True

    if text == "📊 Ranking Personas":
        if funcionario['nivel_acesso'] < 4:
            await update.message.reply_text("⛔ Acesso Negado.")
            return True
        from services.supabase_service import get_ranking_personas
        ranking = get_ranking_personas()
        if not ranking:
            await update.message.reply_text("📉 Ainda não há dados de ranking das personas.")
            return True
        texto_ranking = "🏆 *Ranking de Uso das Personas* 🏆\n\n"
        for i, p in enumerate(ranking, 1):
            texto_ranking += f"{i}º - *{p['persona_nome']}* ({p['vezes_selecionada']} escolhas)\n"
        texto_ranking += "\n_Este ranking ajuda a identificar quais personas remover no futuro._"
        await update.message.reply_text(texto_ranking, parse_mode="Markdown")
        return True

    # Comandos do menu Sistema
    acoes_restritas = ["🎟️ Gerar Código", "🚫 Revogar Acesso", "⏸️ Suspender/Ativar", "📢 Transmissão Global", "👥 Listar Usuários"]
    if text in acoes_restritas:
        if funcionario.get('medalhao') == 'Silver':
            from services.supabase_service import verificar_autorizacao_valida
            if not verificar_autorizacao_valida(funcionario['id'], text):
                keyboard = [[InlineKeyboardButton("✅ Solicitar Autorização Gold", callback_data=f"solicitar_auth_{text}")]]
                await update.message.reply_text(f"⛔ *Acesso Restrito!*\nVocê possui a patente *Silver* e precisa de autorização para usar o comando `{text}`.", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
                return True
                
        if text == "🎟️ Gerar Código":
            keyboard = [
                [InlineKeyboardButton("1️⃣ Quiosque (Vendedor)", callback_data="gerar_1")],
                [InlineKeyboardButton("2️⃣ Marketing", callback_data="gerar_2")],
                [InlineKeyboardButton("3️⃣ Boss", callback_data="gerar_3")],
                [InlineKeyboardButton("4️⃣ Administrador (ADM)", callback_data="gerar_4")],
                [InlineKeyboardButton("🧪 Código de Testador (TST-)", callback_data="gerar_teste_menu")]
            ]
            await update.message.reply_text("Para qual tipo de usuário você deseja gerar o código de acesso?", reply_markup=InlineKeyboardMarkup(keyboard))
            return True
            
        elif text == "👥 Listar Usuários":
            if funcionario['nivel_acesso'] < 4: return True
            todos = get_todos_funcionarios()
            msg = "👥 *Usuários Ativos no Sistema:*\n\n"
            for f in todos:
                status_txt = "✅ Ativo" if f.get("ativo", True) else "⏸️ Suspenso"
                msg += f"👤 *{f['nome']}* ({status_txt})\n├ ID: `{f['id']}`\n├ Cargo: {f['cargo']}\n└ Nível: {f['nivel_acesso']}\n\n"
            await update.message.reply_text(msg, parse_mode="Markdown")
            return True
            
        elif text == "📢 Transmissão Global":
            if funcionario['nivel_acesso'] < 4: return True
            user_states[telegram_id] = "esperando_mensagem_broadcast"
            await update.message.reply_text("Digite a mensagem que você quer transmitir para TODOS os celulares do sistema.\n\n(Ou digite `Cancelar` para desistir).", parse_mode="Markdown")
            return True
            
        elif text == "🚫 Revogar Acesso":
            if funcionario['nivel_acesso'] < 4: return True
            user_states[telegram_id] = "esperando_nome_revogar"
            await update.message.reply_text("Digite o **NOME EXATO** (ou parte do nome) do usuário que você deseja remover PERMANENTEMENTE do sistema.\n\n(Ou digite `Cancelar` para desistir).", parse_mode="Markdown")
            return True
            
        elif text == "⏸️ Suspender/Ativar":
            if funcionario['nivel_acesso'] < 4: return True
            user_states[telegram_id] = "esperando_nome_suspender"
            await update.message.reply_text("Digite o **NOME EXATO** (ou parte do nome) do usuário que você deseja suspender ou ativar.\n\n(Ou digite `Cancelar` para desistir).", parse_mode="Markdown")
            return True

    if text == "📊 Resumo do Sistema" and nivel_efetivo == 4:
        todos = get_todos_funcionarios()
        await update.message.reply_text(f"📊 *Status Atual do Piticão:*\n\n- Bot Operacional: Sim\n- Usuários Logados: {len(todos)}\n- Integração Gemini 1.5: Online\n\n(Painel Web em breve)", parse_mode="Markdown")
        return True

    # Estados do Admin
    if estado_atual == "esperando_mensagem_broadcast":
        if text.lower() == "cancelar":
            user_states.pop(telegram_id, None)
            await update.message.reply_text("Transmissão cancelada.")
            return True
        funcionarios = get_todos_funcionarios()
        sucessos = 0
        for f in funcionarios:
            if str(f["telegram_id"]) != telegram_id:
                try:
                    await context.bot.send_message(chat_id=f["telegram_id"], text=f"📢 *MENSAGEM DA ADMINISTRAÇÃO:*\n\n{text}", parse_mode="Markdown")
                    sucessos += 1
                except: pass
        user_states.pop(telegram_id, None)
        await update.message.reply_text(f"✅ Transmissão enviada com sucesso para {sucessos} usuário(s).")
        return True

    if estado_atual in ["esperando_nome_revogar", "esperando_nome_suspender"]:
        if text.lower() == "cancelar":
            user_states.pop(telegram_id, None)
            await update.message.reply_text("Ação cancelada.")
            return True
        resp = supabase.table("funcionarios").select("id, nome, ativo").ilike("nome", f"%{text}%").execute()
        if not resp.data:
            await update.message.reply_text("Nenhum usuário encontrado com esse nome. Tente novamente ou digite Cancelar.")
            return True
        acao = "revogar" if estado_atual == "esperando_nome_revogar" else "suspender"
        if len(resp.data) > 1:
            keyboard = []
            for f in resp.data:
                keyboard.append([InlineKeyboardButton(f"{f['nome']}", callback_data=f"{acao}_escolher_{f['id']}")])
            await update.message.reply_text("Foram encontrados mais de um usuário. Selecione o correto:", reply_markup=InlineKeyboardMarkup(keyboard))
            return True
        f = resp.data[0]
        user_states.pop(telegram_id, None)
        if acao == "revogar":
            keyboard = [
                [InlineKeyboardButton("✅ Sim, Revogar", callback_data=f"revogar_confirma_{f['id']}")],
                [InlineKeyboardButton("❌ Não, Cancelar", callback_data="revogar_cancela")]
            ]
            await update.message.reply_text(f"Tem certeza que deseja revogar **PERMANENTEMENTE** o acesso do usuário **{f['nome']}**?", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            status_atual = "✅ Ativo" if f['ativo'] else "⏸️ Suspenso"
            keyboard = [
                [InlineKeyboardButton("✅ Ativar", callback_data=f"suspender_ativar_{f['id']}")],
                [InlineKeyboardButton("⏸️ Desativar", callback_data=f"suspender_desativar_{f['id']}")]
            ]
            await update.message.reply_text(f"Usuário: **{f['nome']}**\nStatus atual: {status_atual}\n\nO que você deseja fazer?", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        return True

    if estado_atual and estado_atual.startswith("esperando_nome_codigo_"):
        if text.lower() == "cancelar":
            user_states.pop(telegram_id, None)
            await update.message.reply_text("Geração de código cancelada.")
            return True
        partes = estado_atual.split("_")
        nivel_para_gerar = int(partes[3])
        medalhao = partes[4] if partes[4] != "None" else None
        is_teste = len(partes) > 5 and partes[5] == "Teste"
        nome_customizado = text.strip()
        if medalhao: nome_customizado = f"{nome_customizado} ({medalhao} Access)"
        
        codigo = gerar_novo_codigo(funcionario['id'], nivel_para_gerar, nome_atribuido=nome_customizado, medalhao=medalhao, is_tester=is_teste)
        user_states.pop(telegram_id, None)
        
        if codigo:
            bot_username = context.bot.username
            deep_link = f"https://t.me/{bot_username}?start={codigo}"
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(deep_link)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            bio = BytesIO()
            bio.name = "codigo_acesso.png"
            img.save(bio, "PNG")
            bio.seek(0)
            
            mensagem = (
                f"🎟️ *Código de Acesso Gerado com Sucesso!*\n\n"
                f"Cargo: *{NIVEIS.get(nivel_para_gerar)}*\n"
                f"Nome Vinculado: *{nome_customizado}*\n\n"
                f"💡 _Mande o usuário apontar a câmera do celular para este QR Code, ou envie a imagem para ele!_\n"
                f"⚠️ *ATENÇÃO: Este código expira em 30 minutos!*\n\n"
                f"*(Alternativa: envie o link ou código abaixo)*\n"
                f"Link direto: {deep_link}"
            )
            await context.bot.send_photo(chat_id=telegram_id, photo=bio, caption=mensagem, parse_mode="Markdown")
            await update.message.reply_text(f"`{codigo}`", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Erro ao gerar o código no banco de dados.")
        return True

    return False
