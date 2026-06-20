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
from datetime import datetime

user_states = {}  # Dicionário simples para guardar estado das conversas do ADM
last_interaction = {} # Dicionário para guardar a última interação de cada usuário (Session Timeout)
impersonation_states = {} # Dicionário para Administradores testarem outros perfis: telegram_id -> nivel_efetivo
saved_test_profiles = {} # telegram_id -> set of levels

def obter_saudacao():
    hora = datetime.now().hour
    if 5 <= hora < 12:
        return "Bom dia"
    elif 12 <= hora < 18:
        return "Boa tarde"
    else:
        return "Boa noite"

APRESENTACOES = {
    "Homem-Aranha": "🕸️🕷️ **Homem-Aranha assumindo o controle!** Com grandes poderes vêm grandes responsabilidades corporativas. O que vamos acessar no menu do sistema hoje, parceiro?",
    "Deadpool": "⚔️🌮 **Deadpool na área!** Sério que me colocaram num chat corporativo? Tá bom, vamos fingir que eu trabalho aqui. Qual botão do menu a gente vai apertar hoje?",
    "Batman": "🦇🌑 **...** Eu sou a noite. O sistema está seguro e eu estou monitorando tudo. O que você quer investigar no menu?",
    "Alfred": "🎩☕ **Aos seus serviços.** O sistema corporativo está polido e pronto para uso. O que deseja visualizar no menu neste momento?",
    "C3PO": "🤖✨ **Saudações, eu sou C-3PO!** Especialista em relações cibernético-humanas e... sistemas de estoque! Em qual menu corporativo posso auxiliá-lo de forma eficiente hoje?",
    "Darth Vader": "🌑⚔️ **O Lado Sombrio está no controle.** Não me decepcione com erros. Escolha a funcionalidade do menu imediatamente.",
    "Vegeta": "💥😠 **Príncipe Vegeta chegou!** Não me faça perder tempo com tolices. O trabalho é a prioridade! Qual funcionalidade do menu você precisa usar agora?",
    "Naruto": "🍜🦊 **Tô certo! Naruto Uzumaki chegou!** Eu nunca desisto de um chamado no sistema! O que nós vamos acessar no menu hoje?",
    "Hermione": "🪄📚 **Olá, preste atenção!** É Leviosa, não Leviosá. Mantenha o sistema organizado. O que você precisa acessar no nosso menu principal hoje?",
    "Padrão": "🐶👕 **Piticão na área!** Au au! Estou pronto para ajudar a ERP Project. Qual botão do menu vamos acessar hoje?"
}

load_dotenv()
MASTER_ADMIN_CODE = os.getenv("MASTER_ADMIN_CODE")

# Mapeamento de níveis para texto
NIVEIS = {
    1: "Quiosque (Vendedor)",
    2: "Marketing",
    3: "Boss",
    4: "Administrador"
}

