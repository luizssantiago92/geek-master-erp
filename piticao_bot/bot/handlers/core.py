from datetime import datetime
from telegram import ReplyKeyboardMarkup

NIVEIS = {
    1: "Quiosque (Vendedor)",
    2: "Marketing",
    3: "Boss",
    4: "Administrador"
}

def obter_saudacao():
    hora = datetime.now().hour
    if 5 <= hora < 12:
        return "Bom dia"
    elif 12 <= hora < 18:
        return "Boa tarde"
    else:
        return "Boa noite"

from telegram import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

URL_MINI_APP = "https://geek-master-erp.vercel.app/admin" # Atualize esta URL após o deploy na Vercel

def get_menu_por_nivel(nivel: int, is_tester_mode: bool = False) -> ReplyKeyboardMarkup:
    """Retorna o teclado principal adequado ao nível de acesso do usuário."""
    if nivel == 1:
        keyboard = [
            ["📦 Estoque (Entrada)", "🛒 Venda (Saída)"],
            ["📋 Reposição", "📦 Encomendas"]
        ]
    elif nivel == 2:
        keyboard = [
            ["📊 Relatórios (Em breve)"],
            [KeyboardButton("🏢 Página de Ajustes", web_app=WebAppInfo(url=URL_MINI_APP))]
        ]
    elif nivel == 3:
        keyboard = [
            ["🛍️ Modo Venda", "📦 Modo Estoque", "🔄 Sincronizar Catálogos"],
            [KeyboardButton("🏢 Página de Ajustes", web_app=WebAppInfo(url=URL_MINI_APP))],
            ["🔙 Voltar ao Menu"]
        ]
    elif nivel == 4:
        keyboard = [
            ["⚙️ Controle de Sistema", "🧑‍💻 Modo Testador"]
        ]
    else:
        keyboard = [["/start"]]
        
    if is_tester_mode:
        keyboard.append(["🔙 Sair do Teste"])
        
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
