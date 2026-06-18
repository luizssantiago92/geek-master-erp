import re

def fix_file():
    with open("c:/Users/c.barbosa.CELLAIRIS/Downloads/Luiz/Master Geek/piticao_bot/bot/handlers.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Replacing specific broken strings
    content = content.replace(
        'await update.message.reply_text("📦 **ESTOQUE (Entrada/Cadastro)**\n\nEnvie a foto do produto + código de barras. Se o produto for novo, ele será cadastrado automaticamente. Se já existir, apenas daremos entrada (+1).", parse_mode="Markdown")',
        'await update.message.reply_text("📦 **ESTOQUE (Entrada/Cadastro)**\\n\\nEnvie a foto do produto + código de barras. Se o produto for novo, ele será cadastrado automaticamente. Se já existir, apenas daremos entrada (+1).", parse_mode="Markdown")'
    )
    
    content = content.replace(
        'await update.message.reply_text("🛒 **REGISTRAR VENDA (-1)**\n\nEnvie a **foto do código de barras** (ou do produto) que acabou de ser vendido.", parse_mode="Markdown")',
        'await update.message.reply_text("🛒 **REGISTRAR VENDA (-1)**\\n\\nEnvie a **foto do código de barras** (ou do produto) que acabou de ser vendido.", parse_mode="Markdown")'
    )

    content = content.replace(
        'texto = "🚨 **LISTA DE REPOSIÇÃO** 🚨\n\nOs seguintes itens estão esgotados no seu quiosque:\n\n"',
        'texto = "🚨 **LISTA DE REPOSIÇÃO** 🚨\\n\\nOs seguintes itens estão esgotados no seu quiosque:\\n\\n"'
    )

    content = content.replace(
        'texto += f"• {nome} (EAN: {ean})\n"',
        'texto += f"• {nome} (EAN: {ean})\\n"'
    )

    content = content.replace(
        'await update.message.reply_text("✅ *Tudo limpo!*\nVocê não tem nenhuma encomenda aguardando ação neste momento.", parse_mode="Markdown")',
        'await update.message.reply_text("✅ *Tudo limpo!*\\nVocê não tem nenhuma encomenda aguardando ação neste momento.", parse_mode="Markdown")'
    )

    content = content.replace(
        'texto = f"📦 Você tem **{len(encomendas)}** encomendas aguardando ação:\n\nSelecione um pedido abaixo para gerenciar:"',
        'texto = f"📦 Você tem **{len(encomendas)}** encomendas aguardando ação:\\n\\nSelecione um pedido abaixo para gerenciar:"'
    )

    with open("c:/Users/c.barbosa.CELLAIRIS/Downloads/Luiz/Master Geek/piticao_bot/bot/handlers.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    fix_file()
