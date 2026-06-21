# Interface do Usuário: Quiosque (Vendedor)

**Nível de Acesso:** Operacional
**Responsável:** Operação de caixa, organização física e primeiro contato com o bot no momento de chegada de mercadorias.

## Ferramentas Disponíveis no Telegram (Botões Principais)

1. **📦 Adicionar Produto (Estoque Base):**
   - **Descrição:** Função rápida para escanear ou fotografar produtos que chegaram na loja física.
   - **Comportamento:** O Quiosque envia a foto do produto. O Bot (usando IA + Scraper) processa a imagem e cria o rascunho do item no banco de dados com o status `PENDENTE`.

2. **🔎 Consultar Disponibilidade:**
   - **Descrição:** Busca rápida no banco.
   - **Comportamento:** Para não perder vendas físicas, o vendedor pode perguntar ao Bot (ex: "Tem o Funko do Naruto?") e o bot responde se há registro na loja, agilizando o atendimento.

## Permissões na "Página de Ajustes de Catálogo" (Backend Web)
- **Acesso Quase Nulo:** O vendedor de quiosque geralmente **não** precisará entrar na página web de ajustes. O trabalho dele se encerra ao mandar a foto ou código de barras no Telegram (alimentar o início do funil). As edições e correções são de responsabilidade do Marketing, Boss e Admin.
