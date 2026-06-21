# Documentação Mestre do Projeto Master Geek (Bot + Site)

Este documento reflete as regras de negócio e o funcionamento atual do projeto para evitar conflitos futuros. Qualquer atualização estrutural passará por validação de conflito com este documento.

---

## 1. O Bot do Telegram (`piticao_bot`)

**Propósito:** Assistente administrativo para automatizar o cadastro de produtos no banco de dados (Supabase), eliminando cadastro manual pelo lojista.

### 1.1. Cadastro Inteligente de Funko Pops
O fluxo atual de cadastro da categoria Funko Pop segue estas etapas:

1. **Ação do Lojista:** No menu inicial, seleciona a opção `"Funko Pop"`.
2. **Entrada de Dados:** O bot oferece duas formas de inserir o produto:
   - **(Recomendado) Via Foto:** O lojista envia uma foto da caixa. O bot aciona a IA (Gemini Vision) para extrair o Nome do Personagem, Franquia e Número. O bot pede confirmação: *"É este produto: BONECO FUNKO POP! [Franquia] - [Nome] #[Numero]?"*
   - **Manual:** O lojista digita, em três mensagens sequenciais, o Nome, a Franquia e o Número da caixa.
3. **Regra de Agilidade:** O bot NÃO DEVE pedir preço, descrição ou imagem de catálogo para Funkos. Essa etapa é 100% automatizada.
4. **Processamento em Lote (Background):** Após a confirmação, o bot avisa *"Processando..."* e já libera a tela para o lojista enviar a próxima foto. O produto entra numa fila onde o Scraper atuará.

### 1.2. O Scraper de Enriquecimento (Buscador Web)
- **Como Funciona:** Em segundo plano, o código (`scraping_service.py`) procura o produto na internet para achar a foto oficial do catálogo, preço e descrição técnica.
- **Status Atual:** Atualmente, o scraper está rodando em "Modo de Simulação (Mock)". Ele atribui uma foto padrão e dados fictícios.
- **Próximo Passo Aprovado (A implementar):** Substituir essa simulação por uma integração real com o navegador oculto (*Playwright*). O robô vai baixar a imagem real (ex: Toy Story 5), fazer o upload dela para o Supabase Storage (para evitar bloqueios de hospedagem de terceiros) e salvar a URL permanente no banco.

---

## 2. O Site / E-Commerce (React + Vite)

**Propósito:** Vitrine online para clientes e Painel de Aprovação para o lojista.

### 2.1. O Banco de Dados (Supabase)
Todo controle de visibilidade é feito pela coluna **`status_publicacao`** na tabela `produtos`.
- **`PENDENTE`:** Produto cadastrado pelo Bot. Aguardando revisão humana. (Invisível no site).
- **`PUBLICADO`:** Aprovado e visível na vitrine para venda.

### 2.2. Painel Administrativo (`/admin`)
- Funciona como a mesa de trabalho do lojista na web. Lista todos os produtos cadastrados.
- **Recursos Atuais:**
  - Edição individual de Preço, Nome, Descrição e selo de "Lançamento".
  - **Ações em Massa:** Checkboxes de seleção. Botões no topo para "Salvar Selecionados" ou "Enviar Selecionados para Site" de uma vez só.
- **Proteção Anti-Quebra:** Se o link oficial da imagem falhar por algum motivo, a interface exibe um bloco cinza "Sem Foto" ao invés do ícone de imagem quebrada do navegador.

### 2.3. A Vitrine (Home)
- Consome exclusivamente os itens com status `PUBLICADO`.
- Filtra qualquer produto que comece com `[TESTE]` ou que não tenha passado pela aprovação do painel admin.

---

## 3. Integração Futura: WhatsApp
Quando o módulo WhatsApp for iniciado, ele precisará consultar estas regras de produto (status, formatação de nome) para garantir que a experiência do usuário pelo WhatsApp consuma a mesma base de dados já aprovada e higienizada. Novas regras de atendimento via IA serão adicionadas a este documento.

---
> **Política de Conflitos:** Ao pedir uma alteração, se o pedido contradizer o fluxo acima (por exemplo, pedir para o bot do telegram perguntar o preço de um Funko), o assistente deverá barrar a ação e perguntar se a Regra Oficial descrita aqui deve ser revogada.
