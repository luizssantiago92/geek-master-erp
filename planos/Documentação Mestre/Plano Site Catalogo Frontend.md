# Plano Site Catálogo Frontend (Público)

## 1. Objetivo e Função
O Frontend do Site Catálogo é a Vitrine da loja física na internet. Sua principal função é exibir os produtos que estão no estoque e incentivar o cliente a fazer uma compra ou reserva.

## 2. Tipos de Usuário
- **Visitantes Anônimos:** Clientes que apenas navegam pela vitrine, olham os lançamentos e preços.
- **Clientes Logados:** Clientes que criaram uma conta (Cadastro) e fizeram Login. Têm acesso ao perfil, lista de desejos e histórico.

## 3. Funcionamento e Etapas (Experiência do Cliente)

1. **Autenticação e Cadastro:**
   - **Login:** O sistema terá opções de login (ex: e-mail/senha ou Google). 
   - **Completar Cadastro:** Após a criação da conta básica, o cliente será direcionado para uma página onde preencherá seus dados vitais (Nome completo, Telefone, Endereço de entrega, CPF) para que o sistema saiba quem ele é.
2. **Navegação na Vitrine (Home):**
   - O cliente acessa o site e vê apenas os produtos que possuem o `status_publicacao = 'PUBLICADO'`.
   - Há um bloqueio de segurança: Qualquer produto cadastrado pelo robô que inicie com a palavra `[TESTE]` nunca aparecerá aqui.
   - Os produtos exibem banners de **"Lançamento"** baseados nos dados coletados pelo scraper.
3. **Página do Produto e Recomendações:**
   - Ao clicar num produto, o cliente vê a galeria de imagens oficiais, preço e descrição técnica.
   - O site exibirá seções dinâmicas de "Quem viu isto, também viu..." (Recomendações cruzadas de produtos similares ou da mesma franquia).
4. **Carrinho / Checkout:**
   - O cliente adiciona itens ao carrinho.
   - A página de Checkout exibe o total.

## 4. Questões em Aberto / Pendências a Resolver
- **Finalização do Checkout:** O fluxo de Checkout final vai gerar um Pix automático e realizar a venda direto pelo site, ou vai redirecionar a lista de compras para o WhatsApp para que o vendedor finalize a negociação humanizada?
- **Sistema de Fidelidade / Ranking:** Será necessário integrar o ranking de clientes (XP) já no cadastro/login do frontend?
