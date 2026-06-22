# Interface do Usuário: Administrador (Admin)

**Nível de Acesso:** Supremo
**Responsável:** Controle total do bot e do sistema de catálogo.

## Ferramentas Disponíveis no Telegram (Botões Principais)

1. **🛠️ Sistema:**
   - **Descrição:** Painel de controle do sistema do Bot.
   - **Comportamento:** Permite gerenciar configurações globais, forçar reinicializações e acessar o Modo Testador.

2. **📦 Estoque:**
   - **Descrição:** Acesso às ferramentas de inserção de produtos.
   - **Comportamento:** O Admin pode cadastrar produtos diretamente pelo bot (como Funko Pops) sem passar por aprovação de superiores.

3. **📊 Relatórios:**
   - **Descrição:** Visualização de métricas e status do banco de dados.
   - **Comportamento:** Gera alertas ou resumos diários de acessos e produtos inseridos.

4. **⚙️ Configurações:**
   - **Descrição:** Ajuste fino de dados.
   - **Comportamento:** Permite alterar credenciais ou chaves de API (quando suportado via bot).

5. **Gerar Link de Acesso (Catálogo Web):**
   - **Descrição:** Botão para logar na "Página de Ajuste de Catálogo".
   - **Comportamento:** O bot gera um "Magic Link" (JWT) de uso único e temporário que permite ao Admin entrar na interface Web.

## Permissões na "Página de Ajustes de Catálogo" (Backend Web)
- **Visualizar:** Todos os produtos e categorias.
- **Editar:** Fotos, textos, descrições e categorias.
- **Deletar:** Qualquer produto do banco de dados.
- **Privilégio Exclusivo (Ação de Publicação):** O Admin é o ÚNICO usuário que possui o botão de mudar o status de um produto de `PENDENTE` para `PUBLICADO`. Somente ele decide o que vai ao ar no site público (Catálogo do Cliente).
