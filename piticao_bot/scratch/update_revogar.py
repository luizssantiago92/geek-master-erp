import os

def update_handlers():
    file_path = "c:/Users/c.barbosa.CELLAIRIS/Downloads/Luiz/Master Geek/piticao_bot/bot/handlers.py"
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update the Menu text for "Revogar Acesso"
    old_revogar_menu = """    elif text == "🚫 Revogar Acesso":
        if funcionario['nivel_acesso'] < 4: return
        user_states[telegram_id] = "esperando_id_revogar"
        await update.message.reply_text("Digite o *ID* do usuário que você deseja remover PERMANENTEMENTE do sistema.\\n\\n(Ou digite `Cancelar` para desistir).", parse_mode="Markdown")
        return"""

    new_revogar_menu = """    elif text == "🚫 Revogar Acesso":
        if funcionario['nivel_acesso'] < 4: return
        user_states[telegram_id] = "esperando_nome_revogar"
        await update.message.reply_text("Digite o **NOME EXATO** (ou parte do nome) do usuário que você deseja remover PERMANENTEMENTE do sistema.\\n\\n(Ou digite `Cancelar` para desistir).", parse_mode="Markdown")
        return"""
    
    content = content.replace(old_revogar_menu, new_revogar_menu)

    # 2. Update the Menu text for "Suspender/Ativar"
    old_suspender_menu = """    elif text == "⏸️ Suspender/Ativar":
        if funcionario['nivel_acesso'] < 4: return
        user_states[telegram_id] = "esperando_id_suspender"
        await update.message.reply_text("Digite o *ID* do usuário seguido da letra *A* (Ativar) ou *D* (Desativar).\\n\\nExemplo: `14 D` (para suspender o acesso do usuário 14)\\n\\n(Ou digite `Cancelar` para desistir).", parse_mode="Markdown")
        return"""

    new_suspender_menu = """    elif text == "⏸️ Suspender/Ativar":
        if funcionario['nivel_acesso'] < 4: return
        user_states[telegram_id] = "esperando_nome_suspender"
        await update.message.reply_text("Digite o **NOME EXATO** (ou parte do nome) do usuário que você deseja suspender ou ativar.\\n\\n(Ou digite `Cancelar` para desistir).", parse_mode="Markdown")
        return"""
    
    content = content.replace(old_suspender_menu, new_suspender_menu)

    # 3. Replace the old states logic. 
    # Let's find exactly the blocks.
    
    old_estado_revogar = """    if estado_atual == "esperando_id_revogar":
        if text.lower() == "cancelar":
            user_states.pop(telegram_id, None)
            await update.message.reply_text("Revogação cancelada.")
            return
            
        from services.supabase_service import deletar_funcionario
        sucesso = deletar_funcionario(text)
        user_states.pop(telegram_id, None)
        if sucesso:
            await update.message.reply_text(f"✅ Usuário com ID `{text}` foi revogado permanentemente. Ele não tem mais acesso ao sistema.", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Ocorreu um erro ou esse ID não existe.")
        return"""

    old_estado_suspender = """    if estado_atual == "esperando_id_suspender":
        if text.lower() == "cancelar":
            user_states.pop(telegram_id, None)
            await update.message.reply_text("Ação cancelada.")
            return
            
        partes = text.split()
        if len(partes) != 2 or partes[1].upper() not in ["A", "D"]:
            await update.message.reply_text("Formato inválido. Digite o ID seguido de A ou D.\\nExemplo: `123 A` (para Ativar) ou `123 D` (para Desativar).\\n(Ou digite Cancelar)", parse_mode="Markdown")
            return
            
        id_alvo = partes[0]
        novo_status = partes[1].upper() == "A"
        
        from services.supabase_service import alterar_status_funcionario
        sucesso = alterar_status_funcionario(id_alvo, novo_status)
        
        if sucesso:
            acao = "ATIVADO ✅" if novo_status else "SUSPENSO ⏸️"
            await update.message.reply_text(f"Usuário com ID `{id_alvo}` foi *{acao}* com sucesso.", parse_mode="Markdown")
            user_states.pop(telegram_id, None)
        else:
            await update.message.reply_text("❌ Erro ao alterar o status. Verifique se o ID existe e tente novamente.")
        return"""
        
    new_estado_nome = """    if estado_atual in ["esperando_nome_revogar", "esperando_nome_suspender"]:
        if text.lower() == "cancelar":
            user_states.pop(telegram_id, None)
            await update.message.reply_text("Ação cancelada.")
            return
            
        from services.supabase_service import supabase
        resp = supabase.table("funcionarios").select("id, nome, ativo").ilike("nome", f"%{text}%").execute()
        
        if not resp.data:
            await update.message.reply_text("Nenhum usuário encontrado com esse nome. Tente novamente ou digite Cancelar.")
            return
            
        acao = "revogar" if estado_atual == "esperando_nome_revogar" else "suspender"
        
        if len(resp.data) > 1:
            keyboard = []
            for f in resp.data:
                keyboard.append([InlineKeyboardButton(f"{f['nome']}", callback_data=f"{acao}_escolher_{f['id']}")])
            await update.message.reply_text("Foram encontrados mais de um usuário. Selecione o correto:", reply_markup=InlineKeyboardMarkup(keyboard))
            return
            
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
            await update.message.reply_text(f"Usuário: **{f['nome']}**\\nStatus atual: {status_atual}\\n\\nO que você deseja fazer?", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        return"""

    content = content.replace(old_estado_revogar, new_estado_nome)
    content = content.replace(old_estado_suspender, "") # We replaced old_estado_revogar with the new combined one, so we just remove the old suspender block

    # 4. Insert handle_callback logic
    new_callbacks = """
    if data.startswith("revogar_escolher_"):
        f_id = data.replace("revogar_escolher_", "")
        from services.supabase_service import supabase
        f = supabase.table("funcionarios").select("nome").eq("id", f_id).execute().data[0]
        keyboard = [
            [InlineKeyboardButton("✅ Sim, Revogar", callback_data=f"revogar_confirma_{f_id}")],
            [InlineKeyboardButton("❌ Não, Cancelar", callback_data="revogar_cancela")]
        ]
        await query.edit_message_text(f"Tem certeza que deseja revogar **PERMANENTEMENTE** o acesso do usuário **{f['nome']}**?", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        return
        
    if data.startswith("suspender_escolher_"):
        f_id = data.replace("suspender_escolher_", "")
        from services.supabase_service import supabase
        f = supabase.table("funcionarios").select("nome, ativo").eq("id", f_id).execute().data[0]
        status_atual = "✅ Ativo" if f['ativo'] else "⏸️ Suspenso"
        keyboard = [
            [InlineKeyboardButton("✅ Ativar", callback_data=f"suspender_ativar_{f_id}")],
            [InlineKeyboardButton("⏸️ Desativar", callback_data=f"suspender_desativar_{f_id}")]
        ]
        await query.edit_message_text(f"Usuário: **{f['nome']}**\\nStatus atual: {status_atual}\\n\\nO que você deseja fazer?", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data.startswith("revogar_confirma_"):
        f_id = data.replace("revogar_confirma_", "")
        from services.supabase_service import deletar_funcionario
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
        from services.supabase_service import alterar_status_funcionario
        if alterar_status_funcionario(f_id, True):
            await query.edit_message_text("✅ Usuário ativado com sucesso.")
        else:
            await query.edit_message_text("❌ Erro ao ativar usuário.")
        return
        
    if data.startswith("suspender_desativar_"):
        f_id = data.replace("suspender_desativar_", "")
        from services.supabase_service import alterar_status_funcionario
        if alterar_status_funcionario(f_id, False):
            await query.edit_message_text("⏸️ Usuário desativado com sucesso.")
        else:
            await query.edit_message_text("❌ Erro ao desativar usuário.")
        return
"""

    # We insert these callbacks right after `data = query.data`
    content = content.replace("    data = query.data", "    data = query.data\n" + new_callbacks)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("DONE")

if __name__ == "__main__":
    update_handlers()
