from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
import os
import json
import tempfile
from bot.state import user_states
from services.supabase_service import get_funcionario_by_telegram_id, salvar_produto, buscar_produto_por_ean, supabase, upload_image_to_storage, adicionar_produto_teste
from services.gemini_service import analisar_imagem_gemini, analisar_caixa_funko, ler_qr_code_gemini
from services.supabase_service import validar_e_usar_codigo

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lida com o recebimento de imagens (produtos, códigos de barras, etc)."""
    if not update.message.photo:
        return
        
    telegram_id = str(update.message.from_user.id)
    telegram_name = update.message.from_user.first_name
    funcionario = get_funcionario_by_telegram_id(telegram_id)
    
    if not funcionario:
        # Usuário não cadastrado tentou enviar uma foto. Pode ser um QR Code de acesso!
        msg_auth = await update.message.reply_text("🔎 Analisando imagem em busca de Código de Acesso...")
        foto_file = await update.message.photo[-1].get_file()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            await foto_file.download_to_drive(tmp_file.name)
            caminho = tmp_file.name
            
        texto_qr = ler_qr_code_gemini(caminho)
        os.remove(caminho)
        
        if "PTC-" in texto_qr:
            # Extrair apenas a parte que importa (ex: PTC-1234A)
            import re
            match = re.search(r'(PTC-\d+[A-Z])', texto_qr)
            if match:
                codigo = match.group(1)
                sucesso, resposta = validar_e_usar_codigo(telegram_id, telegram_name, codigo)
                if sucesso:
                    await msg_auth.edit_text(f"🎉 **Autenticação Concluída com Sucesso!**\n\nBem-vindo(a), {resposta['nome']}!\nCargo: {resposta['cargo']}", parse_mode="Markdown")
                    # Enviar menu inicial
                    from bot.handlers.core import cmd_start
                    await cmd_start(update, context)
                else:
                    await msg_auth.edit_text(resposta)
            else:
                await msg_auth.edit_text("❌ Nenhum código válido encontrado na imagem.")
        else:
            await msg_auth.edit_text("❌ Não reconheci você. Peça um código de acesso (QR Code) ao seu gerente.")
        return
        
    estado_atual = user_states.get(telegram_id)
    if not estado_atual:
        await update.message.reply_text("Por favor, selecione uma opção no menu primeiro (ex: Estoque, Venda).")
        return

    foto_file = await update.message.photo[-1].get_file()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        await foto_file.download_to_drive(tmp_file.name)
        caminho = tmp_file.name
        
    texto_espera = "Processando imagem..."
    if estado_atual == "esperando_foto_entrada":
        texto_espera = "Carregando... ⏳\nEnquanto o carregamento é feito nos bastidores, um novo lote de até 10 itens pode ser enviado para a fila de espera!"
        
    msg_espera = await update.message.reply_text(texto_espera)
        
    # --- ROTEAMENTO INTELIGENTE DE FOTO PARA FUNKO ---
    if estado_atual == "teste_novo_scraping_tipo":
        estado_atual = "teste_funko_nome|||null|||null|||null"
        user_states[telegram_id] = estado_atual

    # --- FLUXO DE LEITURA DE CAIXA DE FUNKO ---
    if estado_atual and estado_atual.startswith("teste_funko_nome"):
        partes = estado_atual.split("|||")
        nome_salvo = partes[1] if len(partes) > 1 and partes[1] != "null" else None
        franquia_salva = partes[2] if len(partes) > 2 and partes[2] != "null" else None
        numero_salvo = partes[3] if len(partes) > 3 and partes[3] != "null" else None

        resultado_json = analisar_caixa_funko(caminho)
        try: os.remove(caminho)
        except: pass
            
        try:
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
                await msg_espera.edit_text(f"Li a imagem, mas faltou identificar: {lista_faltando}.\n\nPode digitar o que falta?", parse_mode="Markdown")
                return
                
            nome_encontrado = f"BONECO FUNKO POP! {str(franquia).upper()} - {str(nome).upper()} #{str(numero)}"
            user_states[telegram_id] = f"teste_funko_confirma|||{nome}|||{franquia}|||{numero}"
            keyboard = ReplyKeyboardMarkup([["✅ Sim", "❌ Não"]], resize_keyboard=True)
            await msg_espera.delete()
            await update.message.reply_text(f"🔎 Li a imagem e encontrei o seguinte produto:\n*{nome_encontrado}*\n\nÉ esse mesmo que você quer cadastrar?", parse_mode="Markdown", reply_markup=keyboard)
            return
            
        except Exception:
            await msg_espera.edit_text("❌ Erro ao processar a resposta da IA. Por favor, digite as informações do funko manualmente:")
            return

    # --- FLUXO DE ADICIONAR PRODUTO TESTE VIA FOTO ---
    if estado_atual and estado_atual.startswith("teste_add_foto"):
        partes = estado_atual.split("|||")
        nome = partes[1]
        franquia = partes[2]
        preco = float(partes[3])
        
        with open(caminho, "rb") as f:
            bytes_img = f.read()
            
        url_publica = upload_image_to_storage(bytes_img, caminho)
        
        try: os.remove(caminho)
        except: pass
            
        prod = adicionar_produto_teste(nome, franquia, preco, url_publica)
        user_states.pop(telegram_id, None)
        
        if prod:
            await msg_espera.edit_text(f"✅ *Produto Teste Adicionado com Imagem!*\nNome: {prod['nome']}\nID: `{prod['id']}`", parse_mode="Markdown")
        else:
            await msg_espera.edit_text("❌ Erro ao salvar o produto no banco.")
        return

    # Processamento padrão de código de barras
    resultado_json = analisar_imagem_gemini(caminho)
    try: os.remove(caminho)
    except: pass
        
    try:
        limpo = resultado_json.replace("```json", "").replace("```", "").strip()
        dados = json.loads(limpo)
        
        nome = dados.get("nome")
        marca = dados.get("marca")
        ean = dados.get("ean")

        # --- FLUXO DE ENTRADA DE ESTOQUE (CADASTRO ÚNICO) ---
        if estado_atual == "esperando_foto_entrada":
            if not nome:
                await msg_espera.edit_text("❌ Imagem não lida (Não identifiquei o produto).")
                return
                
            produto_id = None
            if ean:
                existente = buscar_produto_por_ean(ean)
                if existente: produto_id = existente['id']
            
            if not produto_id:
                if not ean:
                    user_states[telegram_id] = f"esperando_codigo_entrada|||{nome}|||{marca or ''}|||{foto_file.file_id}"
                    await msg_espera.edit_text(f"✅ Produto *{nome}* identificado como NOVO!\n\n📸 **Agora envie a foto apenas do código de barras** da embalagem para finalizarmos o cadastro e dar entrada.", parse_mode="Markdown")
                    return
                else:
                    produto_db = {
                        "nome": nome,
                        "marca": marca,
                        "ean": ean,
                        "foto_original_url": foto_file.file_id,
                        "status_scraping": "NAO_NECESSARIO"
                    }
                    if salvar_produto(produto_db):
                        novo_prod = buscar_produto_por_ean(ean)
                        produto_id = novo_prod['id']
                    else:
                        await msg_espera.edit_text("❌ Erro ao salvar novo produto.")
                        return
                        
            resp_est = supabase.table("estoque").select("*").eq("produto_id", produto_id).eq("quiosque_id", funcionario['id']).execute()
            if resp_est.data:
                nova_qtd = resp_est.data[0]['quantidade'] + 1
                supabase.table("estoque").update({"quantidade": nova_qtd}).eq("id", resp_est.data[0]['id']).execute()
            else:
                supabase.table("estoque").insert({"produto_id": produto_id, "quiosque_id": funcionario['id'], "quantidade": 1}).execute()
                
            await msg_espera.edit_text("✅ Produto registrado no Catálogo (se novo) e Entrada de Estoque (+1) efetuada!")
            # Não limpamos o state para permitir envios em lote: user_states.pop(telegram_id, None)
        # --- FLUXO DE 2ª FOTO DA ENTRADA DE ESTOQUE ---
        elif estado_atual.startswith("esperando_codigo_entrada"):
            partes = estado_atual.split("|||")
            nome_salvo = partes[1]
            marca_salvo = partes[2]
            foto_salva = partes[3]
            
            if not ean:
                await msg_espera.edit_text("❌ Não consegui ler nenhum código de barras nesta foto. Tente enviar de perto.")
                return
                
            existente = buscar_produto_por_ean(ean)
            if existente:
                produto_id = existente['id']
            else:
                produto_db = {
                    "nome": nome_salvo,
                    "marca": marca_salvo,
                    "ean": ean,
                    "foto_original_url": foto_salva,
                    "status_scraping": "NAO_NECESSARIO"
                }
                salvar_produto(produto_db)
                novo_prod = buscar_produto_por_ean(ean)
                produto_id = novo_prod['id']
                
            resp_est = supabase.table("estoque").select("*").eq("produto_id", produto_id).eq("quiosque_id", funcionario['id']).execute()
            if resp_est.data:
                nova_qtd = resp_est.data[0]['quantidade'] + 1
                supabase.table("estoque").update({"quantidade": nova_qtd}).eq("id", resp_est.data[0]['id']).execute()
            else:
                supabase.table("estoque").insert({"produto_id": produto_id, "quiosque_id": funcionario['id'], "quantidade": 1}).execute()
                
            await msg_espera.edit_text("✅ Produto cadastrado com sucesso e Entrada de Estoque (+1) efetuada!")
            user_states[telegram_id] = "esperando_foto_entrada" # Volta pro lote
        # --- FLUXO DE VENDA DE PRODUTO ---
        elif estado_atual == "esperando_foto_venda":
            if not ean and not nome:
                await msg_espera.edit_text("❌ Imagem não lida.")
                return
                
            produto_id = None
            if ean:
                existente = buscar_produto_por_ean(ean)
                if existente: produto_id = existente['id']
            if not produto_id and nome:
                resp = supabase.table("produtos").select("*").ilike("nome", f"%{nome}%").execute()
                if resp.data: produto_id = resp.data[0]['id']
                
            if not produto_id:
                if not ean:
                    await msg_espera.edit_text("❌ Produto não encontrado e sem EAN na foto. Tente a foto do código de barras de perto.")
                    return
                
                produto_db = {
                    "nome": nome or "Produto Desconhecido (Vendido s/ Cadastro)",
                    "marca": marca,
                    "ean": ean,
                    "foto_original_url": foto_file.file_id,
                    "status_scraping": "NAO_NECESSARIO"
                }
                salvar_produto(produto_db)
                novo_prod = buscar_produto_por_ean(ean)
                produto_id = novo_prod['id']
                
            supabase.table("vendas").insert({
                "produto_ean": ean,
                "quiosque_id": funcionario['id'],
                "quantidade": 1
            }).execute()
            
            resp_est = supabase.table("estoque").select("*").eq("produto_id", produto_id).eq("quiosque_id", funcionario['id']).execute()
            if resp_est.data:
                nova_qtd = resp_est.data[0]['quantidade'] - 1
                supabase.table("estoque").update({"quantidade": nova_qtd}).eq("id", resp_est.data[0]['id']).execute()
            else:
                supabase.table("estoque").insert({"produto_id": produto_id, "quiosque_id": funcionario['id'], "quantidade": -1}).execute()
                
            await msg_espera.edit_text("✅ Venda Registrada (-1). Baixa no estoque efetuada!")
            user_states.pop(telegram_id, None)

    except json.JSONDecodeError:
        await msg_espera.edit_text("❌ Imagem não lida.")
    except Exception as e:
        print(f"Error in handle_photo: {e}")
        await msg_espera.edit_text("❌ Ocorreu um erro interno.")
