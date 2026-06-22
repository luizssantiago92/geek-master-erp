# Plano Site Catálogo Backend (Página de Ajuste de Catálogo)

## 1. Objetivo e Função
A parte Oculta do Site (antiga Rota `/admin`) agora é formalmente a **Página de Ajuste de Catálogo**. Ela funciona como o "purgatório" entre o trabalho automático do Robô (Telegram) e a Vitrine Pública. É nela que os produtos que entraram no estoque são ajustados, corrigidos e validados antes de ficarem visíveis para os clientes finais fazerem encomendas.

## 2. Autenticação e Segurança (Telegram Auth Exclusivo)
O sistema não possui tela clássica de Login (e-mail/senha) para a área administrativa.
- **Acesso Bloqueado:** A página oculta não pode ser acessada digitando a URL no navegador. Se tentarem, recebem tela de Acesso Negado (HTTP 403).
- **A Chave é o Celular (Telegram):** O único jeito de entrar no painel de edição é usando os botões ("Produtos Cadastrados" / "Estoque") dentro do Bot do Telegram, que injetam um Link Mágico (Magic Link temporário/JWT).
- **Controle Total:** Se um funcionário for demitido, o Adm exclui o Telegram dele no banco. O funcionário perde instantaneamente a habilidade de gerar os links mágicos e, consequentemente, não consegue mais acessar a página de nenhum computador.

## 3. Funcionamento e Etapas (Curadoria com Autorização)

1. **Acesso Colaborativo:** Qualquer funcionário autorizado que usar o Link Mágico do Telegram pode entrar na página de Ajuste de Catálogo.
2. **Revisão da Fila:** Eles visualizam os itens recém-cadastrados pelo robô (em amarelo, com a tag `PENDENTE`).
3. **Edição Preparatória:** O funcionário pode arrumar o texto do scraper, corrigir um preço ou subir a foto correta se o bot não conseguiu extrair (Módulo de Ajuste).
4. **O Gargalo da Autorização (Publicação Exclusiva):**
   - Os funcionários podem **"Salvar Ajustes"** à vontade para deixar o cadastro perfeito.
   - Porém, a alteração de status para `PUBLICADO` (o botão "Enviar para o Site") é **Exclusiva do Nível Administrador**.
   - Assim, os funcionários preparam o terreno, mas somente o Admin tem o poder de fazer a revisão final e apertar o botão que empurra o produto ajustado para a tela dos clientes.
5. **Prevenção de Quebras Visuais:** Se por alguma falha o robô scraper não conseguiu a imagem oficial, a interface exibe um bloco "Sem Foto", garantindo a elegância visual do painel enquanto o funcionário não sobe a imagem manual.

## 4. Questões em Aberto / Pendências a Resolver
*(Nenhuma pendência estrutural. A regra de publicação exclusiva do Administrador resolve as questões de hierarquia web sem sobrecarregar os gestores).*
