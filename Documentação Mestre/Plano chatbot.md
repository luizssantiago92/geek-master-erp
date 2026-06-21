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

## 4. O Modo Testador (Exclusivo Adm)
O Adm possui um comando nativo chamado **Modo Testador**.
- **Simulação de Personas:** O Adm pode ativar esse modo para assumir temporariamente a identidade de um `Boss`, `Marketing` ou `Quiosque`. Isso serve para testar em tempo real se os botões e regras daquele perfil específico estão funcionando, antes de liberar a versão final para a equipe.
- **Produtos Isolados (Sandbox):** Qualquer produto cadastrado com o Modo Testador ativado é marcado internamente como `[TESTE]`. Esses produtos nunca vão para a Vitrine principal, indo cair exclusivamente em uma página de Backend isolada, onde o Adm checa se o Scraper e os dados entraram corretamente no banco.

## 5. Personas da IA e Ranking (Gamificação)
- **Personas (Stealth):** O bot não tem a mesma "personalidade" com todo mundo. A Inteligência Artificial ajusta seu tom (mais sério com o Boss, mais animado ou dinâmico com o Quiosque), criando uma experiência conversacional direcionada.
- **Sistema de Ranking:** Existe uma camada de gamificação interna. Funcionários ganham XP ou sobem em um ranking baseado em interações e cadastros efetuados.

## 6. Fluxo de Operação Principal: Cadastro em Lote (Ex: Funko)
1. **Início:** O usuário (ex: Quiosque) seleciona a categoria "Funko Pop".
2. **Batch (Lote de Imagens):** O usuário pode tirar 10 fotos seguidas de 10 Funkos diferentes e enviar de uma vez.
3. **Processamento em Massa:** O bot entra no modo lote e avisa *"Analisando o lote de produtos"*. A Inteligência Artificial (Gemini Vision) lê embalagem por embalagem, extraindo **Nome, Franquia e Número**.
4. **Acionamento do Scraper:** O bot empurra a lista para background. O Scraper entra em ação e busca as fotos oficiais e preços **exclusivamente no site oficial `funko.com.br`** (Single Source of Truth).
5. **Aviso Final:** O bot descarrega tudo no banco de dados como `PENDENTE` e avisa *"Já cadastrei todos eles"*, retornando o usuário ao menu principal, sem travar o chat do Telegram em nenhum momento.

## 7. Questões em Aberto / Pendências a Resolver
*(Nenhum conflito atual neste documento. Regras 100% estabelecidas e baseadas no escopo integral.)*
