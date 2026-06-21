# Plano Chatbot (Telegram)

## 1. Objetivo e Função
O Chatbot no Telegram atua como um **Assistente Administrativo (Backoffice)** para a loja física e online. Sua principal função é eliminar o trabalho braçal de cadastro de produtos, permitindo que a entrada de novos itens no sistema seja rápida, preferencialmente feita apenas tirando fotos com o celular.

## 2. Tipos de Usuário
- **Administrador / Gerente:** O usuário que está gerenciando a loja. Tem acesso total para enviar comandos e cadastrar produtos.

## 3. Botões e Menus Disponíveis
- **Menu Principal:** Oferece as grandes categorias da loja (ex: `Funko Pop`, `Vestuário Geek`, `Acessórios`, `Decoração`, `Colecionáveis`).
- **Navegação:** Botão obrigatório de `Voltar ao Menu` em todos os submenus para evitar que o usuário fique preso em um fluxo.
- **Confirmação:** Botões `✅ Sim` e `❌ Não` quando a IA solicita verificação de dados extraídos.

## 4. Funcionamento e Etapas (Exemplo: Categoria Funko)

1. **Início do Fluxo:** O usuário seleciona "Funko Pop".
2. **Entrada de Dados:** O bot avisa que precisa da foto da caixa OU de 3 dados textuais (Nome, Franquia, Número).
3. **Análise por IA:** O usuário envia a foto. A Inteligência Artificial (Gemini Vision) lê a embalagem e extrai os 3 dados automaticamente.
4. **Confirmação:** O bot devolve a string formatada: `"BONECO FUNKO POP! [FRANQUIA] - [NOME] #[NUMERO]"` e pergunta se está correto.
5. **Processamento Assíncrono:**
   - Se aprovado, o bot envia a mensagem `"Processando..."`.
   - A tela do chat é liberada imediatamente para o usuário tirar a próxima foto (fluxo contínuo).
   - Em background (sem incomodar o usuário), o módulo Scraper busca o produto na internet para achar a **Foto Oficial de Estúdio**, o **Preço** e a **Descrição**.
6. **Salvamento:** O bot empurra os dados completos para o banco de dados Supabase com o status `PENDENTE`.

## 5. Questões em Aberto / Pendências a Resolver
- **Cadastro em Lote (Batch):** Atualmente, se o usuário mandar 3 ou mais funkos, o bot pode "pipocar" notificações na tela quando cada um terminar de processar no background. **Meta:** Implementar uma trava para que, se houver um lote de fotos, o bot fique silencioso e só envie UM aviso final quando houver um período de inatividade (indicando que o usuário terminou o lote).
- **Scraper Real:** A busca de preços/fotos na web (Scraper) atualmente usa dados fictícios simulados (Mock). O próximo passo é ativar o robô Real (Playwright) para baixar e subir as fotos definitivas no Supabase Storage.
