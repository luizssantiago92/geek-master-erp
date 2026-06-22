from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
import asyncio
from services.supabase_service import supabase, buscar_encomendas_pendentes, salvar_produto
from bot.state import user_states, pending_notifications
from bot.handlers.core import get_menu_por_nivel

async def processar_salvamento_assincrono(nome, franquia, numero, chat_id, context, nivel_efetivo, is_testing):
    from services.scraping_service import scrape_funko_product
    # Passando nome e franquia juntos para evitar que o Bing se confunda com homônimos (ex: cachorro/cavalo)
    query_busca = f"{nome} {franquia}"
    resultado_scraping = scrape_funko_product(query_busca)
    
    if not resultado_scraping:
        await context.bot.send_message(chat_id=chat_id, text=f"⚠️ [Background] Não encontrei o produto na internet: {query_busca}.")
        return

    resultado_scraping["nome"] = f"BONECO FUNKO POP! {str(franquia).upper()} - {str(nome).upper()} #{str(numero)}"
    resultado_scraping["franquia"] = str(franquia)

    produto_db = {
        "nome": resultado_scraping["nome"],
        "franquia": str(franquia),
        "preco_base": resultado_scraping["preco_base"],
        "imagem_url": resultado_scraping.get("imagem_url"),
        "status_scraping": "CONCLUIDO",
        "descricao": resultado_scraping.get("descricao"),
        "is_new": resultado_scraping.get("is_new", False),
        "imagens_galeria": resultado_scraping.get("imagens_galeria", []),
        "status_publicacao": "PENDENTE"
    }
    
    salvo = salvar_produto(produto_db)
    if salvo:
        nome_curto = resultado_scraping['nome']
        
        if chat_id not in pending_notifications:
            pending_notifications[chat_id] = {"count": 0, "names": [], "task": None}
            
        pending_notifications[chat_id]["count"] += 1
        pending_notifications[chat_id]["names"].append(nome_curto)
        
        if pending_notifications[chat_id]["task"]:
            pending_notifications[chat_id]["task"].cancel()
            
        pending_notifications[chat_id]["task"] = asyncio.create_task(enviar_resumo_debounced(chat_id, context))
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"❌ Erro ao salvar no banco de dados: {resultado_scraping['nome']}")

async def enviar_resumo_debounced(chat_id, context):
    try:
        await asyncio.sleep(10)
    except asyncio.CancelledError:
        return
        
    data = pending_notifications.get(chat_id)
    if not data or data["count"] == 0:
        return
        
    count = data["count"]
    names = data["names"]
    
    if count <= 3:
        for name in names:
            await context.bot.send_message(chat_id=chat_id, text=f"✅ Produto cadastrado com sucesso: *{name}*", parse_mode="Markdown")
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"✅ *Todos os {count} produtos foram cadastrados com sucesso!*", parse_mode="Markdown")
        
    pending_notifications[chat_id] = {"count": 0, "names": [], "task": None}

