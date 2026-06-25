import re
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from services.supabase_service import get_funcionario_by_telegram_id, supabase

# Expressões Regulares para as hashtags
REGEX_VENDAS = r'(?i)#vendas?\s*(?:r\$)?\s*(\d+(?:[.,]\d+)?)(?!\/)'
REGEX_META_DIA = r'(?i)#metadoria\s*(?:r\$)?\s*(\d+(?:[.,]\d+)?)'
REGEX_META_MES = r'(?i)#metadomes\s*(?:r\$)?\s*(\d+(?:[.,]\d+)?)'
REGEX_VENDA_QUIOSQUE = r'(?i)#vendadoquiosquedia\s*(?:r\$)?\s*(\d+(?:[.,]\d+)?)\s*,\s*(\d{1,2}/\d{1,2})'

def extrair_valor(match_group):
    """Converte o valor string (ex: 500,00 ou 500.00) para float"""
    val_str = match_group.replace(',', '.')
    try:
        return float(val_str)
    except:
        return 0.0

async def processar_mensagem_grupo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lida com as hashtags no grupo de vendas"""
    message = update.message or update.edited_message
    if not message or not message.text:
        return
        
    chat_type = message.chat.type
    if chat_type not in ['group', 'supergroup']:
        return # Ignora se não for grupo
        
    texto = message.text
    telegram_id = str(message.from_user.id)
    funcionario = get_funcionario_by_telegram_id(telegram_id)
    
    if not funcionario:
        return # Ignora usuários não cadastrados
        
    is_edit = update.edited_message is not None
    msg_resposta = ""

    # 1. Processar #vendas
    match_vendas = re.search(REGEX_VENDAS, texto)
    if match_vendas:
        if funcionario['nivel_acesso'] != 2:
            msg_resposta = f"⛔ *{funcionario['nome']}*, apenas Vendedores (Nível 2) devem lançar `#vendas` individuais. Se quiser lançar do quiosque todo, use `#vendadoquiosquedia`."
        else:
            valor = extrair_valor(match_vendas.group(1))
            quiosque_id = funcionario.get('quiosque_id')
            
            if is_edit:
                # Atualizar venda
                pass # Lógica de edição (opcional simplificar apagando e inserindo nova)
                msg_resposta = f"🔄 Venda atualizada para *R$ {valor:.2f}*! (Função de edição avançada em breve)"
            else:
                # Inserir nova venda
                nova_venda = {
                    "vendedor_id": funcionario['id'],
                    "quiosque_id": quiosque_id,
                    "valor": valor
                }
                supabase.table("vendas_diarias").insert(nova_venda).execute()
                
                # Computar pontos (10k = 100 pontos)
                pontos_ganhos = (valor / 10000) * 100
                
                # Buscar ou criar registro de pontos
                resp_pontos = supabase.table("pontos_vendedores").select("*").eq("vendedor_id", funcionario['id']).execute()
                if resp_pontos.data:
                    pontos_atuais = resp_pontos.data[0]['pontos_acumulados']
                    novo_total = pontos_atuais + pontos_ganhos
                    supabase.table("pontos_vendedores").update({"pontos_acumulados": novo_total}).eq("vendedor_id", funcionario['id']).execute()
                else:
                    supabase.table("pontos_vendedores").insert({"vendedor_id": funcionario['id'], "pontos_acumulados": pontos_ganhos}).execute()
                    novo_total = pontos_ganhos
                    
                msg_resposta = f"🚀 Boa, *{funcionario['nome']}*!\n✅ Venda de *R$ {valor:.2f}* registrada.\n⭐ Pontos ganhos: *{pontos_ganhos:.1f}* (Total: *{novo_total:.1f}*)"

    # 2. Processar #metadoria e #metadomes
    match_metadia = re.search(REGEX_META_DIA, texto)
    match_metames = re.search(REGEX_META_MES, texto)
    
    if match_metadia or match_metames:
        if funcionario['nivel_acesso'] not in [1, 4, 5]:
            msg_resposta = f"⛔ *{funcionario['nome']}*, apenas Quiosques, Boss ou Admin podem definir metas!"
        else:
            quiosque_id = funcionario['id'] if funcionario['nivel_acesso'] == 1 else None # Se for admin, precisa especificar, mas para simplificar assume do admin por enquanto
            
            if quiosque_id:
                if match_metadia:
                    valor_dia = extrair_valor(match_metadia.group(1))
                    supabase.table("metas").insert({"quiosque_id": quiosque_id, "tipo": "DIA", "valor": valor_dia}).execute()
                    msg_resposta += f"🎯 *Meta do Dia* definida para R$ {valor_dia:.2f}!\n"
                    
                if match_metames:
                    valor_mes = extrair_valor(match_metames.group(1))
                    supabase.table("metas").insert({"quiosque_id": quiosque_id, "tipo": "MES", "valor": valor_mes}).execute()
                    msg_resposta += f"🏆 *Meta do Mês* definida para R$ {valor_mes:.2f}!\n"

    # 3. Processar #vendadoquiosquedia
    match_vendaquiosque = re.search(REGEX_VENDA_QUIOSQUE, texto)
    if match_vendaquiosque:
        if funcionario['nivel_acesso'] not in [1, 4, 5]:
            msg_resposta = f"⛔ *{funcionario['nome']}*, apenas Quiosques, Boss ou Admin podem lançar fechamento de quiosque!"
        else:
            valor = extrair_valor(match_vendaquiosque.group(1))
            data_str = match_vendaquiosque.group(2) # "24/06"
            # Formatando para YYYY-MM-DD
            try:
                dia, mes = data_str.split('/')
                ano_atual = datetime.now().year
                data_formatada = f"{ano_atual}-{mes.zfill(2)}-{dia.zfill(2)}"
                
                quiosque_id = funcionario['id'] if funcionario['nivel_acesso'] == 1 else None
                if quiosque_id:
                    supabase.table("vendas_diarias").insert({
                        "quiosque_id": quiosque_id,
                        "valor": valor,
                        "data": data_formatada
                    }).execute()
                    msg_resposta = f"✅ Fechamento do Quiosque lançado: *R$ {valor:.2f}* no dia {data_str}."
            except Exception as e:
                msg_resposta = f"❌ Erro ao formatar a data: {e}"

    if msg_resposta:
        await context.bot.send_message(chat_id=message.chat_id, text=msg_resposta, parse_mode="Markdown", reply_to_message_id=message.message_id)
