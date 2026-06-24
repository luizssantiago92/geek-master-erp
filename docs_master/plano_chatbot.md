# Plano Chatbot (Telegram) - Bíblia do Sistema

## 1. Objetivo e Função
O Chatbot no Telegram atua como um **Assistente Administrativo (Backoffice)** para a loja física e online. Sua principal função é eliminar o trabalho braçal de cadastro de produtos, gerenciamento de estoque e campanhas, funcionando como o cérebro central de entrada de dados no Supabase.

## 2. Autenticação e Controle de Acesso Restrito
O sistema é inviolável e não permite "cadastro aberto". Todo usuário precisa de um convite para existir.
- **Códigos de Acesso (PTC-):** O administrador gera um código de acesso único atrelado a um nome e um perfil hierárquico (Cargo). Este código possui validade de **30 minutos**.
  - `PTC-` = Código padrão Piticão.
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

---

## 4. Interface do Usuário: Administrador (Admin)

**Nível de Acesso:** Supremo (Nível 4)
**Responsável:** Controle total do bot, desenvolvimento de novas ferramentas e homologação da plataforma.

### Ferramentas Disponíveis no Telegram (Botões Principais)

1. **🛠️ Sistema:**
   - **Descrição:** Painel de controle do sistema do Bot.
   - **Comportamento:** Permite gerenciar configurações globais e funções administrativas essenciais do backend.
   - **Sub-Menus:**
     - `🎟️ Gerar Código`: Cria códigos de acesso (PTC- ou TST-) para novos funcionários ou simulações.
     - `👥 Listar Usuários`: Visualiza quantidade e status de usuários ativos no sistema.
     - `🚫 Revogar Acesso`: Remove permanentemente um usuário.
     - `⏸️ Suspender/Ativar`: Bloqueia/desbloqueia um usuário temporariamente.
     - `📢 Transmissão Global`: Envia um broadcast para todos os funcionários.

2. **🧪 Modo Testador:**
   - **Descrição:** A ferramenta mais crítica para o desenvolvimento do ERP.
   - **Comportamento:** Permite criar perfis fictícios ("usuários de teste") e simular acessos de Nível 1 (Quiosque), Nível 2 (Marketing) e Nível 3 (Boss). Através deste modo, o Administrador testa em sandbox todas as funções que os funcionários terão antes de liberá-las no ambiente de produção. Produtos inseridos via Testador ganham a tag `[TESTE]` e não afetam o estoque oficial.

---

## 5. Interface do Usuário: Modo Testador (Especial Admin)

**Nível de Acesso:** Especial (Acima do Supremo)
**Responsável:** Isolamento de testes de software e validação de novas features.

O Modo Testador não é um "cargo humano", mas sim uma camada de simulação ativada exclusivamente pelo **Admin**. 

### Como é ativado?
Dentro do menu do Nível 4, o Admin clica em `🧪 Modo Testador`. A partir desse momento, todas as interações dele relacionadas a testes são "enjauladas" (Sandbox).

### Comportamento Obrigatório do Sistema neste Modo:

1. **Isolamento de Banco de Dados:**
   - Tudo o que for cadastrado (ex: Estoque Teste) receberá a tag `[TESTE]` no nome.
   - O status do produto é salvo como `PENDENTE`, garantindo que NUNCA apareça no site do cliente final.

2. **Fluxo Livre de Quebras:**
   - Erros que ocorrerem aqui não disparam alarmes severos para os outros níveis. É o ambiente perfeito para simular falhas. Por exemplo, o Botão `Teste de Imagem Fallback` existe aqui para testar bloqueios propositais de Scraper.

3. **Permanência do Modo:**
   - **Regra de Negócio:** O Modo Testador é uma ferramenta **permanente**. Mesmo após a conclusão e entrega total do software, esse modo existirá. Sempre que uma nova função for criada no futuro, ela será implantada **primeiro no Modo Testador** para o Admin validar, antes de liberar os botões para as interfaces de Boss, Marketing ou Quiosque.

### Ferramentas Disponíveis no Telegram (Modo Testador)
- **📦 Estoque Teste:** Simula o envio de foto/cadastro de produto, mas direcionando para tabelas ou nomes simulados (`[TESTE]`). Pode-se Cadastrar ou Limpar produtos de teste.
- **🧪 Testar Usuários:** Permite ao Admin gerar um código da classe `TST-` para simular um onboarding de novos funcionários. Com isso, o Admin pode "encarnar" temporariamente a interface e permissões de Níveis inferiores (ex: Quiosque, Boss) no próprio celular para ver como eles enxergam os menus.
- **🔗 Página de Ajustes Teste:** Gera um link mágico que, na interface Web, permite ver claramente quais produtos são "lixo de teste" para poderem ser apagados a qualquer momento com segurança, sem medo de apagar o estoque real.

---

## 6. Inteligência do Piticão (Quebra da 4ª Parede)
- **O Fim das Personas Fixas:** Não há mais um menu de "Escolha sua Persona".
- **Comportamento Direto (Zero Papo Furado):** A Inteligência Artificial (Gemini) atuará sempre focada em resolver o problema do usuário (produtividade em 1º lugar). Contudo, de forma autônoma e aleatória, o "Piticão" fará inserções lúdicas quebrando a quarta parede, assumindo momentaneamente o estilo de personagens nerds (como Darth Vader, Homem-Aranha, Deadpool) para dar bom dia ou confirmar comandos, sem precisar que o usuário configure nada.

## 7. Fluxo de Operação Principal: Cadastro em Lote (Ex: Funko)
1. **Início:** O usuário (ex: Quiosque) seleciona a categoria "Funko Pop".
2. **Batch (Lote de Imagens):** O usuário pode tirar 10 fotos seguidas de 10 Funkos diferentes e enviar de uma vez.
3. **Processamento em Massa:** O bot entra no modo lote e avisa *"Analisando o lote de produtos"*. A Inteligência Artificial (Gemini Vision) lê embalagem por embalagem, extraindo **Nome, Franquia e Número**.
4. **Acionamento do Clone:** O bot empurra a lista para background. O sistema interno busca as fotos oficiais e preços **exclusivamente no banco de dados clonado** dos sites oficiais (`piticas`, `zonacriativa`, `mocadopop`).
5. **Aviso Final:** O bot descarrega tudo no banco de dados como `PENDENTE` e avisa *"Já cadastrei todos eles"*, retornando o usuário ao menu principal, sem travar o chat do Telegram em nenhum momento.