async def handle_quiosque_messages(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, telegram_id: str, funcionario: dict, nivel_efetivo: int, is_testing: bool) -> bool:
    """Retorna True se a mensagem foi tratada aqui."""
    estado_atual = user_states.get(telegram_id)
    
    if text == "📦 Estoque":
        user_states[telegram_id] = "esperando_foto_entrada"
        await update.message.reply_text("📦 **ESTOQUE (Entrada/Cadastro)**\n\nEnvie a foto do produto + código de barras. Se o produto for novo, ele será cadastrado automaticamente. Se já existir, apenas daremos entrada (+1).", parse_mode="Markdown")
        return True
        
    if text == "🛒 Venda":
        user_states[telegram_id] = "esperando_foto_venda"
        await update.message.reply_text("🛒 **REGISTRAR VENDA (-1)**\n\nEnvie a **foto do código de barras** (ou do produto) que acabou de ser vendido.", parse_mode="Markdown")
        return True
        
    if text == "📋 Reposição":
        resp = supabase.table("estoque").select("quantidade, produtos(nome, ean)").eq("quiosque_id", funcionario['id']).lte("quantidade", 0).execute()
        if not resp.data:
            await update.message.reply_text("✅ O seu quiosque não tem nenhum item esgotado no momento!")
            return True
            
        texto = "🚨 **LISTA DE REPOSIÇÃO** 🚨\n\nOs seguintes itens estão esgotados no seu quiosque:\n\n"
        for item in resp.data:
            prod = item.get("produtos", {})
            nome = prod.get("nome", "Produto Desconhecido")
            ean = prod.get("ean", "Sem código")
            texto += f"• {nome} (EAN: {ean})\n"
            
        import urllib.parse
        msg_zap = urllib.parse.quote(texto.replace("**", "*"))
        link_zap = f"https://api.whatsapp.com/send?text={msg_zap}"
        
        keyboard = [[InlineKeyboardButton("📲 Enviar para Gerente 1", url=link_zap)]]
        await update.message.reply_text(texto, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        return True
        
    if text == "📦 Encomendas":
        encomendas = buscar_encomendas_pendentes(funcionario['id'])
        if not encomendas:
            await update.message.reply_text("✅ *Tudo limpo!*\nVocê não tem nenhuma encomenda aguardando ação neste momento.", parse_mode="Markdown")
            return True
        texto = f"📦 Você tem **{len(encomendas)}** encomendas aguardando ação:\n\nSelecione um pedido abaixo para gerenciar:"
        keyboard = []
        for enc in encomendas:
            status_emoji = "⏳" if enc['status'] == "PENDENTE" else "🛍️"
            nome_botao = f"{status_emoji} #{enc['codigo_pedido']} - {enc['cliente_nome']}"
            keyboard.append([InlineKeyboardButton(nome_botao, callback_data=f"enc_detalhe_{enc['id']}")])
        await update.message.reply_text(texto, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        return True

    # Fluxo Cadastro Inteligente / Funko
    if text.strip().lower() == "funko" and estado_atual == "teste_novo_scraping_tipo":
        user_states[telegram_id] = "teste_funko_nome|||null|||null|||null"
        await update.message.reply_text("Me envie uma foto da caixa do Funko!\n\nOu, se preferir, digite de uma vez o *NOME* do personagem, a *FRANQUIA* e o *NÚMERO* da caixa:", parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
        return True

    if text.strip().lower() == "funko" and estado_atual != "teste_novo_scraping_tipo" and not (estado_atual and estado_atual.startswith("teste_")):
        await update.message.reply_text("Para cadastrar um Funko, por favor use o botão oficial 'Funko' no menu de Cadastrar Produto.")
        return True

    if estado_atual and estado_atual.startswith("teste_funko_nome"):
        partes = estado_atual.split("|||")
        nome_salvo = partes[1] if len(partes) > 1 and partes[1] != "null" else None
        franquia_salva = partes[2] if len(partes) > 2 and partes[2] != "null" else None
        numero_salvo = partes[3] if len(partes) > 3 and partes[3] != "null" else None

        msg_espera = await update.message.reply_text("Processando sua resposta...", parse_mode="Markdown")
        from services.gemini_service import extrair_dados_funko_texto
        resultado_json = extrair_dados_funko_texto(text)
        
        try:
            import json
            limpo = resultado_json.replace("```json", "").replace("```", "").strip()
            dados = json.loads(limpo)
            
            nome = dados.get("nome") or nome_salvo
            franquia = dados.get("franquia") or franquia_salva
            numero = dados.get("numero") or numero_salvo
            
            faltando = []
            if not nome: faltando.append("*NOME* do personagem")
            if not franquia: faltando.append("*FRANQUIA*")
            if not numero: faltando.append("*NÚMERO* da caixa")
            
            if faltando:
                lista_faltando = ", ".join(faltando)
                user_states[telegram_id] = f"teste_funko_nome|||{nome or 'null'}|||{franquia or 'null'}|||{numero or 'null'}"
                await msg_espera.edit_text(f"Entendi algumas coisas, mas ainda falta: {lista_faltando}.\n\nPode me informar o que falta?", parse_mode="Markdown")
                return True
                
            nome_encontrado = f"BONECO FUNKO POP! {str(franquia).upper()} - {str(nome).upper()} #{str(numero)}"
            user_states[telegram_id] = f"teste_funko_confirma|||{nome}|||{franquia}|||{numero}"
            keyboard = ReplyKeyboardMarkup([["✅ Sim", "❌ Não"]], resize_keyboard=True)
            await msg_espera.delete()
            await update.message.reply_text(f"🔎 Encontrei o seguinte produto baseado nas suas informações:\n*{nome_encontrado}*\n\nÉ esse mesmo que você quer cadastrar?", parse_mode="Markdown", reply_markup=keyboard)
            return True
        except Exception:
            await msg_espera.edit_text("❌ Erro ao entender a resposta. Pode digitar de novo?")
            return True

    if estado_atual and estado_atual.startswith("teste_funko_confirma"):
        keyboard = ReplyKeyboardMarkup([
            ["Funko", "Caneca e Copo"],
            ["Action Figure", "Vestuário", "Acessório"],
            ["🔙 Voltar ao Menu"]
        ], resize_keyboard=True)
        
        if text == "❌ Não":
            user_states[telegram_id] = "teste_novo_scraping_tipo"
            await update.message.reply_text("Cadastro cancelado. Qual produto deseja registrar agora?", reply_markup=keyboard)
            return True
            
        partes = estado_atual.split("|||")
        nome = partes[1]
        franquia = partes[2]
        numero = partes[3]

        user_states[telegram_id] = "teste_novo_scraping_tipo"
        await update.message.reply_text("⏳ Carregando informações...\n\nQual é o próximo produto a ser cadastrado?", reply_markup=keyboard, parse_mode="Markdown")
        asyncio.create_task(processar_salvamento_assincrono(nome, franquia, numero, update.effective_chat.id, context, nivel_efetivo, is_testing))
        return True

    # Pular Produto Novo
    if estado_atual and estado_atual.startswith("esperando_codigo_produto_novo") and text.lower().strip() == "pular":
        partes = estado_atual.split("|||")
        nome_salvo = partes[1]
        marca_salvo = partes[2]
        foto_salva = partes[3]
        produto_db = {
            "nome": nome_salvo,
            "marca": marca_salvo,
            "ean": None,
            "foto_original_url": foto_salva,
            "foto_profissional_url": None,
            "status_scraping": "NAO_NECESSARIO"
        }
        if salvar_produto(produto_db):
            await update.message.reply_text("✅ Produto cadastrado no Catálogo Geral (sem código de barras).")
            user_states.pop(telegram_id, None)
        else:
            await update.message.reply_text("❌ Erro ao salvar no banco.")
        return True

    return False
