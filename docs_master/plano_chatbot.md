# Plano Chatbot (Telegram) - Bíblia do Sistema

## 1. Objetivo e Função
O Chatbot no Telegram atua como um **Assistente Administrativo (Backoffice)** para a loja física e online. Sua principal função é eliminar o trabalho braçal de cadastro de produtos, gerenciamento de estoque e campanhas, funcionando como o cérebro central de entrada de dados no Supabase.

## 2. Autenticação e Controle de Acesso Restrito
O sistema é inviolável e não permite "cadastro aberto". Todo usuário precisa de um convite para existir.
- **Códigos de Acesso (PTC- / TST-):** O administrador gera um código de acesso único atrelado a um nome e um perfil hierárquico (Cargo). Este código possui validade de **30 minutos**.
  - `PTC-` = Código padrão Piticão.
  - `TST-` = Código de usuário de teste (Sandbox).
- **Entrada Manual ou QRCode:** O usuário novato entra no Telegram e pode se autenticar de duas formas:
  - Digitando `/start [CÓDIGO]`.
  - Escaneando um **QR Code** com a câmera do celular (que redireciona para o bot já passando o código como parâmetro), ou enviando a imagem do QR Code para o próprio Piticão efetuar a leitura através de Visão Computacional.
- **Bypass do Administrador (.env):** O Administrador Master não precisa gerar um código no banco de dados para si. Ele se autentica utilizando uma "senha mestra invisível" (armazenada na variável `MASTER_ADMIN_CODE` no `.env`). Ao digitar `/start [SENHA]`, o bot imediatamente apaga a mensagem (para não deixar rastro no histórico) e confere o Nível 4 Supremo ao usuário.
- **Gerenciamento de Vínculos:** O Administrador tem poder absoluto sobre quem está no sistema:
  - Pode **Desativar/Ativar** temporariamente o acesso de um funcionário sem deletar seus dados históricos.
  - Pode **Revogar (Deletar)** permanentemente um Telegram ID do banco.

## 3. Os 4 Perfis de Usuário (Hierarquia)
O bot exibe menus diferentes dependendo do cargo da pessoa:
1. **Adm (Desenvolvedor/Sistema):** Acesso Divino. O único que tem acesso ao Modo Testador e a Sistema.
2. **Boss (Gerência / Dono):** Acesso aos cadastros, relatórios comerciais e aprovação final.
3. **Marketing:** Focado em ferramentas de promoção, banners, vitrine e criação de copies.
4. **Quiosque (Vendedores):** Focado na operação da ponta. 

## 4. O Modo Testador (Exclusivo Adm) e Integração Backend
O Adm possui um comando nativo chamado **Modo Testador**.
- **Simulação de Hierarquia:** O Adm pode ativar esse modo para assumir temporariamente a identidade de um `Boss`, `Marketing` ou `Quiosque`. Isso serve para testar em tempo real se os botões e regras daquele perfil específico estão funcionando.
- **Cadastro de Produtos Teste (Sandbox):** O ato de cadastrar produtos de teste é uma funcionalidade nativa e essencial do Modo Testador. Ele serve exclusivamente para inserir produtos fictícios que ganham a tag `[TESTE]`. Esses produtos de teste nunca vão para a Vitrine principal, indo cair apenas em uma página de Backend isolada.
- **Fase de Desenvolvimento (Regra de Ouro):** Durante a criação, os botões das interfaces de níveis inferiores (Quiosque, Boss, Marketing) serão construídos e aprimorados **exclusivamente testando via Modo Testador**. O Modo Testador manterá esses botões permanentemente como ambiente seguro (sandbox) para auditorias futuras.

## 5. Inteligência do Piticão (Quebra da 4ª Parede)
- **O Fim das Personas Fixas:** Não há mais um menu de "Escolha sua Persona".
- **Comportamento Direto (Zero Papo Furado):** A Inteligência Artificial (Gemini) atuará sempre focada em resolver o problema do usuário (produtividade em 1º lugar). Contudo, de forma autônoma e aleatória, o "Piticão" fará inserções lúdicas quebrando a quarta parede, assumindo momentaneamente o estilo de personagens nerds (como Darth Vader, Homem-Aranha, Deadpool) para dar bom dia ou confirmar comandos, sem precisar que o usuário configure nada.

## 6. Fluxo de Operação Principal: Cadastro em Lote (Ex: Funko)
1. **Início:** O usuário (ex: Quiosque) seleciona a categoria "Funko Pop".
2. **Batch (Lote de Imagens):** O usuário pode tirar 10 fotos seguidas de 10 Funkos diferentes e enviar de uma vez.
3. **Processamento em Massa:** O bot entra no modo lote e avisa *"Analisando o lote de produtos"*. A Inteligência Artificial (Gemini Vision) lê embalagem por embalagem, extraindo **Nome, Franquia e Número**.
4. **Acionamento do Clone:** O bot empurra a lista para background. O sistema interno busca as fotos oficiais e preços **exclusivamente no banco de dados clonado** dos sites oficiais (`piticas`, `zonacriativa`, `mocadopop`).
5. **Aviso Final:** O bot descarrega tudo no banco de dados como `PENDENTE` e avisa *"Já cadastrei todos eles"*, retornando o usuário ao menu principal, sem travar o chat do Telegram em nenhum momento.
