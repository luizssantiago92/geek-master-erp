from datetime import datetime
from telegram import ReplyKeyboardMarkup

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
            ["🔗 Página de Ajustes", "🎭 Escolher Persona"]
        ]
    elif nivel == 3:
        keyboard = [
            ["📊 Dashboards de Resultados"],
            ["🔐 Aprovações Pendentes", "🔄 Sincronizar Catálogos"],
            ["🔗 Página de Ajustes", "🎭 Escolher Persona"]
        ]
    elif nivel == 4:
        keyboard = [
            ["🛠️ Sistema", "🎭 Personas"],
            ["🔗 Página de Ajustes", "🧪 Modo Testador"],
            ["🔄 Sincronizar Catálogos"]
        ]
    else:
        keyboard = [["/start"]]
        
    if is_testing:
        keyboard.append(["🔙 Sair do Teste"])
        
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
