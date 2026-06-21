# Plano Site Catálogo Backend (Área Administrativa)

## 1. Objetivo e Função
A parte Backend do Site (Rota `/admin`) é o Painel de Aprovação e Curadoria. Ele existe para ser o ponto de controle humano entre o trabalho automático que o Robô (Telegram) faz e o que o cliente final vê na internet.

## 2. Tipos de Usuário e Autenticação
- **Administrador (Master / Dono):** Acesso irrestrito a todas as páginas do sistema administrativo. 
- **Pessoal Autorizado (Vendedores/Staff):** O acesso à rota `/admin` será bloqueado por um sistema de login ou proteção de rota. Visitantes normais que tentarem acessar a URL serão barrados. O nível de permissão ditará o que cada um pode fazer (a ser estruturado via perfis de Auth no Supabase).

## 3. Funcionamento e Etapas (Curadoria de Produtos)

1. **Acesso Protegido:** O funcionário logado entra na área `/admin`.
2. **Revisão da Fila:** Ele visualiza o banco de dados inteiro em formato de cards de produtos. Os itens mais recentes (cadastrados pelo robô) aparecem destacados em amarelo com a tag `PENDENTE`.
3. **Edição e Correção:** O admin revisa se a foto capturada pelo scraper está correta. Pode ajustar o nome, editar o preço manualmente e definir se o produto recebe o selo "É Lançamento?".
4. **Módulo de Ações em Massa:**
   - Através de caixas de seleção, o admin pode marcar vários produtos (Lote).
   - Botões superiores: "Salvar Selecionados" salva todas as edições textuais simultaneamente.
   - Botão **"Enviar Selecionados para Site"**: Altera o `status_publicacao` dos itens para `PUBLICADO`, tornando-os instantaneamente visíveis na Vitrine Pública.
5. **Prevenção de Quebras Visuais:** Se por alguma falha de conexão o robô scraper não conseguiu a imagem oficial, a interface de aprovação mostra um bloco "Sem Foto", garantindo a elegância visual do painel.

## 4. Questões em Aberto / Pendências a Resolver
- **Integração do Auth:** Ainda precisamos plugar a validação do Supabase Auth na rota `/admin` do React para bloquear acesso de quem tentar entrar digitando a URL diretamente.
- **Níveis de Acesso:** Vendedores de quiosque terão acesso ao Painel Admin na web, ou o painel web será exclusivamente do Dono/Gerente e o vendedor fará tudo só pelo bot do Telegram?
