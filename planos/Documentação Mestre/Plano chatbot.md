# Plano Chatbot (Telegram)

## 1. Objetivo e Função
O Chatbot no Telegram atua como um **Assistente Administrativo (Backoffice)** para a loja física e online. Sua principal função é eliminar o trabalho braçal de cadastro de produtos, permitindo que a entrada de novos itens no sistema seja rápida, preferencialmente feita apenas tirando fotos com o celular.

## 2. Tipos de Usuário e Permissões
- **Master (Administrador):** Acesso total. Pode ver todas as opções, gerenciar o sistema e ver botões restritos.
- **Quiosque (Vendedores):** Acesso limitado ao cadastro de produtos. Visão simplificada para não sobrecarregar o vendedor.
- **Modo Testador:** Ativado pelo comando `/teste_on` e desativado por `/teste_off`. Permite testar cadastros sem sujar o banco de dados principal (os produtos ganham a tag `[TESTE]`).

## 3. Botões e Menus Disponíveis
- **Menu Principal:** Oferece as grandes categorias da loja (ex: `Funko Pop`, `Vestuário Geek`, `Acessórios`, `Decoração`, `Colecionáveis`).
- **Funções Especiais:** `Cadastrar Funcionários` e `Ver Acessos` (visíveis apenas para o perfil Master).
- **Navegação:** Botão obrigatório de `Voltar ao Menu` em todos os submenus para evitar que o usuário fique preso em um fluxo.
- **Confirmação:** Botões `✅ Sim` e `❌ Não` quando a IA solicita verificação de dados extraídos.

## 4. Funcionamento e Etapas (Cadastro Inteligente em Lote - Funko)

1. **Início do Fluxo:** O usuário seleciona "Funko Pop".
2. **Entrada de Dados:** O bot avisa que precisa da foto da caixa OU de 3 dados textuais (Nome, Franquia, Número).
3. **Análise de Lote (Batch):** Se o usuário enviar várias fotos juntas, o bot avisará que está *"analisando o lote de produtos"*. A IA (Gemini Vision) lê cada embalagem individualmente.
4. **Processamento Assíncrono e Scraper:**
   - O bot pega as informações (Nome, Franquia, Número) de cada item do lote e aciona o **Scraper**.
   - O Scraper usará exclusivamente o site oficial **`funko.com.br`** como base confiável de pesquisa, pois todos os itens de quiosque existem lá. Ele baixará a Foto Oficial de Estúdio, Preço e Descrição.
5. **Finalização:** Ao terminar todo o lote, o bot avisa que *"já cadastrou todos eles"* e pergunta se o usuário deseja registrar mais alguma coisa, retornando automaticamente para o submenu de seleção de produtos.

## 5. Próximo Passo Tecnológico (Scraper Real)
A regra de negócios acima foi definida. O próximo passo de programação (já aprovado) é garantir que o Scraper Real utilizando `Playwright` consiga ler corretamente as informações do `funko.com.br` e fazer o upload da imagem real para o banco de dados. Assim que isso for resolvido tecnicamente, a funcionalidade do chatbot estará 100% pronta.


