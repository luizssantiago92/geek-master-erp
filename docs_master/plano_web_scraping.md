# Plano de Implementação: Web Scraping Funko & Atualizações no E-commerce

Este plano incorpora os novos requisitos dos áudios mais recentes: 
1) O fluxo detalhado de como rasparemos o site `funko.com.br`.
2) A garantia de que produtos de `[TESTE]` nunca aparecerão na vitrine online.
3) A adição de recomendações e banners na aplicação React (Home e Checkout).

## 1. Módulo de Scraping (`scraping_service.py`)
Criaremos a inteligência de raspagem voltada especificamente para o site da Funko (`funko.com.br`) usando `BeautifulSoup` e contornando eventuais erros de SSL/pip.
- **Identificadores:** Vamos capturar as tags `LANÇAMENTO` ou `PRÉ-VENDA`. Se existirem, marcaremos o produto com a flag `isNew`.
- **Imagens:** O site tem as 3 fotos menores na lateral esquerda e a foto principal. O bot extrairá a galeria completa.
- **Dados:** Título, Preço, Descrição (texto informativo que fica abaixo da imagem/ao lado) serão salvos no banco.
- **Salvar como Teste:** O bot irá prefixar o nome com `[TESTE] ` e injetará no banco `produtos`.

## 2. Bloqueio de Testes na Aplicação (`Home.jsx`)
- Como solicitado ("nunca vão aparecer no sistema online"), na nossa vitrine React, criaremos um filtro automático no banco ou na interface que **oculta permanentemente** qualquer produto cujo nome comece com `[TESTE]`.
- Assim você pode cadastrar e deletar no backend sem sujar a vitrine real.

## 3. UI/UX: Home & Recomendações
- **Banners Temáticos:** Vamos adicionar uma seção customizada na `Home.jsx` (ex: um Banner no formato *Toy Story* ou *Lançamentos*).
- **Seção "Quem viu isto, também viu":**
  - Vamos adicionar esta seção no final do carrinho no **`Checkout.jsx`**, recomendando itens complementares aos que o cliente tem no carrinho (ou aleatórios, caso o carrinho esteja vazio).
  - Vamos adicionar também na `Home.jsx` uma área dedicada de produtos sugeridos, como você mencionou.

## 4. Próximos Passos
1. Corrigir a instalação do BeautifulSoup.
2. Implementar `scraping_service.py` focando no padrão HTML que você mandou na imagem da Jessie.
3. Atualizar as views da aplicação web.

> [!IMPORTANT]
> **Aprovação Necessária**
> Como o plano envolve filtrar produtos no frontend e alterar a interface da Home e do Checkout para adicionar recomendações, preciso da sua confirmação final.
> Posso prosseguir com a implementação destas alterações no bot e no frontend?
