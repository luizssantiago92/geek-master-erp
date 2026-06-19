import os
import re

def update_handlers():
    file_path = "c:/Users/c.barbosa.CELLAIRIS/Downloads/Luiz/Master Geek/piticao_bot/bot/handlers.py"
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update the Onboarding logic (Stealth Mode block)
    old_stealth = """    # STEALTH MODE: Zero-Trust Absoluto
    if not funcionario:
        return"""

    new_stealth = """    # STEALTH MODE: Zero-Trust Absoluto
    if not funcionario:
        codigo = None
        # Se for texto, pode ser o deep link do QR Code ou código digitado manualmente
        if text:
            texto_limpo = text.strip()
            if texto_limpo.startswith("/start "):
                codigo = texto_limpo.replace("/start ", "").strip().upper()
            elif texto_limpo.startswith("/menu") or texto_limpo == "/start":
                await update.message.reply_text("👋 Olá! Eu sou o Piticão.\\n\\nPara acessar o sistema corporativo, você precisa de um **Código de Acesso** (Ex: PTC-XXXX). Peça ao seu gestor e envie o código aqui, ou aponte a câmera do celular para o QR Code gerado pelo administrador.")
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
                from services.supabase_service import get_funcionario_by_telegram_id
                funcionario = get_funcionario_by_telegram_id(telegram_id)
            else:
                return
        else:
            # Se não é um código válido, ignora (stealth mode)
            return"""
            
    content = content.replace(old_stealth, new_stealth)

    # 2. Update normal Code Generation
    old_gen = """        if codigo:
            # Prepara a mensagem de compartilhamento para o WhatsApp
            import urllib.parse
            mensagem_whatsapp = (
                f"Olá! Este é o seu código de acesso exclusivo para o bot Piticão.\\n\\n"
                f"Cargo: {NIVEIS.get(nivel_para_gerar)}\\n"
                f"Código: {codigo}\\n\\n"
                f"Abra o Telegram, procure pelo nosso bot e envie este código para validar seu acesso.\\n\\n"
                f"⚠️ *ATENÇÃO:* Este código expira em 30 minutos! Caso ele expire, você terá que solicitar um novo código."
            )
            texto_url = urllib.parse.quote(mensagem_whatsapp)
            link_whatsapp = f"https://api.whatsapp.com/send?text={texto_url}"
            
            # Adiciona o botão de compartilhar
            keyboard_share = [[InlineKeyboardButton("📲 Compartilhar via WhatsApp", url=link_whatsapp)]]
            reply_markup_share = InlineKeyboardMarkup(keyboard_share)

            await update.message.reply_text(
                f"🎟️ *Código de Acesso Gerado com Sucesso!*\\n\\n"
                f"Cargo: *{NIVEIS.get(nivel_para_gerar)}*\\n"
                f"Nome Vinculado: *{nome_customizado}*\\n\\n"
                f"💡 _Dica: Você pode copiar o código da mensagem abaixo ou usar o botão para enviar direto pro WhatsApp._",
                parse_mode="Markdown",
                reply_markup=reply_markup_share
            )
            # Envia o código em uma mensagem isolada para facilitar a cópia
            await update.message.reply_text(f"`{codigo}`", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Erro ao gerar o código no banco de dados.")
        return"""

    new_gen = """        if codigo:
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
                f"🎟️ *Código de Acesso Gerado com Sucesso!*\\n\\n"
                f"Cargo: *{NIVEIS.get(nivel_para_gerar)}*\\n"
                f"Nome Vinculado: *{nome_customizado}*\\n\\n"
                f"💡 _Mande o usuário apontar a câmera do celular para este QR Code, ou envie a imagem para ele!_\n"
                f"*(Alternativa: envie o link ou código abaixo)*\n"
                f"Link direto: {deep_link}"
            )
            await context.bot.send_photo(chat_id=telegram_id, photo=bio, caption=mensagem, parse_mode="Markdown")
            await update.message.reply_text(f"`{codigo}`", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Erro ao gerar o código no banco de dados.")
        return"""
        
    content = content.replace(old_gen, new_gen)
    
    # 3. Update test code generation in handle_callback
    old_teste = """            if codigo:
                await query.edit_message_text(f"✅ Código TST- gerado para {nome_nivel}:\\n\\n`{codigo}`\\n\\nVá no Modo Testador e insira este código.", parse_mode="Markdown")
            else:"""
            
    new_teste = """            if codigo:
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
                
                msg = f"✅ Código TST- gerado para {nome_nivel}.\\nEscaneie este QR Code ou envie a imagem para o bot, ou digite o código manualmente no Modo Testador.\\nLink direto: {deep_link}"
                await context.bot.send_photo(chat_id=telegram_id, photo=bio, caption=msg, parse_mode="Markdown")
                await context.bot.send_message(chat_id=telegram_id, text=f"`{codigo}`", parse_mode="Markdown")
                await query.delete_message()
            else:"""

    content = content.replace(old_teste, new_teste)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("QR Code logic implemented successfully.")

if __name__ == "__main__":
    update_handlers()
