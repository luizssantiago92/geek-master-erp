# Interface do Usuário: Administrador (Admin)

**Nível de Acesso:** Supremo (Nível 4)
**Responsável:** Controle total do bot, desenvolvimento de novas ferramentas e homologação da plataforma.

## Acesso Oculto (Bypass)
O Administrador não precisa de um código gerado via banco de dados para entrar no sistema. Ele possui acesso garantido através da senha invisível configurada no servidor (arquivo `.env`).
- **Comando de Entrada:** `/start [SENHA_DO_ENV]`
- **Segurança:** Imediatamente após enviar a senha, o bot apaga a mensagem do chat para que a credencial não fique exposta no histórico do Telegram. O usuário ganha Nível 4 instantaneamente.

## Ferramentas Disponíveis no Telegram (Botões Principais)

1. **⚙️ Sistema:**
   - **Descrição:** Painel de controle do sistema do Bot.
   - **Comportamento:** Permite gerenciar configurações globais e funções administrativas essenciais do backend.

2. **🧑‍💻 Modo Testador:**
   - **Descrição:** A ferramenta mais crítica para o desenvolvimento do ERP.
   - **Comportamento:** Permite criar perfis fictícios ("usuários de teste") e simular acessos de Nível 1 (Quiosque), Nível 2 (Marketing) e Nível 3 (Boss). Através deste modo, o Administrador testa em sandbox todas as funções que os funcionários terão antes de liberá-las no ambiente de produção. Produtos inseridos via Testador ganham a tag `[TESTE]` e não afetam o estoque oficial.