def get_menu_por_nivel(nivel: int, is_testing: bool = False) -> ReplyKeyboardMarkup:
    """Retorna o teclado interativo (ReplyKeyboardMarkup) apropriado para o nível de acesso."""
    if nivel == 1:
        keyboard = [
            ["📦 Estoque", "🛒 Venda"],
            ["📋 Reposição", "📦 Encomendas"],
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
            ["🛠️ Sistema", "🎭 Personas"],
            ["🧪 Modo Testador"]
        ]
    else:
        keyboard = [["/start"]]
        
    if is_testing:
        keyboard.append(["🔙 Sair do Teste"])
        
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
    if not funcionario:
        codigo = None
        # Se for texto, pode ser o deep link do QR Code ou código digitado manualmente
        if text:
            texto_limpo = text.strip()
            if texto_limpo.startswith("/start "):
                codigo = texto_limpo.replace("/start ", "").strip().upper()
            elif texto_limpo.startswith("/menu") or texto_limpo == "/start":
                await update.message.reply_text("👋 Olá! Eu sou o Piticão.\n\nPara acessar o sistema corporativo, você precisa de um **Código de Acesso** (Ex: PTC-XXXX). Peça ao seu gestor e envie o código aqui, ou aponte a câmera do celular para o QR Code gerado pelo administrador.")
                return
            else:
                codigo = texto_limpo.upper()
                
        # Se enviou foto (tentando enviar a imagem do QR Code em vez de usar a câmera do celular nativa)
        elif update.message.photo:
            await update.message.reply_text("📸 Analisando o QR Code enviado...")
            try:
                import cv2
                import tempfile
                photo_file = await update.message.photo[-1].get_file()
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_img:
                    caminho_temporario = temp_img.name
                await photo_file.download_to_drive(caminho_temporario)
                
                # Lê o QR Code usando OpenCV
                img = cv2.imread(caminho_temporario)
                detector = cv2.QRCodeDetector()
                data, bbox, _ = detector.detectAndDecode(img)
                os.remove(caminho_temporario)
                
                if data:
                    # Pode ser um link do tipo t.me/bot?start=PTC-XXXX
                    if "start=" in data:
                        codigo = data.split("start=")[-1].strip().upper()
                    else:
                        codigo = data.strip().upper()
                else:
                    await update.message.reply_text("❌ Não consegui ler nenhum QR Code nesta imagem.")
                    return
            except Exception as e:
                await update.message.reply_text(f"❌ Erro ao ler a imagem: {e}")
                return

        if codigo and (codigo.startswith("PTC-") or codigo.startswith("TST-")):
            from services.supabase_service import validar_e_usar_codigo
            if codigo.startswith("TST-"):
                # Código TST é só para simulação (se o cara já for admin), mas se ele não for nada, não deve usar TST, mas vamos validar se quiser
                pass 

            sucesso, msg_retorno = validar_e_usar_codigo(telegram_id, update.message.from_user.first_name, codigo)
            await update.message.reply_text(msg_retorno, parse_mode="Markdown")
            if sucesso:
                funcionario = get_funcionario_by_telegram_id(telegram_id)
                nome_exibicao = NIVEIS.get(funcionario['nivel_acesso'])
                await update.message.reply_text(f"Olá {funcionario['nome']}! Sou o Piticão 🐶.\\nSua área de trabalho ({nome_exibicao}) já está carregada no teclado abaixo.", reply_markup=get_menu_por_nivel(funcionario['nivel_acesso'], False), parse_mode="Markdown")
                return
            else:
                return
        else:
            # Se não é um código válido, ignora (stealth mode)
            return
        
    nivel_real = funcionario['nivel_acesso']
    nivel_efetivo = impersonation_states.get(telegram_id, nivel_real)
    is_testing = telegram_id in impersonation_states
        
    estado_atual = user_states.get(telegram_id)
    
    # Interceptadores do Modo Testador
    if estado_atual == "esperando_codigo_teste":
        codigo = text.strip().upper()
        if text.lower() == "cancelar":
            user_states.pop(telegram_id, None)
            await update.message.reply_text("Simulação cancelada.")
            return
            
        if not codigo.startswith("TST-"):
            await update.message.reply_text("❌ Código inválido. Para simular Onboarding, você deve usar um *Código de Testador* (que começa com TST-).\nDigite o código novamente ou envie Cancelar.", parse_mode="Markdown")
            return
            
        from services.supabase_service import validar_codigo_teste
        nivel_teste = validar_codigo_teste(codigo)
        
        if not nivel_teste:
             await update.message.reply_text("❌ Código de teste inválido, expirado ou já utilizado.")
             return
             
        user_states.pop(telegram_id, None)
        impersonation_states[telegram_id] = nivel_teste
        
        from services.supabase_service import adicionar_perfil_teste
        adicionar_perfil_teste(funcionario['id'], nivel_teste)
        
        nome_exibicao = NIVEIS.get(nivel_teste)
        
        await update.message.reply_text(f"*(SIMULAÇÃO DE CADASTRO)*\n✅ Código Verificado! Bem-vindo(a) à ERP Project.\nSeu perfil de **{nome_exibicao}** foi salvo nos seus atalhos de teste.", parse_mode="Markdown")
        await update.message.reply_text(f"Olá {funcionario['nome']}! Sou o Piticão 🐶.\nSua área de trabalho ({nome_exibicao}) já está carregada no teclado abaixo.\n*(Você está no Modo Testador)*", reply_markup=get_menu_por_nivel(nivel_teste, True), parse_mode="Markdown")
        return

    if text == "🔙 Sair do Teste" and is_testing:
        impersonation_states.pop(telegram_id, None)
        await update.message.reply_text("🧪 Teste encerrado. Bem-vindo de volta à conta de Administrador principal.", reply_markup=get_menu_por_nivel(nivel_real, False))
        return
        
    if text == "🔙 Voltar ao Menu":
        await update.message.reply_text(
            "Retornando ao menu principal.",
            reply_markup=get_menu_por_nivel(nivel_efetivo, is_testing)
        )
        return

    if text == "🛠️ Sistema" and nivel_efetivo == 4:
        keyboard = ReplyKeyboardMarkup([
            ["🎟️ Gerar Código", "👥 Listar Usuários"],
            ["📢 Transmissão Global", "⏸️ Suspender/Ativar"],
            ["🚫 Revogar Acesso", "📊 Resumo do Sistema"],
            ["🔙 Voltar ao Menu"]
        ], resize_keyboard=True)
        await update.message.reply_text("Você acessou o menu de **Sistema**.", reply_markup=keyboard, parse_mode='Markdown')
        return

    if text == "🎭 Personas" and nivel_efetivo == 4:
        keyboard = ReplyKeyboardMarkup([
            ["🎭 Escolher Persona", "📊 Ranking Personas"],
            ["🔙 Voltar ao Menu"]
        ], resize_keyboard=True)
        await update.message.reply_text("Você acessou o menu de **Personas**.", reply_markup=keyboard, parse_mode='Markdown')
        return

    if text == "🧪 Modo Testador" and nivel_efetivo == 4:
        keyboard = ReplyKeyboardMarkup([
            ["📦 Estoque Teste", "🧪 Testar Usuários"],
            ["🔙 Voltar ao Menu"]
        ], resize_keyboard=True)
        await update.message.reply_text("Você acessou o **Modo Testador**.", reply_markup=keyboard, parse_mode='Markdown')
        return
        
    if text == "🧪 Testar Usuários" and nivel_real == 4:
        keyboard = [
            [InlineKeyboardButton("🔑 Inserir TST- (Simular Novo Acesso)", callback_data="teste_onboarding")]
        ]
        
        perfis = funcionario.get('perfis_teste', [])
        for p in perfis:
            keyboard.append([InlineKeyboardButton(f"Perfil {NIVEIS.get(p)}", callback_data=f"teste_nivel_{p}")])
            
        await update.message.reply_text("🧪 **Testar Usuários - Perfis Criados**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return
    
    # ==============================================================
    # A PARTIR DAQUI, O USUÁRIO ESTÁ AUTENTICADO COMO FUNCIONÁRIO
    # ==============================================================
    
    if not funcionario.get("ativo", True):
        await update.message.reply_text("⛔ *Acesso Negado:*\nSeu acesso ao sistema Piticão está temporariamente suspenso. Procure a Administração.", parse_mode="Markdown")
        return
        
    # Interceptador do Saber Mais (Atualizações)
    if text.lower() in ["saber mais", "saber mais."]:
        try:
            with open("latest_release_notes.txt", "r", encoding="utf-8") as f:
                notas = f.read()
            await update.message.reply_text(f"📝 *Detalhes da Última Atualização:*\n\n{notas}", parse_mode="Markdown")
        except:
            pass
        return
        
    # Verifica reset de sessão (Virada de dia)
    agora = datetime.now()
    ultima_vez = last_interaction.get(telegram_id)
    
    # Se for a primeira interação ou se virou o dia (passou da meia-noite)
    if not ultima_vez or agora.date() > ultima_vez.date():
        persona_atual = funcionario.get('persona', 'Padrão')
        msg_apres = APRESENTACOES.get(persona_atual, APRESENTACOES["Padrão"])
        saudacao = obter_saudacao()
        texto_orientacao = f"*(Sessão Reiniciada)*\n\n{saudacao}!\n{msg_apres}\n\nVocê precisa de ajuda? Acesse o /menu abaixo e siga os caminhos para utilizar a ferramenta."
        try:
            await update.message.reply_text(texto_orientacao, parse_mode="Markdown")
        except: pass
        
    last_interaction[telegram_id] = agora
    
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

    # --- FLUXO ESTOQUE TESTE NOVO SCRAPING ---
    if estado_atual == "teste_novo_scraping_tipo":
        if text.lower() == "cancelar":
            user_states.pop(telegram_id, None)
            await update.message.reply_text("Cancelado.", reply_markup=get_menu_por_nivel(nivel_efetivo, is_testing))
            return
        
        user_states[telegram_id] = f"teste_novo_scraping_franquia|||{text}"
        await update.message.reply_text("Qual é a *FRANQUIA* do produto?\n(Ex: Marvel, Disney, Toy Story)", parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
        return

    if estado_atual and estado_atual.startswith("teste_novo_scraping_franquia"):
        if text.lower() == "cancelar":
            user_states.pop(telegram_id, None)
            await update.message.reply_text("Cancelado.", reply_markup=get_menu_por_nivel(nivel_efetivo, is_testing))
            return
            
        tipo = estado_atual.split("|||")[1]
        franquia = text.strip()
        user_states[telegram_id] = f"teste_novo_scraping_termo|||{tipo}|||{franquia}"
        
        if tipo.lower() == "funko":
            await update.message.reply_text("🔎 Qual é o *NOME* ou *NÚMERO* do Funko Pop?\n(Ex: Jessie, Luffy, Supergirl, Batman 274)", parse_mode="Markdown")
        else:
            await update.message.reply_text("🔎 Qual é o *NOME* do produto para buscar?", parse_mode="Markdown")
        return

    if estado_atual and estado_atual.startswith("teste_novo_scraping_termo"):
        if text.lower() == "cancelar":
            user_states.pop(telegram_id, None)
            await update.message.reply_text("Cancelado.", reply_markup=get_menu_por_nivel(nivel_efetivo, is_testing))
            return
            
        partes = estado_atual.split("|||")
        tipo = partes[1]
        franquia = partes[2]
        termo = text.strip()
        
        await update.message.reply_text(f"🤖 Acessando site oficial para raspar dados de '{termo}'...")
        
        from services.scraping_service import scrape_funko_product
        # Simula o scraper da funko
        resultado_scraping = scrape_funko_product(termo)
        
        if not resultado_scraping:
            await update.message.reply_text("⚠️ Não encontrei o produto na internet. Tente outro nome ou cancele.", reply_markup=get_menu_por_nivel(nivel_efetivo, is_testing))
            user_states.pop(telegram_id, None)
            return
            
        import json
        # Salva o resultado no estado para o próximo passo (precifica)
        user_states[telegram_id] = f"teste_novo_scraping_preco|||{tipo}|||{franquia}|||{json.dumps(resultado_scraping)}"
        
        msg = f"✅ *Produto Encontrado!*\n\n"
        msg += f"📦 *Nome:* {resultado_scraping['nome']}\n"
        if resultado_scraping.get('is_new'):
            msg += f"🔥 *TAG:* LANÇAMENTO / PRÉ-VENDA\n"
        msg += f"💰 *Preço Oficial:* R$ {resultado_scraping['preco_base']:.2f}\n"
        msg += f"📝 *Descrição:* {resultado_scraping['descricao']}\n\n"
        
        msg += "Qual será o nosso *PREÇO DE VENDA (R$)*?\n(Ex: 149.90)"
        
        if resultado_scraping.get('imagem_url'):
            await update.message.reply_photo(photo=resultado_scraping['imagem_url'], caption=msg, parse_mode="Markdown")
        else:
            await update.message.reply_text(msg, parse_mode="Markdown")
        return

    if estado_atual and estado_atual.startswith("teste_novo_scraping_preco"):
        if text.lower() == "cancelar":
            user_states.pop(telegram_id, None)
            await update.message.reply_text("Cancelado.", reply_markup=get_menu_por_nivel(nivel_efetivo, is_testing))
            return
            
        try:
            preco_venda = float(text.replace(",", "."))
        except ValueError:
            await update.message.reply_text("❌ Preço inválido. Digite apenas números e ponto. (Ex: 149.90)")
            return
            
        import json
        partes = estado_atual.split("|||")
        tipo = partes[1]
        franquia = partes[2]
        resultado_scraping = json.loads(partes[3])
        
        from services.supabase_service import salvar_produto
        
        # Insere no banco com prefixo [TESTE]
        nome_final = f"[TESTE] {resultado_scraping['nome']}"
        produto_db = {
            "nome": nome_final,
            "franquia": franquia,
            "preco_base": preco_venda,
            "imagem_url": resultado_scraping.get("imagem_url"),
            "status_scraping": "CONCLUIDO"
        }
        
        salvo = salvar_produto(produto_db)
        user_states.pop(telegram_id, None)
        
        if salvo:
            await update.message.reply_text(f"✅ *Produto Teste Cadastrado!*\n\nEle foi injetado no banco de dados e pronto para testes no Frontend.\n(Lembre-se: Ele não aparecerá para clientes finais).", parse_mode="Markdown", reply_markup=get_menu_por_nivel(nivel_efetivo, is_testing))
        else:
            await update.message.reply_text("❌ Erro ao salvar o produto no banco.", reply_markup=get_menu_por_nivel(nivel_efetivo, is_testing))
        return
        
    if estado_atual == "teste_del_id":
        if text.lower() == "cancelar":
            user_states.pop(telegram_id, None)
            await update.message.reply_text("Cancelado.")
            return
            
        from services.supabase_service import excluir_produto_teste
        if excluir_produto_teste(text.strip()):
            await update.message.reply_text("✅ Produto excluído com sucesso.")
        else:
            await update.message.reply_text("❌ Erro ao excluir produto. Verifique o ID.")
        user_states.pop(telegram_id, None)
        return

    if estado_atual in ["esperando_nome_revogar", "esperando_nome_suspender"]:
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
            await update.message.reply_text(f"Usuário: **{f['nome']}**\nStatus atual: {status_atual}\n\nO que você deseja fazer?", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if estado_atual and estado_atual.startswith("esperando_nome_codigo_"):
        if text.lower() == "cancelar":
            user_states.pop(telegram_id, None)
            await update.message.reply_text("Geração de código cancelada.")
            return
            
        partes = estado_atual.split("_")
        nivel_para_gerar = int(partes[3])
        medalhao = partes[4] if partes[4] != "None" else None
        is_teste = len(partes) > 5 and partes[5] == "Teste"
        
        nome_customizado = text.strip()
        
        # Anexa o nível Medalhão se existir
        if medalhao:
            nome_customizado = f"{nome_customizado} ({medalhao} Access)"
        
        from services.supabase_service import gerar_novo_codigo
        codigo = gerar_novo_codigo(funcionario['id'], nivel_para_gerar, nome_atribuido=nome_customizado, medalhao=medalhao, is_tester=is_teste)
        user_states.pop(telegram_id, None)
        
        if codigo:
            import qrcode
            from io import BytesIO
            
            # Tenta pegar o username do bot
            bot_username = context.bot.username
            deep_link = f"https://t.me/{bot_username}?start={codigo}"
            
            # Gera a imagem do QR Code
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
                f"💡 _Mande o usuário apontar a câmera do celular para este QR Code, ou envie a imagem para ele!_\\n"
                f"⚠️ *ATENÇÃO: Este código expira em 30 minutos!*\\n\\n"
                f"*(Alternativa: envie o link ou código abaixo)*\\n"
                f"Link direto: {deep_link}"
            )
            await context.bot.send_photo(chat_id=telegram_id, photo=bio, caption=mensagem, parse_mode="Markdown")
            await update.message.reply_text(f"`{codigo}`", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Erro ao gerar o código no banco de dados.")
        return



    # Comando Inicial ou Menu (Boas vindas e exibição do Teclado)
    if text.startswith("/start") or text.startswith("/menu"):
        nome_exibicao = NIVEIS.get(nivel_efetivo)
        aviso_teste = "\n*(Você está no Modo Testador)*" if is_testing else ""
        await update.message.reply_text(f"Olá {funcionario['nome']}! Sou o Piticão 🐶.\nSua área de trabalho ({nome_exibicao}) já está carregada no teclado abaixo.{aviso_teste}", reply_markup=get_menu_por_nivel(nivel_efetivo, is_testing), parse_mode="Markdown")
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

    # Se o usuário está no meio de um fluxo de cadastro e digitou "pular"
    estado_atual = user_states.get(telegram_id)
    if estado_atual and estado_atual.startswith("esperando_codigo_produto_novo") and text.lower().strip() == "pular":
        from services.supabase_service import salvar_produto
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
        salvo = salvar_produto(produto_db)
        if salvo:
            await update.message.reply_text("✅ Produto cadastrado no Catálogo Geral (sem código de barras).")
            user_states.pop(telegram_id, None)
        else:
            await update.message.reply_text("❌ Erro ao salvar no banco.")
        return

    # --- Menu Nível 1 (Quiosque) ---
    if text == "📦 Estoque":
        user_states[telegram_id] = "esperando_foto_entrada"
        await update.message.reply_text("📦 **ESTOQUE (Entrada/Cadastro)**\n\nEnvie a foto do produto + código de barras. Se o produto for novo, ele será cadastrado automaticamente. Se já existir, apenas daremos entrada (+1).", parse_mode="Markdown")
        return
        
    elif text == "🛒 Venda":
        user_states[telegram_id] = "esperando_foto_venda"
        await update.message.reply_text("🛒 **REGISTRAR VENDA (-1)**\n\nEnvie a **foto do código de barras** (ou do produto) que acabou de ser vendido.", parse_mode="Markdown")
        return
        
    elif text == "📋 Reposição":
        from services.supabase_service import supabase
        resp = supabase.table("estoque").select("quantidade, produtos(nome, ean)").eq("quiosque_id", funcionario['id']).lte("quantidade", 0).execute()
        
        if not resp.data:
            await update.message.reply_text("✅ O seu quiosque não tem nenhum item esgotado no momento!")
            return
            
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
        return
        
    elif text == "📦 Encomendas":
        from services.supabase_service import buscar_encomendas_pendentes
        encomendas = buscar_encomendas_pendentes(funcionario['id'])
        if not encomendas:
            await update.message.reply_text("✅ *Tudo limpo!*\nVocê não tem nenhuma encomenda aguardando ação neste momento.", parse_mode="Markdown")
            return
        texto = f"📦 Você tem **{len(encomendas)}** encomendas aguardando ação:\n\nSelecione um pedido abaixo para gerenciar:"
        keyboard = []
        for enc in encomendas:
            status_emoji = "⏳" if enc['status'] == "PENDENTE" else "🛍️"
            nome_botao = f"{status_emoji} #{enc['codigo_pedido']} - {enc['cliente_nome']}"
            keyboard.append([InlineKeyboardButton(nome_botao, callback_data=f"enc_detalhe_{enc['id']}")])
        await update.message.reply_text(texto, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
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
        await update.message.reply_text("Aqui geraremos links de acesso rápido aos Dashboards executivos do seu painel Web.")
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
            [InlineKeyboardButton("4️⃣ Administrador (ADM)", callback_data="gerar_4")],
            [InlineKeyboardButton("🧪 Código de Testador (TST-)", callback_data="gerar_teste_menu")]
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
        user_states[telegram_id] = "esperando_nome_revogar"
        await update.message.reply_text("Digite o **NOME EXATO** (ou parte do nome) do usuário que você deseja remover PERMANENTEMENTE do sistema.\n\n(Ou digite `Cancelar` para desistir).", parse_mode="Markdown")
        return
        
    elif text == "⏸️ Suspender/Ativar":
        if funcionario['nivel_acesso'] < 4: return
        user_states[telegram_id] = "esperando_nome_suspender"
        await update.message.reply_text("Digite o **NOME EXATO** (ou parte do nome) do usuário que você deseja suspender ou ativar.\n\n(Ou digite `Cancelar` para desistir).", parse_mode="Markdown")
        return
        
    elif text == "📊 Resumo do Sistema":
        from services.supabase_service import get_todos_funcionarios
        todos = get_todos_funcionarios()
        await update.message.reply_text(f"📊 *Status Atual do Piticão:*\n\n- Bot Operacional: Sim\n- Usuários Logados: {len(todos)}\n- Integração Gemini 1.5: Online\n\n(Painel Web em breve)", parse_mode="Markdown")
        return

    elif text == "📦 Estoque Teste":
        if funcionario['nivel_acesso'] < 4: return
        keyboard = [
            ["➕ Cadastrar Produto de Teste"],
            ["🧹 Limpar Produtos de Teste"],
            ["🔙 Voltar ao Menu"]
        ]
        await update.message.reply_text("📦 *Gerenciamento de Estoque Teste*\n\nEscolha uma opção:", parse_mode="Markdown", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return
        
    elif text == "🔙 Voltar ao Menu":
        user_states.pop(telegram_id, None)
        await update.message.reply_text("Retornando ao menu principal...", reply_markup=get_menu_por_nivel(nivel_efetivo, is_testing))
        return

    elif text == "➕ Cadastrar Produto de Teste":
        if funcionario['nivel_acesso'] < 4: return
        # Em breve usaremos a nova máquina de estados de Scraping aqui!
        user_states[telegram_id] = "teste_novo_scraping_tipo"
        keyboard = ReplyKeyboardMarkup([
            ["Funko", "Caneca e Copo"],
            ["Action Figure", "Vestuário", "Acessório"],
            ["Cancelar"]
        ], resize_keyboard=True)
        await update.message.reply_text("📦 *Novo Cadastro Inteligente*\n\nQual é o tipo de produto que você deseja cadastrar?", parse_mode="Markdown", reply_markup=keyboard)
        return
        
    elif text == "🧹 Limpar Produtos de Teste":
        if funcionario['nivel_acesso'] < 4: return
        from services.supabase_service import supabase
        # Remove todos os produtos onde franquia = 'Teste' ou nome like '[TESTE]%'
        resp = supabase.table("produtos").delete().ilike("nome", "[TESTE]%").execute()
        
        await update.message.reply_text("🧹 *Limpeza de Teste Concluída!*\n\nTodos os produtos de teste foram removidos permanentemente do banco de dados.", parse_mode="Markdown")
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
        await query.edit_message_text(f"Usuário: **{f['nome']}**\nStatus atual: {status_atual}\n\nO que você deseja fazer?", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
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

    
    if data.startswith("gerar_"):
        if data == "gerar_teste_menu":
            keyboard = [
                [InlineKeyboardButton("1️⃣ Quiosque (Teste)", callback_data="gerar_teste_nivel_1")],
                [InlineKeyboardButton("2️⃣ Marketing (Teste)", callback_data="gerar_teste_nivel_2")],
                [InlineKeyboardButton("3️⃣ Boss (Teste)", callback_data="gerar_teste_nivel_3")]
            ]
            await query.edit_message_text("Para qual perfil você quer gerar um Código de Teste (TST-)?", reply_markup=InlineKeyboardMarkup(keyboard))
            return
            
        if data.startswith("gerar_teste_nivel_"):
            nivel = int(data.replace("gerar_teste_nivel_", ""))
            nome_nivel = NIVEIS.get(nivel)
            nome_customizado = f"Perfil {nome_nivel}"
            
            from services.supabase_service import gerar_novo_codigo
            codigo = gerar_novo_codigo(funcionario['id'], nivel, nome_atribuido=nome_customizado, is_tester=True)
            
            if codigo:
                import qrcode
                from io import BytesIO
                bot_username = context.bot.username
                deep_link = f"https://t.me/{bot_username}?start={codigo}"
                
                qr = qrcode.QRCode(version=1, box_size=10, border=4)
                qr.add_data(deep_link)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                
                bio = BytesIO()
                bio.name = "teste_acesso.png"
                img.save(bio, "PNG")
                bio.seek(0)
                
                msg = f"✅ Código TST- gerado para {nome_nivel}.\nEscaneie este QR Code ou envie a imagem para o bot, ou digite o código manualmente no Modo Testador.\n\n⚠️ *ATENÇÃO: Este código expira em 30 minutos!*\n\nLink direto: {deep_link}"
                await context.bot.send_photo(chat_id=telegram_id, photo=bio, caption=msg, parse_mode="Markdown")
                await context.bot.send_message(chat_id=telegram_id, text=f"`{codigo}`", parse_mode="Markdown")
                await query.delete_message()
            else:
                await query.edit_message_text("❌ Erro ao gerar o código de teste.")
            return

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
        from services.supabase_service import supabase
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
        
        from services.supabase_service import atualizar_encomenda_status
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
            
            mensagem_persona = APRESENTACOES.get(nova_persona, APRESENTACOES["Padrão"])
            
            await query.edit_message_text(f"✅ Persona alterada para: *{nova_persona}*", parse_mode="Markdown")
            try:
                await context.bot.send_message(chat_id=telegram_id, text=mensagem_persona, parse_mode="Markdown")
            except Exception as e:
                print("Erro ao enviar mensagem de persona:", e)
        else:
            await query.edit_message_text("❌ Erro ao alterar a persona.")
            
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

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lida com o recebimento de imagens (produtos, códigos de barras, etc)."""
    if not update.message.photo:
        return
        
    telegram_id = str(update.message.from_user.id)
    from services.supabase_service import get_funcionario_by_telegram_id, salvar_produto, buscar_produto_por_ean, supabase
    funcionario = get_funcionario_by_telegram_id(telegram_id)
    
    if not funcionario:
        return
        
    estado_atual = user_states.get(telegram_id)
    if not estado_atual:
        await update.message.reply_text("Por favor, selecione uma opção no menu primeiro (ex: Estoque, Venda).")
        return

    foto_file = await update.message.photo[-1].get_file()
    
    import json
    import tempfile
    import os
    from services.gemini_service import analisar_imagem_gemini
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        await foto_file.download_to_drive(tmp_file.name)
        caminho = tmp_file.name
        
    msg_espera = await update.message.reply_text("Processando imagem...")
        
    # --- FLUXO DE ADICIONAR PRODUTO TESTE VIA FOTO ---
    if estado_atual and estado_atual.startswith("teste_add_foto"):
        partes = estado_atual.split("|||")
        nome = partes[1]
        franquia = partes[2]
        preco = float(partes[3])
        
        from services.supabase_service import upload_imagem_produto, adicionar_produto_teste
        with open(caminho, "rb") as f:
            bytes_img = f.read()
            
        url_publica = upload_imagem_produto(bytes_img, caminho)
        
        try:
            os.remove(caminho)
        except:
            pass
            
        prod = adicionar_produto_teste(nome, franquia, preco, url_publica)
        user_states.pop(telegram_id, None)
        
        if prod:
            await msg_espera.edit_text(f"✅ *Produto Teste Adicionado com Imagem!*\nNome: {prod['nome']}\nID: `{prod['id']}`", parse_mode="Markdown")
        else:
            await msg_espera.edit_text("❌ Erro ao salvar o produto no banco.")
        return

    resultado_json = analisar_imagem_gemini(caminho)
    
    try:
        os.remove(caminho)
    except:
        pass
        
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
                if existente: 
                    produto_id = existente['id']
            
            # Se não achou pelo EAN, cria o produto!
            if not produto_id:
                if not ean:
                    # Precisamos do EAN para cadastrar novo
                    user_states[telegram_id] = f"esperando_codigo_entrada|||{nome}|||{marca or ''}|||{foto_file.file_id}"
                    await msg_espera.edit_text(f"✅ Produto *{nome}* identificado como NOVO!\n\n📸 **Agora envie a foto apenas do código de barras** da embalagem para finalizarmos o cadastro e dar entrada.", parse_mode="Markdown")
                    return
                else:
                    # Tem nome e EAN, cadastra novo direto
                    produto_db = {
                        "nome": nome,
                        "marca": marca,
                        "ean": ean,
                        "foto_original_url": foto_file.file_id,
                        "foto_profissional_url": None,
                        "status_scraping": "NAO_NECESSARIO"
                    }
                    salvo = salvar_produto(produto_db)
                    if salvo:
                        # Busca o ID do produto recem criado
                        novo_prod = buscar_produto_por_ean(ean)
                        produto_id = novo_prod['id']
                    else:
                        await msg_espera.edit_text("❌ Erro ao salvar novo produto.")
                        return
                        
            # Com produto_id garantido, damos entrada no estoque
            resp_est = supabase.table("estoque").select("*").eq("produto_id", produto_id).eq("quiosque_id", funcionario['id']).execute()
            if resp_est.data:
                nova_qtd = resp_est.data[0]['quantidade'] + 1
                supabase.table("estoque").update({"quantidade": nova_qtd}).eq("id", resp_est.data[0]['id']).execute()
            else:
                supabase.table("estoque").insert({"produto_id": produto_id, "quiosque_id": funcionario['id'], "quantidade": 1}).execute()
                
            await msg_espera.edit_text("✅ Produto registrado no Catálogo (se novo) e Entrada de Estoque (+1) efetuada!")
            user_states.pop(telegram_id, None)
            
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
                    "foto_profissional_url": None,
                    "status_scraping": "NAO_NECESSARIO"
                }
                salvar_produto(produto_db)
                novo_prod = buscar_produto_por_ean(ean)
                produto_id = novo_prod['id']
                
            # Entrada no estoque
            resp_est = supabase.table("estoque").select("*").eq("produto_id", produto_id).eq("quiosque_id", funcionario['id']).execute()
            if resp_est.data:
                nova_qtd = resp_est.data[0]['quantidade'] + 1
                supabase.table("estoque").update({"quantidade": nova_qtd}).eq("id", resp_est.data[0]['id']).execute()
            else:
                supabase.table("estoque").insert({"produto_id": produto_id, "quiosque_id": funcionario['id'], "quantidade": 1}).execute()
                
            await msg_espera.edit_text("✅ Produto cadastrado com sucesso e Entrada de Estoque (+1) efetuada!")
            user_states.pop(telegram_id, None)

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
                # Se não achar o produto, cadastra com fallback e registra a venda
                # Mas para venda, melhor garantir que tem EAN
                if not ean:
                    await msg_espera.edit_text("❌ Produto não encontrado e sem EAN na foto. Tente a foto do código de barras de perto.")
                    return
                
                produto_db = {
                    "nome": nome or "Produto Desconhecido (Vendido s/ Cadastro)",
                    "marca": marca,
                    "ean": ean,
                    "foto_original_url": foto_file.file_id,
                    "foto_profissional_url": None,
                    "status_scraping": "NAO_NECESSARIO"
                }
                salvar_produto(produto_db)
                novo_prod = buscar_produto_por_ean(ean)
                produto_id = novo_prod['id']
                
            # Registra a venda
            supabase.table("vendas").insert({
                "produto_ean": ean,
                "quiosque_id": funcionario['id'],
                "quantidade": 1
            }).execute()
            
            # Subtrai do estoque
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
