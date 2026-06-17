import os
import urllib.parse
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from services.supabase_service import (
    get_funcionario_by_telegram_id, 
    validar_e_usar_codigo, 
    registrar_master_admin,
    gerar_novo_codigo
)
from services.gemini_service import analisar_imagem_gemini
import tempfile

user_states = {}  # Dicionário simples para guardar estado das conversas do ADM


load_dotenv()
MASTER_ADMIN_CODE = os.getenv("MASTER_ADMIN_CODE")

# Mapeamento de níveis para texto
NIVEIS = {
    1: "Quiosque (Vendedor)",
    2: "Marketing",
    3: "Boss",
    4: "Administrador"
}

def get_menu_por_nivel(nivel: int) -> ReplyKeyboardMarkup:
    """Retorna o teclado interativo (ReplyKeyboardMarkup) apropriado para o nível de acesso."""
    if nivel == 1:
        keyboard = [
            ["📦 Baixa em Encomenda", "🏷️ Cadastrar Produto"],
            ["🔍 Consultar Estoque"],
            ["🎭 Escolher Persona"]
        ]
    elif nivel == 2:
        keyboard = [
            ["🗺️ Postar no Maps", "💬 Disparo Comunidades"],
            ["🎭 Escolher Persona"]
        ]
    elif nivel == 3:
        keyboard = [
            ["📊 Dashboards de Resultados"],
            ["🔐 Aprovações Pendentes"],
            ["🎭 Escolher Persona"]
        ]
    elif nivel == 4:
        keyboard = [
            ["🎟️ Gerar Código", "👥 Listar Usuários"],
            ["📢 Transmissão Global", "⏸️ Suspender/Ativar"],
            ["🚫 Revogar Acesso", "📊 Resumo do Sistema"],
            ["🎭 Escolher Persona", "📊 Ranking Personas"]
        ]
    else:
        keyboard = [["/start"]]
        
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa mensagens de texto."""
    if not update.message:
        return

    text = update.message.text or ""
    telegram_id = str(update.message.from_user.id)
    
    # 1. Removido o bloqueio de comandos puros para que /start e /menu funcionem.

    funcionario = get_funcionario_by_telegram_id(telegram_id)
    
    # STEALTH MODE: Zero-Trust Absoluto
    # Se não existe no banco, ignora completamente a mensagem sem avisar nada.
    if not funcionario:
        return
        
    estado_atual = user_states.get(telegram_id)
    
    # ==============================================================
    # A PARTIR DAQUI, O USUÁRIO ESTÁ AUTENTICADO COMO FUNCIONÁRIO
    # ==============================================================
    
    if not funcionario.get("ativo", True):
        await update.message.reply_text("⛔ *Acesso Negado:*\nSeu acesso ao sistema Piticão está temporariamente suspenso. Procure a Administração.", parse_mode="Markdown")
        return
    
    if estado_atual == "esperando_mensagem_broadcast":
        if text.lower() == "cancelar":
            user_states.pop(telegram_id, None)
            await update.message.reply_text("Transmissão cancelada.")
            return
        
        from services.supabase_service import get_todos_funcionarios
        funcionarios = get_todos_funcionarios()
        sucessos = 0
        for f in funcionarios:
            if str(f["telegram_id"]) != telegram_id:
                try:
                    await context.bot.send_message(chat_id=f["telegram_id"], text=f"📢 *MENSAGEM DA ADMINISTRAÇÃO:*\n\n{text}", parse_mode="Markdown")
                    sucessos += 1
                except Exception:
                    pass
        user_states.pop(telegram_id, None)
        await update.message.reply_text(f"✅ Transmissão enviada com sucesso para {sucessos} usuário(s).")
        return

    if estado_atual == "esperando_id_revogar":
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
        return

    if estado_atual and estado_atual.startswith("esperando_nome_codigo_"):
        if text.lower() == "cancelar":
            user_states.pop(telegram_id, None)
            await update.message.reply_text("Geração de código cancelada.")
            return
            
        partes = estado_atual.split("_")
        nivel_para_gerar = int(partes[3])
        medalhao = partes[4] if partes[4] != "None" else None
        
        nome_customizado = text.strip()
        
        # Anexa o nível Medalhão se existir
        if medalhao:
            nome_customizado = f"{nome_customizado} ({medalhao} Access)"
        
        from services.supabase_service import gerar_novo_codigo
        codigo = gerar_novo_codigo(funcionario['id'], nivel_para_gerar, nome_atribuido=nome_customizado, medalhao=medalhao)
        user_states.pop(telegram_id, None)
        
        if codigo:
            # Prepara a mensagem de compartilhamento para o WhatsApp
            import urllib.parse
            mensagem_whatsapp = (
                f"Olá! Este é o seu código de acesso exclusivo para o bot Piticão.\n\n"
                f"Cargo: {NIVEIS.get(nivel_para_gerar)}\n"
                f"Código: {codigo}\n\n"
                f"Abra o Telegram, procure pelo nosso bot e envie este código para validar seu acesso.\n\n"
                f"⚠️ *ATENÇÃO:* Este código expira em 30 minutos! Caso ele expire, você terá que solicitar um novo código."
            )
            texto_url = urllib.parse.quote(mensagem_whatsapp)
            link_whatsapp = f"https://api.whatsapp.com/send?text={texto_url}"
            
            # Adiciona o botão de compartilhar
            keyboard_share = [[InlineKeyboardButton("📲 Compartilhar via WhatsApp", url=link_whatsapp)]]
            reply_markup_share = InlineKeyboardMarkup(keyboard_share)

            await update.message.reply_text(
                f"🎟️ *Código de Acesso Gerado com Sucesso!*\n\n"
                f"Cargo: *{NIVEIS.get(nivel_para_gerar)}*\n"
                f"Nome Vinculado: *{nome_customizado}*\n"
                f"Código: `{codigo}`\n\n"
                f"💡 _Dica: Você pode clicar no código acima para copiar ou usar o botão abaixo para enviar direto pro WhatsApp._",
                parse_mode="Markdown",
                reply_markup=reply_markup_share
            )
        else:
            await update.message.reply_text("❌ Erro ao gerar o código no banco de dados.")
        return

    if estado_atual == "esperando_id_suspender":
        if text.lower() == "cancelar":
            user_states.pop(telegram_id, None)
            await update.message.reply_text("Ação cancelada.")
            return
            
        partes = text.split()
        if len(partes) != 2 or partes[1].upper() not in ["A", "D"]:
            await update.message.reply_text("Formato inválido. Digite o ID seguido de A ou D.\nExemplo: `123 A` (para Ativar) ou `123 D` (para Desativar).\n(Ou digite Cancelar)", parse_mode="Markdown")
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
        return

    # Comando Inicial ou Menu (Boas vindas e exibição do Teclado)
    if text.startswith("/start") or text.startswith("/menu"):
        await update.message.reply_text(f"Olá {funcionario['nome']}! Sou o Piticão 🐶.\nSua área de trabalho ({NIVEIS.get(funcionario['nivel_acesso'])}) já está carregada no teclado abaixo.", reply_markup=get_menu_por_nivel(funcionario['nivel_acesso']))
        return

    # Tratamento de Fotos (OCR de Notas / Produtos)
    if update.message.photo:
        await update.message.reply_text("📸 Imagem recebida! Processando com a Inteligência Artificial do Piticão...")
        
        try:
            # Pega a foto em melhor qualidade (última da lista)
            photo_file = await update.message.photo[-1].get_file()
            
            # Cria um arquivo temporário no sistema
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_img:
                caminho_temporario = temp_img.name
                
            # Baixa a imagem do servidor do Telegram
            await photo_file.download_to_drive(caminho_temporario)
            
            # Envia para a API do Gemini processar
            resultado = analisar_imagem_gemini(caminho_temporario)
            
            # Responde ao usuário com o resultado
            await update.message.reply_text(f"🤖 *Resultado da Leitura IA:*\n`{resultado}`", parse_mode="Markdown")
            
            # Limpa o arquivo temporário
            os.remove(caminho_temporario)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ocorreu um erro ao processar a foto: {e}")
            
        return
        
    # Tratamento de Figurinhas (Repreensão de Vendedores)
    if update.message.sticker:
        await update.message.reply_text("⛔ *Ação não permitida!*\nBrincadeiras e figurinhas não são adequadas para este canal corporativo. Por favor, mantenha o foco no trabalho e utilize os botões do menu abaixo.", parse_mode="Markdown")
        return
        
    # ==============================================================
    # LÓGICA DOS BOTÕES DOS MENUS INTERATIVOS
    # ==============================================================
    
    # --- Menu Nível 1 (Quiosque) ---
    if text == "📦 Baixa em Encomenda":
        from services.supabase_service import buscar_encomendas_pendentes
        pendentes = buscar_encomendas_pendentes(funcionario['id'])
        if not pendentes:
            await update.message.reply_text("✅ Seu quiosque não tem nenhuma encomenda pendente de retirada no momento.")
            return
            
        msg = "📦 *Encomendas Pendentes para Retirada:*\nSelecione uma clicando no botão abaixo.\n\n"
        keyboard = []
        for enc in pendentes:
            cliente = enc.get('clientes', {})
            nome_cliente = cliente.get('nome', 'Cliente')
            codigo = enc['codigo_retirada']
            valor = enc['valor_original']
            msg += f"🔹 *{nome_cliente}* - Código: `{codigo}` - Valor: R$ {valor}\n"
            keyboard.append([InlineKeyboardButton(f"Dar Baixa: {codigo} ({nome_cliente})", callback_data=f"iniciar_baixa_{enc['id']}_{valor}")])
            
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=reply_markup)
        return

    elif text == "🏷️ Cadastrar Produto":
        user_states[telegram_id] = "esperando_foto_produto"
        await update.message.reply_text("📸 *Cadastro Rápido:*\nPor favor, envie uma foto do produto onde o **Código de Barras (EAN)** esteja bem legível.", parse_mode="Markdown")
        return

    elif text == "🔍 Consultar Estoque":
        user_states[telegram_id] = "esperando_busca_estoque"
        await update.message.reply_text("🔍 *Busca de Estoque:*\nDigite o nome do produto ou envie uma foto do código de barras.", parse_mode="Markdown")
        return
        
    # --- Menu Compartilhado: Escolher Persona ---
    if text == "🎭 Escolher Persona":
        keyboard = [
            [InlineKeyboardButton("🕸️ H-Aranha", callback_data="persona_set_Homem-Aranha"), InlineKeyboardButton("⚔️ Deadpool", callback_data="persona_set_Deadpool")],
            [InlineKeyboardButton("🦇 Batman", callback_data="persona_set_Batman"), InlineKeyboardButton("🎩 Alfred", callback_data="persona_set_Alfred")],
            [InlineKeyboardButton("🤖 C-3PO", callback_data="persona_set_C3PO"), InlineKeyboardButton("🌑 Darth Vader", callback_data="persona_set_Darth Vader")],
            [InlineKeyboardButton("💥 Vegeta", callback_data="persona_set_Vegeta"), InlineKeyboardButton("🍜 Naruto", callback_data="persona_set_Naruto")],
            [InlineKeyboardButton("🪄 Hermione", callback_data="persona_set_Hermione"), InlineKeyboardButton("🐶 Piticão", callback_data="persona_set_Piticão")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        persona_atual = funcionario.get('persona', 'Padrão')
        await update.message.reply_text(f"Atualmente você está usando a persona: *{persona_atual}*\n\nEscolha uma nova persona para me controlar:", reply_markup=reply_markup, parse_mode="Markdown")
        return

    # --- Menu Exclusivo ADM: Ranking de Personas ---
    if text == "📊 Ranking Personas":
        if funcionario['nivel_acesso'] < 4:
            await update.message.reply_text("⛔ Acesso Negado.")
            return
            
        from services.supabase_service import get_ranking_personas
        ranking = get_ranking_personas()
        
        if not ranking:
            await update.message.reply_text("📉 Ainda não há dados de ranking das personas.")
            return
            
        texto_ranking = "🏆 *Ranking de Uso das Personas* 🏆\n\n"
        for i, p in enumerate(ranking, 1):
            texto_ranking += f"{i}º - *{p['persona_nome']}* ({p['vezes_selecionada']} escolhas)\n"
            
        texto_ranking += "\n_Este ranking ajuda a identificar quais personas remover no futuro._"
        await update.message.reply_text(texto_ranking, parse_mode="Markdown")
        return

    # --- Menu Nível 2 (Marketing) ---
    if text == "🏷️ Cadastrar Produto":
        await update.message.reply_text("Ok! Tire uma foto do produto onde o **código de barras (EAN)** fique bem legível e me envie.", parse_mode="Markdown")
        return
    elif text == "🔍 Consultar Estoque":
        await update.message.reply_text("Digite o nome do produto ou o código de barras para consulta rápida:")
        return

    # --- Menu Nível 2 (Marketing) ---
    elif text == "🗺️ Postar no Maps":
        await update.message.reply_text("Esta funcionalidade conectará à API do Google Meu Negócio em breve. Por enquanto, a integração está pendente.")
        return
    elif text == "💬 Disparo Comunidades":
        await update.message.reply_text("O disparo via WhatsApp WebSocket será implementado na Fase 3 do projeto!")
        return

    # --- Menu Nível 3 (Chefia) ---
    elif text == "📊 Dashboards de Resultados":
        await update.message.reply_text("Aqui geraremos links de acesso rápido aos Dashboards executivos do seu Lovable.")
        return
    elif text == "🔐 Aprovações Pendentes":
        await update.message.reply_text("Nenhuma requisição de cancelamento ou desconto pendente no balcão no momento.")
        return

    # --- Menu Nível 4 (Administrador) ---
    # Ações Restritas para arquitetura Medalhão
    acoes_restritas = ["🎟️ Gerar Código", "🚫 Revogar Acesso", "⏸️ Suspender/Ativar", "📢 Transmissão Global", "👥 Listar Usuários"]
    if text in acoes_restritas:
        if funcionario.get('medalhao') == 'Silver':
            from services.supabase_service import verificar_autorizacao_valida
            if not verificar_autorizacao_valida(funcionario['id'], text):
                keyboard = [[InlineKeyboardButton("✅ Solicitar Autorização Gold", callback_data=f"solicitar_auth_{text}")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(f"⛔ *Acesso Restrito!*\nVocê possui a patente *Silver* e precisa de autorização para usar o comando `{text}`.", parse_mode="Markdown", reply_markup=reply_markup)
                return
    
    if text == "🎟️ Gerar Código":
        keyboard = [
            [InlineKeyboardButton("1️⃣ Quiosque (Vendedor)", callback_data="gerar_1")],
            [InlineKeyboardButton("2️⃣ Marketing", callback_data="gerar_2")],
            [InlineKeyboardButton("3️⃣ Boss", callback_data="gerar_3")],
            [InlineKeyboardButton("4️⃣ Administrador (ADM)", callback_data="gerar_4")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Para qual tipo de usuário você deseja gerar o código de acesso?", reply_markup=reply_markup)
        return
        
    elif text == "👥 Listar Usuários":
        if funcionario['nivel_acesso'] < 4: return
        from services.supabase_service import get_todos_funcionarios
        todos = get_todos_funcionarios()
        msg = "👥 *Usuários Ativos no Sistema:*\n\n"
        for f in todos:
            status_txt = "✅ Ativo" if f.get("ativo", True) else "⏸️ Suspenso"
            msg += f"👤 *{f['nome']}* ({status_txt})\n├ ID: `{f['id']}`\n├ Cargo: {f['cargo']}\n└ Nível: {f['nivel_acesso']}\n\n"
        await update.message.reply_text(msg, parse_mode="Markdown")
        return
        
    elif text == "📢 Transmissão Global":
        if funcionario['nivel_acesso'] < 4: return
        user_states[telegram_id] = "esperando_mensagem_broadcast"
        await update.message.reply_text("Digite a mensagem que você quer transmitir para TODOS os celulares do sistema.\n\n(Ou digite `Cancelar` para desistir).", parse_mode="Markdown")
        return
        
    elif text == "🚫 Revogar Acesso":
        if funcionario['nivel_acesso'] < 4: return
        user_states[telegram_id] = "esperando_id_revogar"
        await update.message.reply_text("Digite o *ID* do usuário que você deseja remover PERMANENTEMENTE do sistema.\n\n(Ou digite `Cancelar` para desistir).", parse_mode="Markdown")
        return
        
    elif text == "⏸️ Suspender/Ativar":
        if funcionario['nivel_acesso'] < 4: return
        user_states[telegram_id] = "esperando_id_suspender"
        await update.message.reply_text("Digite o *ID* do usuário seguido da letra *A* (Ativar) ou *D* (Desativar).\n\nExemplo: `14 D` (para suspender o acesso do usuário 14)\n\n(Ou digite `Cancelar` para desistir).", parse_mode="Markdown")
        return
        
    elif text == "📊 Resumo do Sistema":
        from services.supabase_service import get_todos_funcionarios
        todos = get_todos_funcionarios()
        await update.message.reply_text(f"📊 *Status Atual do Piticão:*\n\n- Bot Operacional: Sim\n- Usuários Logados: {len(todos)}\n- Integração Gemini 1.5: Online\n\n(Dashboards Lovable em breve)", parse_mode="Markdown")
        return

    # Eco padrão para outras mensagens soltas de usuários registrados
    if text:
        from services.gemini_service import chat_com_persona
        persona_atual = funcionario.get('persona', 'Padrão')
        # Avisa que está digitando
        await context.bot.send_chat_action(chat_id=telegram_id, action='typing')
        resposta = chat_com_persona(text, persona_atual)
        await update.message.reply_text(resposta)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lida com os cliques nos botões Inline (submenus)."""
    query = update.callback_query
    await query.answer() # Fecha o círculo de carregamento no botão do Telegram
    
    user = update.effective_user
    telegram_id = str(user.id)
    funcionario = get_funcionario_by_telegram_id(telegram_id)
    
    # Segurança: Apenas chefia/adm (>=3) pode gerar códigos, apesar do botão só aparecer pra eles
    if not funcionario or funcionario['nivel_acesso'] < 3:
        await query.edit_message_text(text="⛔ Permissão negada.")
        return
        
    data = query.data
    
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

    elif data.startswith("iniciar_baixa_"):
        # iniciar_baixa_ENCOMENDAID_VALOR
        partes = data.split("_")
        encomenda_id = partes[2]
        valor_original = partes[3]
        
        user_states[telegram_id] = f"esperando_valor_final_{encomenda_id}"
        await query.edit_message_text(f"Você está dando baixa na encomenda.\n\nO valor previsto era de **R$ {valor_original}**.\n\nPor favor, digite o valor FINAL exato que foi pago no sistema da loja para concluirmos a transação. (Ex: 159.90)\n\n(Ou digite `Cancelar`)", parse_mode="Markdown")

    elif data.startswith("medalhao_"):
        partes = data.split("_")
        nivel = int(partes[1])
        medalhao = partes[2]
        user_states[telegram_id] = f"esperando_nome_codigo_{nivel}_{medalhao}"
        await query.edit_message_text(f"Patente selecionada: *{medalhao}*\n\nPor favor, digite o **nome** que será atribuído a este usuário (Ex: `Bruno`).\nO sufixo `({medalhao} Access)` será adicionado automaticamente.\n\n(Ou digite `Cancelar`)", parse_mode="Markdown")

    elif data.startswith("solicitar_auth_"):
        acao_id = data.replace("solicitar_auth_", "")
        from services.supabase_service import criar_solicitacao_autorizacao, get_usuarios_gold
        
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
        from datetime import datetime
        partes = data.split("_", 2)
        tipo = partes[1]
        auth_id = partes[2]
        
        from services.supabase_service import get_autorizacao_por_id, atualizar_autorizacao
        auth_req = get_autorizacao_por_id(auth_id)
        if not auth_req:
            await query.edit_message_text("❌ Solicitação não encontrada.")
            return
            
        if auth_req['status'] != 'PENDENTE':
            await query.edit_message_text(f"⚠️ Esta solicitação já foi tratada. (Status: {auth_req['status']})")
            return
            
        status = "PENDENTE"
        expira = None
        if tipo == "unica":
            status = "AUTORIZADO_UNICA"
        elif tipo == "dia":
            status = "AUTORIZADO_DIA"
            expira = datetime.now().replace(hour=23, minute=59, second=59).isoformat()
        elif tipo == "livre":
            status = "AUTORIZADO_LIVRE"
        elif tipo == "negar":
            status = "NEGADO"
            
        atualizar_autorizacao(auth_id, status, funcionario['id'], expira)
        await query.edit_message_text(f"✅ Solicitação processada com status: `{status}`", parse_mode="Markdown")
        
        try:
            if status == "NEGADO":
                await context.bot.send_message(chat_id=auth_req['solicitante']['telegram_id'], text=f"❌ Sua solicitação para `{auth_req['acao_alvo']}` foi *NEGADA* por {funcionario['nome']}.", parse_mode="Markdown")
            else:
                await context.bot.send_message(chat_id=auth_req['solicitante']['telegram_id'], text=f"✅ Sua solicitação para `{auth_req['acao_alvo']}` foi *APROVADA* ({status}). Você já pode executar o comando novamente no painel.", parse_mode="Markdown")
        except: pass

    elif data.startswith("persona_set_"):
        nova_persona = data.replace("persona_set_", "")
        from services.supabase_service import atualizar_persona, incrementar_uso_persona
        
        atualizado = atualizar_persona(funcionario['id'], nova_persona)
        
        if atualizado:
            # Incrementa o banco de dados do ranking
            incrementar_uso_persona(nova_persona)
            apresentacoes = {
                "Homem-Aranha": "🕸️🕷️ **Homem-Aranha assumindo o controle!** Com grandes poderes vêm grandes responsabilidades corporativas. O que vamos acessar no menu do sistema hoje, parceiro?",
                "Deadpool": "⚔️🌮 **Deadpool na área!** Sério que me colocaram num chat corporativo? Tá bom, vamos fingir que eu trabalho aqui. Qual botão do menu a gente vai apertar hoje?",
                "Batman": "🦇🌑 **...** Eu sou a noite. O sistema está seguro e eu estou monitorando tudo. O que você quer investigar no menu?",
                "Alfred": "🎩☕ **Aos seus serviços.** O sistema corporativo está polido e pronto para uso. O que deseja visualizar no menu neste momento?",
                "C3PO": "🤖✨ **Saudações, eu sou C-3PO!** Especialista em relações cibernético-humanas e... sistemas de estoque! Em qual menu corporativo posso auxiliá-lo de forma eficiente hoje?",
                "Darth Vader": "🌑⚔️ **O Lado Sombrio está no controle.** Não me decepcione com erros. Escolha a funcionalidade do menu imediatamente.",
                "Vegeta": "💥😠 **Príncipe Vegeta chegou!** Não me faça perder tempo com tolices. O trabalho é a prioridade! Qual funcionalidade do menu você precisa usar agora?",
                "Naruto": "🍜🦊 **Tô certo! Naruto Uzumaki chegou!** Eu nunca desisto de um chamado no sistema! O que nós vamos acessar no menu hoje?",
                "Hermione": "🪄📚 **Olá, preste atenção!** É Leviosa, não Leviosá. Mantenha o sistema organizado. O que você precisa acessar no nosso menu principal hoje?",
                "Padrão": "🐶👕 **Piticão na área!** Au au! Estou pronto para ajudar a Master Geek. Qual botão do menu vamos acessar hoje?"
            }
            mensagem_persona = apresentacoes.get(nova_persona, "🐶👕 **Piticão na área!** Au au! Estou pronto para ajudar a Master Geek. Qual botão do menu vamos acessar hoje?")
            
            await query.edit_message_text(f"✅ Persona alterada para: *{nova_persona}*", parse_mode="Markdown")
            try:
                await context.bot.send_message(chat_id=telegram_id, text=mensagem_persona, parse_mode="Markdown")
            except Exception as e:
                print("Erro ao enviar mensagem de persona:", e)
        else:
            await query.edit_message_text("❌ Falha ao atualizar a persona.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa as fotos enviadas pelos usuários (ex: Código de Barras)."""
    if not update.message or not update.message.photo:
        return
        
    telegram_id = str(update.message.from_user.id)
    from services.supabase_service import get_funcionario_by_telegram_id
    funcionario = get_funcionario_by_telegram_id(telegram_id)
    
    if not funcionario:
        return
        
    estado_atual = user_states.get(telegram_id)
    
    if estado_atual in ["esperando_foto_produto", "esperando_busca_estoque"]:
        await context.bot.send_chat_action(chat_id=telegram_id, action='typing')
        await update.message.reply_text("🔎 Analisando o código de barras com IA...")
        
        # Pega a foto em melhor resolução
        photo_file = await update.message.photo[-1].get_file()
        
        import tempfile
        import os
        from services.gemini_service import analisar_imagem_gemini
        from services.supabase_service import buscar_produto_por_ean
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            caminho_temporario = tmp.name
            
        try:
            await photo_file.download_to_drive(custom_path=caminho_temporario)
            resultado_ia = analisar_imagem_gemini(caminho_temporario)
            
            # O Gemini deve retornar apenas números se achar o EAN
            ean_encontrado = ''.join(filter(str.isdigit, resultado_ia))
            
            if not ean_encontrado or len(ean_encontrado) < 5:
                await update.message.reply_text("❌ Não consegui ler nenhum código de barras claro na imagem. Tente tirar a foto mais de perto e sem reflexo.")
                return
                
            if estado_atual == "esperando_foto_produto":
                # Verifica se o produto já existe
                produto_existente = buscar_produto_por_ean(ean_encontrado)
                if produto_existente:
                    from services.supabase_service import adicionar_estoque
                    adicionar_estoque(produto_existente['id'], funcionario['id'], 1)
                    await update.message.reply_text(f"📦 O produto *{produto_existente['nome']}* (EAN: {ean_encontrado}) já existe no catálogo.\n✅ Adicionado +1 no estoque do seu quiosque!", parse_mode="Markdown")
                    user_states.pop(telegram_id, None)
                else:
                    user_states[telegram_id] = f"esperando_nome_produto_{ean_encontrado}"
                    await update.message.reply_text(f"📝 EAN lido: `{ean_encontrado}`\n\nEste produto é novo! Qual é o **nome** dele? (Ex: Funko Pop Batman)", parse_mode="Markdown")
                    
            elif estado_atual == "esperando_busca_estoque":
                produto_existente = buscar_produto_por_ean(ean_encontrado)
                if produto_existente:
                    from services.supabase_service import supabase
                    response = supabase.table("estoque").select("*").eq("produto_id", produto_existente['id']).eq("quiosque_id", funcionario['id']).execute()
                    qtd = response.data[0]['quantidade'] if response.data else 0
                    await update.message.reply_text(f"🔍 **Resultado da Busca:**\n\nProduto: *{produto_existente['nome']}*\nEAN: `{ean_encontrado}`\n\n📦 Seu Estoque: **{qtd} unidades**.", parse_mode="Markdown")
                else:
                    await update.message.reply_text(f"❌ Produto (EAN: {ean_encontrado}) não foi encontrado no catálogo da Master Geek.")
                user_states.pop(telegram_id, None)
                
        finally:
            if os.path.exists(caminho_temporario):
                os.remove(caminho_temporario)
