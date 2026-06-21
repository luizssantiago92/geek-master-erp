# Plano Chatbot (Telegram) - Bíblia do Sistema

## 1. Objetivo e Função
O Chatbot no Telegram atua como um **Assistente Administrativo (Backoffice)** para a loja física e online. Sua principal função é eliminar o trabalho braçal de cadastro de produtos, permitindo que a entrada de novos itens no sistema seja rápida, intuitiva e, preferencialmente, feita apenas tirando fotos com o celular. Funciona como a principal interface de inserção de dados no banco (Supabase).

## 2. Autenticação e Primeiros Passos (O comando `/start`)
Como o sistema insere dados reais no banco de dados da loja, ele é estritamente privado.
- **Primeiro Acesso:** Quando uma pessoa desconhecida manda `/start` para o bot, ele captura o Telegram ID dela. O bot informa que ela não tem acesso e a coloca em uma fila de solicitações.
- **Liberação:** Essa pessoa só consegue usar o bot após um usuário com perfil **Master** aprovar seu acesso.
- **Mensagem de Boas-vindas:** Assim que o acesso é liberado, no próximo comando, o bot saúda o funcionário e exibe o menu principal condizente com seu nível de permissão.

## 3. Tipos de Usuário e Permissões
- **Master (Administrador/Dono):** Acesso total. Pode ver todas as opções de cadastro, gerenciar o sistema inteiro e visualizar botões restritos.
- **Quiosque (Vendedores):** Acesso limitado ao cadastro de produtos. Visão simplificada focada na rotina diária para não sobrecarregar o funcionário. Não pode adicionar outros usuários ou ver relatórios confidenciais.
- **Modo Testador:** Ativado pelo comando explícito `/teste_on` e desativado por `/teste_off`. Útil para testes de desenvolvimento; garante que qualquer produto cadastrado durante esse modo receba a tag `[TESTE]` e seja sumariamente ignorado pelo site público.

## 4. Botões, Menus e Comandos Disponíveis
### Menus Globais
- **Menu Principal:** Oferece as grandes categorias da loja: `Funko Pop`, `Vestuário Geek`, `Acessórios`, `Decoração` e `Colecionáveis`. *(No futuro, cada categoria terá seu próprio fluxo adaptado).*
- **Navegação:** Botão obrigatório de `Voltar ao Menu` (ou comando `/cancel`) em todos os submenus para evitar que o usuário fique preso em um diálogo.
- **Confirmação:** Botões `✅ Sim` e `❌ Não` quando a Inteligência Artificial solicita verificação de dados extraídos.

### Funções Restritas (Somente Master)
- **Gerenciar Acessos:** Permite ver quem tentou entrar no bot, aprovar pendentes ou gerar códigos/links de acesso para novos vendedores do quiosque.

## 5. Funcionamento e Etapas: Cadastro Inteligente em Lote (Exemplo: Funko)

1. **Início do Fluxo:** O usuário seleciona a categoria "Funko Pop".
2. **Entrada de Dados:** O bot avisa que precisa da foto da caixa (Recomendado) OU de 3 dados textuais (Nome, Franquia, Número) enviados separadamente.
3. **Análise de Imagem e Lote (Batch):** 
   - Se o usuário enviar várias fotos de uma vez (ou em rápida sucessão), o bot avisará que está *"analisando o lote de produtos"*. 
   - A Inteligência Artificial (Gemini Vision) lê cada embalagem individualmente e extrai o Nome, a Franquia e o Número.
4. **Confirmação Automática:** A IA estrutura a informação ("BONECO FUNKO POP! [FRANQUIA] - [NOME] #[NUMERO]") e pede confirmação apenas se houver dúvida. Se a leitura for óbvia, ele já coloca na fila de processamento.
5. **Processamento Assíncrono e Scraper:**
   - Em background (para não travar o bot), o módulo Scraper entra em ação para os itens confirmados.
   - **Regra de Ouro do Scraper:** Ele buscará as informações **exclusivamente no site oficial `funko.com.br`**, pois todo o estoque físico da loja está disponível lá.
   - O bot fará o download silencioso da Foto Oficial de Estúdio em alta qualidade, do Preço oficial atualizado e da Descrição, fazendo o upload da imagem diretamente para o Storage do Supabase (para não depender de links de terceiros).
6. **Salvamento Final:** O bot empurra os dados completos para a tabela `produtos` com o status de `PENDENTE`.
7. **Finalização:** Ao terminar a varredura do lote e os downloads do scraper, o bot envia um relatório final avisando que *"já cadastrou todos eles"* e pergunta se o usuário deseja registrar mais alguma coisa, retornando automaticamente para o submenu de categorias.

## 6. Resiliência e Tratamento de Erros
- **Falha da IA:** Se a imagem enviada estiver muito borrada ou a IA não conseguir identificar tratar-se de um Funko, o bot avisará que não encontrou os dados e pedirá para o usuário mandar uma foto melhor ou digitar manualmente.
- **Falha do Scraper:** Caso o produto (raro/antigo) não esteja mais listado no `funko.com.br`, o bot salvará o produto no banco apenas com os dados vitais extraídos pela foto. O produto ficará com um alerta de "Sem Foto" no Painel Admin do site para intervenção manual.

## 7. Questões em Aberto / Pendências a Resolver
*(Nenhum conflito pendente nesta documentação. Regras estabelecidas e prontas para execução em código.)*
