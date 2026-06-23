from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes
import json
from services.supabase_service import adicionar_perfil_teste, validar_codigo_teste, salvar_produto, excluir_produto_teste
from bot.state import user_states, impersonation_states
from bot.handlers.core import get_menu_por_nivel, NIVEIS

async def handle_tester_messages(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, telegram_id: str, funcionario: dict, nivel_efetivo: int, is_testing: bool) -> bool:
    """Retorna True se a mensagem foi tratada aqui."""
    estado_atual = user_states.get(telegram_id)
    nivel_real = funcionario['nivel_acesso']

    # Entrando no teste de simulação (onboarding)
    if estado_atual == "esperando_codigo_teste":
        codigo = text.strip().upper()
        if text.lower() == "cancelar":
            user_states.pop(telegram_id, None)
            await update.message.reply_text("Simulação cancelada.")
            return True
            
        if not codigo.startswith("TST-"):
            await update.message.reply_text("❌ Código inválido. Para simular Onboarding, você deve usar um *Código de Testador* (que começa com TST-).\nDigite o código novamente ou envie Cancelar.", parse_mode="Markdown")
            return True
            
        nivel_teste = validar_codigo_teste(codigo)
        if not nivel_teste:
             await update.message.reply_text("❌ Código de teste inválido, expirado ou já utilizado.")
             return True
             
        user_states.pop(telegram_id, None)
        impersonation_states[telegram_id] = nivel_teste
        adicionar_perfil_teste(funcionario['id'], nivel_teste)
        
        nome_exibicao = NIVEIS.get(nivel_teste)
        await update.message.reply_text(f"*(SIMULAÇÃO DE CADASTRO)*\n✅ Código Verificado! Bem-vindo(a) à ERP Project.\nSeu perfil de **{nome_exibicao}** foi salvo nos seus atalhos de teste.", parse_mode="Markdown")
        await update.message.reply_text(f"Olá {funcionario['nome']}! Sou o Piticão 🐶.\nSua área de trabalho ({nome_exibicao}) já está carregada no teclado abaixo.\n*(Você está no Modo Testador)*", reply_markup=get_menu_por_nivel(nivel_teste, True), parse_mode="Markdown")
        return True

    if text == "🔙 Sair do Teste" and is_testing:
        impersonation_states.pop(telegram_id, None)
        await update.message.reply_text("🧪 Teste encerrado. Bem-vindo de volta à conta de Administrador principal.", reply_markup=get_menu_por_nivel(nivel_real, False))
        return True

    # Comandos do menu "Modo Testador"
    if text == "📦 Estoque Teste":
        if funcionario['nivel_acesso'] < 4: return True
        keyboard = [
            ["➕ Cadastrar Produto de Teste"],
            ["🧹 Limpar Produtos de Teste"],
            ["🔙 Voltar ao Menu"]
        ]
        await update.message.reply_text("📦 *Gerenciamento de Estoque Teste*\n\nEscolha uma opção:", parse_mode="Markdown", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return True

    if text == "➕ Cadastrar Produto de Teste":
        if funcionario['nivel_acesso'] < 4: return True
        user_states[telegram_id] = "teste_novo_scraping_tipo"
        keyboard = ReplyKeyboardMarkup([
            ["Funko", "Caneca e Copo"],
            ["Action Figure", "Vestuário", "Acessório"],
            ["🔙 Voltar ao Menu"]
        ], resize_keyboard=True)
        await update.message.reply_text("📦 *Novo Cadastro Inteligente*\n\nQual é o tipo de produto que você deseja cadastrar?", parse_mode="Markdown", reply_markup=keyboard)
        return True

    if text == "🧹 Limpar Produtos de Teste":
        if funcionario['nivel_acesso'] < 4: return True
        from services.supabase_service import supabase
        supabase.table("produtos").delete().eq("status_publicacao", "PENDENTE").execute()
        await update.message.reply_text("🧹 *Limpeza de Teste Concluída!*\n\nTodos os produtos pendentes no catálogo (incluindo do Quiosque e Testes) foram removidos permanentemente de todo o ecossistema.", parse_mode="Markdown")
        return True

    # Máquina de estado Scraping de Teste
    if estado_atual == "teste_novo_scraping_tipo" and text.lower() not in ["funko", "cancelar", "🔙 voltar ao menu"]:
        user_states[telegram_id] = f"teste_novo_scraping_franquia|||{text}"
        await update.message.reply_text("Qual é a *FRANQUIA* do produto?\n(Ex: Marvel, Disney, Toy Story)", parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
        return True

    if estado_atual and estado_atual.startswith("teste_novo_scraping_franquia"):
        if text.lower() == "cancelar":
            user_states.pop(telegram_id, None)
            await update.message.reply_text("Cancelado.", reply_markup=get_menu_por_nivel(nivel_efetivo, is_testing))
            return True
            
        tipo = estado_atual.split("|||")[1]
        franquia = text.strip()
        user_states[telegram_id] = f"teste_novo_scraping_termo|||{tipo}|||{franquia}"
        await update.message.reply_text("🔎 Qual é o *NOME EXATO* do produto para buscar?", parse_mode="Markdown")
        return True

    if estado_atual and estado_atual.startswith("teste_novo_scraping_termo"):
        if text.lower() == "cancelar":
            user_states.pop(telegram_id, None)
            await update.message.reply_text("Cancelado.", reply_markup=get_menu_por_nivel(nivel_efetivo, is_testing))
            return True
            
        partes = estado_atual.split("|||")
        tipo = partes[1]
        franquia = partes[2]
        termo = text.strip()
        
        await update.message.reply_text(f"🤖 Acessando site oficial para raspar dados de '{termo}'...")
        from services.scraping_service import scrape_funko_product
        resultado_scraping = scrape_funko_product(termo)
        
        if not resultado_scraping:
            await update.message.reply_text("⚠️ Não encontrei o produto na internet. Tente outro nome ou cancele.", reply_markup=get_menu_por_nivel(nivel_efetivo, is_testing))
            user_states.pop(telegram_id, None)
            return True
            
        user_states[telegram_id] = f"teste_novo_scraping_preco|||{tipo}|||{franquia}|||{json.dumps(resultado_scraping)}"
        
        msg = f"✅ *Produto Encontrado!*\n\n"
        msg += f"📦 *Nome:* {resultado_scraping['nome']}\n"
        if resultado_scraping.get('is_new'): msg += f"🔥 *TAG:* LANÇAMENTO / PRÉ-VENDA\n"
        msg += f"💰 *Preço Oficial:* R$ {resultado_scraping['preco_base']:.2f}\n"
        msg += f"📝 *Descrição:* {resultado_scraping['descricao']}\n\n"
        msg += "Qual será o nosso *PREÇO DE VENDA (R$)*?\n(Ex: 149.90)"
        
        if resultado_scraping.get('imagem_url'):
            await update.message.reply_photo(photo=resultado_scraping['imagem_url'], caption=msg, parse_mode="Markdown")
        else:
            await update.message.reply_text(msg, parse_mode="Markdown")
        return True

    if estado_atual and estado_atual.startswith("teste_novo_scraping_preco"):
        if text.lower() == "cancelar":
            user_states.pop(telegram_id, None)
            await update.message.reply_text("Cancelado.", reply_markup=get_menu_por_nivel(nivel_efetivo, is_testing))
            return True
            
        try:
            preco_venda = float(text.replace(",", "."))
        except ValueError:
            await update.message.reply_text("❌ Preço inválido. Digite apenas números e ponto. (Ex: 149.90)")
            return True
            
        partes = estado_atual.split("|||")
        franquia = partes[2]
        resultado_scraping = json.loads(partes[3])
        
        nome_final = f"[TESTE] {resultado_scraping['nome']}"
        produto_db = {
            "nome": nome_final,
            "franquia": franquia,
            "preco_base": preco_venda,
            "imagem_url": resultado_scraping.get("imagem_url"),
            "status_scraping": "CONCLUIDO",
            "status_publicacao": "PENDENTE",
            "descricao": resultado_scraping.get("descricao"),
            "is_new": resultado_scraping.get("is_new", False),
            "imagens_galeria": resultado_scraping.get("imagens_galeria", [])
        }
        
        salvo = salvar_produto(produto_db)
        user_states.pop(telegram_id, None)
        
        if salvo:
            await update.message.reply_text(f"✅ *Produto Teste Cadastrado!*\n\nEle foi injetado no banco de dados e pronto para testes no Frontend.\n(Lembre-se: Ele não aparecerá para clientes finais).", parse_mode="Markdown", reply_markup=get_menu_por_nivel(nivel_efetivo, is_testing))
        else:
            await update.message.reply_text("❌ Erro ao salvar o produto no banco.", reply_markup=get_menu_por_nivel(nivel_efetivo, is_testing))
        return True

    if estado_atual == "teste_del_id":
        if text.lower() == "cancelar":
            user_states.pop(telegram_id, None)
            await update.message.reply_text("Cancelado.")
            return True
        if excluir_produto_teste(text.strip()):
            await update.message.reply_text("✅ Produto excluído com sucesso.")
        else:
            await update.message.reply_text("❌ Erro ao excluir produto. Verifique o ID.")
        user_states.pop(telegram_id, None)
        return True

    return False
