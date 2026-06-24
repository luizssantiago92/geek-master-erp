from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from services.supabase_service import get_funcionario_by_telegram_id, supabase, deletar_funcionario, alterar_status_funcionario, gerar_novo_codigo, atualizar_encomenda_status, criar_solicitacao_autorizacao, get_usuarios_gold, get_autorizacao_por_id, atualizar_autorizacao
from bot.state import user_states, impersonation_states
from bot.handlers.core import NIVEIS, get_menu_por_nivel
from datetime import datetime

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lida com os cliques nos botões Inline (submenus)."""
    query = update.callback_query
    await query.answer() 
    
    user = update.effective_user
    telegram_id = str(user.id)
    funcionario = get_funcionario_by_telegram_id(telegram_id)
    
    if not funcionario or funcionario['nivel_acesso'] < 3:
        if not query.data.startswith("enc_") and not query.data == "saber_mais_att":
            await query.edit_message_text(text="⛔ Permissão negada.")
            return
            
    data = query.data

    if data.startswith("revogar_escolher_"):
        f_id = data.replace("revogar_escolher_", "")
        f = supabase.table("funcionarios").select("nome").eq("id", f_id).execute().data[0]
        keyboard = [
            [InlineKeyboardButton("✅ Sim, Revogar", callback_data=f"revogar_confirma_{f_id}")],
            [InlineKeyboardButton("❌ Não, Cancelar", callback_data="revogar_cancela")]
        ]
        await query.edit_message_text(f"Tem certeza que deseja revogar **PERMANENTEMENTE** o acesso do usuário **{f['nome']}**?", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        return
        
    if data.startswith("suspender_escolher_"):
        f_id = data.replace("suspender_escolher_", "")
        f = supabase.table("funcionarios").select("nome, ativo").eq("id", f_id).execute().data[0]
        status_atual = "✅ Ativo" if f['ativo'] else "⏸️ Suspenso"
        keyboard = [
            [InlineKeyboardButton("✅ Ativar", callback_data=f"suspender_ativar_{f_id}")],
            [InlineKeyboardButton("⏸️ Desativar", callback_data=f"suspender_desativar_{f_id}")]
        ]
        await query.edit_message_text(f"Usuário: **{f['nome']}**\nStatus atual: {status_atual}\n\nO que você deseja fazer?", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data.startswith("revogar_confirma_"):
        f_id = data.replace("revogar_confirma_", "")
        if deletar_funcionario(f_id):
            await query.edit_message_text("✅ Usuário revogado permanentemente com sucesso.")
        else:
            await query.edit_message_text("❌ Erro ao revogar usuário.")
        return
        
    if data == "revogar_cancela":
        await query.edit_message_text("Ação cancelada.")
        return
        
    if data.startswith("suspender_ativar_"):
        f_id = data.replace("suspender_ativar_", "")
        if alterar_status_funcionario(f_id, True):
            await query.edit_message_text("✅ Usuário ativado com sucesso.")
        else:
            await query.edit_message_text("❌ Erro ao ativar usuário.")
        return
        
    if data.startswith("suspender_desativar_"):
        f_id = data.replace("suspender_desativar_", "")
        if alterar_status_funcionario(f_id, False):
            await query.edit_message_text("⏸️ Usuário desativado com sucesso.")
        else:
            await query.edit_message_text("❌ Erro ao desativar usuário.")
        return

    if data == "broadcast_whatsapp":
        await query.answer("Em breve: Integração direta com o grupo WhatsApp da Equipe Piticas Rio!", show_alert=True)
        return

    if data == "broadcast_telegram_menu":
        from services.supabase_service import get_todos_funcionarios
        todos = get_todos_funcionarios()
        keyboard = [[InlineKeyboardButton("📢 Enviar para TODOS os Usuários Ativos", callback_data="broadcast_telegram_todos")]]
        for f in todos:
            if f.get('ativo', True) and str(f['telegram_id']) != telegram_id:
                keyboard.append([InlineKeyboardButton(f"👤 {f['nome']} ({f['cargo']})", callback_data=f"broadcast_telegram_user_{f['telegram_id']}")])
        keyboard.append([InlineKeyboardButton("❌ Cancelar", callback_data="broadcast_cancela")])
        
        await query.edit_message_text("Selecione para quem deseja enviar a mensagem:", reply_markup=InlineKeyboardMarkup(keyboard))
        return
        
    if data == "broadcast_cancela":
        await query.edit_message_text("Transmissão cancelada.")
        user_states.pop(telegram_id, None)
        return
        
    if data.startswith("broadcast_telegram_"):
        destino = data.replace("broadcast_telegram_", "")
        if destino.startswith("user_"):
            destino = destino.replace("user_", "")
        user_states[telegram_id] = f"esperando_mensagem_broadcast_{destino}"
        alvo_nome = "TODOS os usuários ativos" if destino == "todos" else "o usuário selecionado"
        await query.edit_message_text(f"Digite a mensagem que você quer transmitir para {alvo_nome}.\n\n(Ou digite `Cancelar` para desistir).", parse_mode="Markdown")
        return

    if data.startswith("gerar_"):


        nivel = int(data.split("_")[1])
        if nivel > 1:
            keyboard = [
                [InlineKeyboardButton("🥇 Gold Access (Acesso Total)", callback_data=f"medalhao_{nivel}_Gold")],
                [InlineKeyboardButton("🥈 Silver Access (Acesso Supervisionado)", callback_data=f"medalhao_{nivel}_Silver")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(f"Você escolheu gerar um código para *{NIVEIS.get(nivel)}*.\n\nSelecione a patente Medalhão para este usuário:", parse_mode="Markdown", reply_markup=reply_markup)
        else:
            user_states[telegram_id] = f"esperando_nome_codigo_{nivel}_None"
            await query.edit_message_text(f"Você escolheu gerar um código para *{NIVEIS.get(nivel)}*.\n\nPor favor, digite o **nome** que será atribuído a este usuário ou quiosque (Ex: `Equipe Shopping Metropolitano`).\n\n(Ou digite `Cancelar`)", parse_mode="Markdown")

    elif data.startswith("enc_detalhe_"):
        enc_id = data.replace("enc_detalhe_", "")
        resp = supabase.table("encomendas").select("*").eq("id", enc_id).execute()
        if not resp.data: return
        enc = resp.data[0]
        
        texto = f"🛒 *Pedido #{enc['codigo_pedido']}*\n"
        texto += f"👤 Cliente: {enc['cliente_nome']}\n"
        texto += f"📱 Telefone: {enc.get('cliente_telefone', 'N/A')}\n"
        texto += f"💰 Valor: R$ {enc['valor_total']}\n\n"
        texto += f"📦 *Produtos:*\n{enc['produtos_resumo']}\n\n"
        
        keyboard = []
        if enc['status'] == "PENDENTE":
            texto += "⚠️ *Status:* Aguardando Separação"
            keyboard.append([InlineKeyboardButton("✅ Confirmar Separação", callback_data=f"enc_status_{enc['id']}_PRONTO_RETIRADA")])
        elif enc['status'] == "PRONTO_RETIRADA":
            texto += "🛍️ *Status:* Pronto para Retirada"
            keyboard.append([InlineKeyboardButton("🛍️ Dar Baixa (Entregue)", callback_data=f"enc_status_{enc['id']}_CONCLUIDO")])
            
        keyboard.append([InlineKeyboardButton("❌ Problema / Cancelar", callback_data=f"enc_status_{enc['id']}_CANCELADO")])
        keyboard.append([InlineKeyboardButton("🔙 Voltar", callback_data="enc_voltar")])
        
        await query.edit_message_text(texto, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        
    elif data.startswith("enc_status_"):
        partes = data.split("_")
        enc_id = partes[2]
        novo_status = partes[3]
        
        sucesso = atualizar_encomenda_status(enc_id, novo_status)
        if sucesso:
            status_msg = {"PRONTO_RETIRADA": "Produto separado!", "CONCLUIDO": "Baixa realizada (Entregue)!", "CANCELADO": "Pedido cancelado."}
            await query.edit_message_text(f"✅ Status atualizado com sucesso: {status_msg.get(novo_status, novo_status)}")
        else:
            await query.edit_message_text("❌ Falha ao atualizar o status.")
            
    elif data == "enc_voltar":
        await query.edit_message_text("Ação cancelada. Utilize o menu '📦 Encomendas' novamente para atualizar a lista.")

    elif data.startswith("medalhao_"):
        partes = data.split("_")
        nivel = int(partes[1])
        medalhao = partes[2]
        user_states[telegram_id] = f"esperando_nome_codigo_{nivel}_{medalhao}"
        await query.edit_message_text(f"Patente selecionada: *{medalhao}*\n\nPor favor, digite o **nome** que será atribuído a este usuário (Ex: `Gerente 2`).\nO sufixo `({medalhao} Access)` será adicionado automaticamente.\n\n(Ou digite `Cancelar`)", parse_mode="Markdown")

    elif data.startswith("solicitar_auth_"):
        acao_id = data.replace("solicitar_auth_", "")
        auth_id = criar_solicitacao_autorizacao(funcionario['id'], acao_id)
        if not auth_id:
            await query.edit_message_text("❌ Falha ao solicitar autorização.")
            return
            
        await query.edit_message_text("⏳ Sua solicitação foi enviada aos gestores Gold correspondentes. Aguarde a notificação de aprovação...")
        
        golds = get_usuarios_gold(funcionario['nivel_acesso'])
        if golds:
            keyboard = [
                [InlineKeyboardButton("✅ Autorizar 1 Vez", callback_data=f"auth_unica_{auth_id}")],
                [InlineKeyboardButton("✅ Autorizar Até Hoje 23:59", callback_data=f"auth_dia_{auth_id}")],
                [InlineKeyboardButton("✅ Autorizar Livre", callback_data=f"auth_livre_{auth_id}")],
                [InlineKeyboardButton("❌ Negar Acesso", callback_data=f"auth_negar_{auth_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            for g in golds:
                try:
                    await context.bot.send_message(chat_id=g['telegram_id'], text=f"🔔 *SOLICITAÇÃO DE AUTORIZAÇÃO (SILVER)*\n\nUsuário: {funcionario['nome']}\nAção Solicitada: `{acao_id}`", parse_mode="Markdown", reply_markup=reply_markup)
                except: pass

    elif data.startswith("auth_"):
        partes = data.split("_", 2)
        tipo = partes[1]
        auth_id = partes[2]
        
        auth_req = get_autorizacao_por_id(auth_id)
        if not auth_req:
            await query.edit_message_text("❌ Solicitação não encontrada.")
            return
            
        if auth_req['status'] != 'PENDENTE':
            await query.edit_message_text(f"⚠️ Esta solicitação já foi tratada. (Status: {auth_req['status']})")
            return
            
        status = "PENDENTE"
        expira = None
        if tipo == "unica": status = "AUTORIZADO_UNICA"
        elif tipo == "dia":
            status = "AUTORIZADO_DIA"
            expira = datetime.now().replace(hour=23, minute=59, second=59).isoformat()
        elif tipo == "livre": status = "AUTORIZADO_LIVRE"
        elif tipo == "negar": status = "NEGADO"
            
        atualizar_autorizacao(auth_id, status, funcionario['id'], expira)
        await query.edit_message_text(f"✅ Solicitação processada com status: `{status}`", parse_mode="Markdown")
        
        try:
            if status == "NEGADO":
                await context.bot.send_message(chat_id=auth_req['solicitante']['telegram_id'], text=f"❌ Sua solicitação para `{auth_req['acao_alvo']}` foi *NEGADA* por {funcionario['nome']}.", parse_mode="Markdown")
            else:
                await context.bot.send_message(chat_id=auth_req['solicitante']['telegram_id'], text=f"✅ Sua solicitação para `{auth_req['acao_alvo']}` foi *APROVADA* ({status}). Você já pode executar o comando novamente no painel.", parse_mode="Markdown")
        except: pass


    elif data == "teste_onboarding":
        user_states[telegram_id] = "esperando_codigo_teste"
        await query.edit_message_text("🔑 Envie o *Código de Testador* (TST-...) que você gerou para simularmos o seu primeiro acesso:", parse_mode="Markdown")

    elif data.startswith("teste_nivel_"):
        nivel_teste = int(data.replace("teste_nivel_", ""))
        impersonation_states[telegram_id] = nivel_teste
        nome_nivel = NIVEIS.get(nivel_teste, "Desconhecido")
        await query.edit_message_text(f"🧪 Modo Testador ativado com sucesso!\nVocê agora está usando o bot como: *{nome_nivel}*", parse_mode="Markdown")
        await context.bot.send_message(chat_id=telegram_id, text="Seu menu foi atualizado automaticamente. Para sair, clique no botão '🔙 Sair do Teste' no final da lista.", reply_markup=get_menu_por_nivel(nivel_teste, True))

    elif data == "saber_mais_att":
        try:
            with open("latest_release_notes.txt", "r", encoding="utf-8") as f:
                notas = f.read()
            await query.edit_message_text(f"📝 *Detalhes da Última Atualização:*\n\n{notas}", parse_mode="Markdown")
        except:
            await query.edit_message_text("Não há detalhes adicionais para esta atualização.")
