# Plano Chatbot (Telegram) - Bíblia do Sistema

## 1. Objetivo e Função
O Chatbot no Telegram atua como um **Assistente Administrativo (Backoffice)** para a loja física e online. Sua principal função é eliminar o trabalho braçal de cadastro de produtos, gerenciamento de estoque e campanhas, funcionando como o cérebro central de entrada de dados no Supabase.

## 2. Autenticação e Controle de Acesso Restrito
O sistema é inviolável e não permite "cadastro aberto". Todo usuário precisa de um convite para existir.
- **Convite Único (Código/QRCode):** O administrador gera um código de acesso único atrelado a um nome e um perfil hierárquico (Cargo). O usuário novato entra no Telegram, digita (ou escaneia) esse código e vincula o próprio Telegram ID ao cargo previamente definido.
- **Gerenciamento de Vínculos:** O Administrador tem poder absoluto sobre quem está no sistema:
  - Pode **Desativar/Ativar** temporariamente o acesso de um funcionário sem deletar seus dados históricos.
  - Pode **Revogar (Deletar)** permanentemente um Telegram ID do banco. Nesse caso, a pessoa só consegue entrar de novo se o Adm gerar um código inteiramente novo.

## 3. Os 4 Perfis de Usuário (Hierarquia)
O bot exibe menus diferentes dependendo do cargo da pessoa:
1. **Adm (Desenvolvedor/Sistema):** Acesso Divino. O único que tem acesso ao painel de geração de códigos, revogação de acessos e configurações estruturais do banco de dados e do próprio robô.
2. **Boss (Gerência / Dono):** Acesso aos cadastros, mas também focado em relatórios comerciais, aprovação final de campanhas e visões estratégicas do negócio.
3. **Marketing:** Focado em ferramentas de promoção, banners, vitrine e criação de copies (textos de venda). Não se envolve com o caixa do quiosque.
4. **Quiosque (Vendedores):** Focado na operação da ponta. Usam o bot para cadastrar caixas novas rapidamente, buscar preço para cliente ou checar estoque. Visão totalmente limpa e sem botões que não competem à venda diária.

## 4. O Modo Testador (Exclusivo Adm) e Integração Backend
O Adm possui um comando nativo chamado **Modo Testador**.
- **Simulação de Hierarquia:** O Adm pode ativar esse modo para assumir temporariamente a identidade de um `Boss`, `Marketing` ou `Quiosque`. Isso serve para testar em tempo real se os botões e regras daquele perfil específico estão funcionando.
- **Cadastro de Produtos Teste (Sandbox):** O ato de cadastrar produtos de teste é uma funcionalidade nativa e essencial do Modo Testador. Ele serve exclusivamente para inserir produtos fictícios que ganham a tag `[TESTE]`. Esses produtos de teste nunca vão para a Vitrine principal, indo cair apenas em uma página de Backend isolada, permitindo ao Adm checar o comportamento do Scraper e do banco de dados sem poluir o estoque real.
- **Botão "Produtos Cadastrados" (Ponte Web):** Através do Modo Testador, o usuário ganha acesso a esse botão que atua como uma "Chave Física" para o Sistema Web. O bot não lista os produtos no Telegram, mas sim gera um **Link Mágico** e criptografado que redireciona o usuário ao painel Backend Web (`/admin`).
- **Fase de Desenvolvimento (Regra de Ouro):** Durante a criação, os botões de ponte Web ("Produtos Cadastrados" e "Estoque") serão construídos e aprimorados **exclusivamente dentro do Modo Testador**. Somente após garantirmos que o fluxo do Telegram para a Web funciona com perfeição e sem furos de segurança, replicaremos esse acesso para os menus reais de Quiosque, Boss e Marketing. O Modo Testador manterá esses botões permanentemente como ambiente seguro (sandbox) para auditorias futuras.

## 5. Botão Personas e Ranking de Uso
- **O Botão Personas:** No menu, há um botão chamado "Personas" que abre uma lista com 10 personalidades baseadas em personagens de franquias famosas (ex: Vegeta, Darth Vader, Deadpool). A persona padrão do sistema é o **"Piticão"**.
- **Comportamento Direto (Zero Papo Furado):** Ao escolher uma persona, a Inteligência Artificial passa a falar no estilo do personagem, MAS sob uma regra inquebrável: ela nunca fica de "papo furado". A IA é focada unicamente em direcionar o usuário para o uso da aplicação, mantendo a produtividade intacta com um tom divertido.
- **Ranking de Personas:** O Ranking não é voltado ao usuário, mas sim ao uso das Personas. Toda vez que uma persona é utilizada pelos usuários, ela ganha um "voto". A persona que receber mais votos fica em primeiro lugar no ranking. O objetivo dessa ferramenta é dar inteligência ao Administrador para ver quais personas a equipe mais usa e quais são ignoradas, permitindo a substituição das menos utilizadas no futuro.

## 6. Fluxo de Operação Principal: Cadastro em Lote (Ex: Funko)
1. **Início:** O usuário (ex: Quiosque) seleciona a categoria "Funko Pop".
2. **Batch (Lote de Imagens):** O usuário pode tirar 10 fotos seguidas de 10 Funkos diferentes e enviar de uma vez.
3. **Processamento em Massa:** O bot entra no modo lote e avisa *"Analisando o lote de produtos"*. A Inteligência Artificial (Gemini Vision) lê embalagem por embalagem, extraindo **Nome, Franquia e Número**.
4. **Acionamento do Scraper:** O bot empurra a lista para background. O Scraper entra em ação e busca as fotos oficiais e preços **exclusivamente no site oficial `funko.com.br`** (Single Source of Truth).
5. **Aviso Final:** O bot descarrega tudo no banco de dados como `PENDENTE` e avisa *"Já cadastrei todos eles"*, retornando o usuário ao menu principal, sem travar o chat do Telegram em nenhum momento.

## 7. Questões em Aberto / Pendências a Resolver
*(Nenhum conflito atual neste documento. Regras 100% estabelecidas e baseadas no escopo integral.)*
