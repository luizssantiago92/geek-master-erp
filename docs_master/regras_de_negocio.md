# Regras de Negócio e Restrições do Sistema (Obrigatório)

Este documento dita as leis supremas do projeto Geek Master. A Inteligência Artificial deve **sempre** consultar e obedecer a estas regras antes de tomar decisões estruturais, executar comandos que afetem dados ou alterar lógicas de negócio.

## 1. Regras de Conduta da Inteligência Artificial (Obrigatório)
1. **Intocabilidade da Documentação:** A IA **NÃO PODE** alterar nenhum arquivo `.md` contido na pasta `docs_master` sem antes propor a mudança e solicitar **permissão explícita** do usuário.
2. **Protocolo de Backup Obrigatório:** Antes de modificar qualquer arquivo da `docs_master` (após a permissão do usuário), a IA **DEVE OBRIGATORIAMENTE** fazer um `git commit` da versão atual para garantir um ponto de restauração, informando o usuário sobre o backup.
3. **Execução Pós-Análise:** A IA só aplicará as mudanças propostas nos códigos ou nos textos **APÓS** o usuário analisar cuidadosamente e aceitar as edições.

## 2. Regras do Catálogo e Vendas (Site Frontend)
1. **Natureza do Site:** O site é um **Catálogo Online / Lista de Encomendas**, e não um E-commerce tradicional.
2. **Pagamentos:** **Não existe** checkout online com PIX, Cartão ou Boleto no site. O cliente cria um "carrinho de encomendas" e o pagamento é feito **exclusivamente de forma presencial (Física) no ato da retirada** no quiosque.
3. **Escassez:** Um cliente só pode adicionar ao carrinho no máximo **3 unidades** de cada produto.
4. **Regra de Parcelamento Presencial:** 
   - Parcelamento em até **5 vezes sem juros** no cartão de crédito.
   - Valor mínimo da parcela é de **R$ 60,00**. *(Exemplo: Para parcelar em 2x, a compra mínima deve ser de R$ 120,00).*

## 3. Regras de Privacidade e Imagem
1. **Restrição de Nomes:** A IA está estritamente proibida de mencionar nomes de marcas corporativas reais (como a dona da franquia que abriga o quiosque) ou nomes próprios de funcionários nos documentos, logs públicos ou interfaces de clientes. Tudo deve ser tratado como "Geek Master" ou termos genéricos.

## 4. Regras do Chatbot Telegram
1. **Comportamento das Personas:** A IA incorporando as personas (ex: Piticão, Darth Vader) **nunca pode ficar de papo furado**. O tom deve ser temático/divertido, porém estritamente focado e direto ao ponto para direcionar o usuário à ferramenta do ERP corporativo.
2. **Zero-Trust (Sem Conta Aberta):** O bot não aceita cadastros soltos. Todos os usuários precisam de um "Código de Acesso" gerado por um Administrador para vincular o Telegram ID ao banco de dados.

## 5. Regras do Backend (Página de Ajuste de Catálogo)
1. **Autenticação "Telegram Only":** A página de ajustes (antigo Admin) não aceita e-mail e senha. A única porta de entrada é um Link Mágico temporário (JWT) injetado através dos botões no Bot do Telegram.
2. **Sistema de Aprovação (Solicitar Publicação):** 
   - Usuários como Boss e Marketing poderão acessar a página web e editar informações dos produtos, mas eles **NÃO** terão o botão "Publicar".
   - Eles terão um botão chamado **"Solicitar Publicação"**.
   - Ao clicar, o Bot no Telegram enviará uma notificação ao Administrador dizendo que um usuário (identificado pelo ID) solicitou a publicação de um item.
   - O Administrador poderá conferir o catálogo, e, estando tudo certo, ele mesmo clicará em "Publicar", alterando o status do produto.

## 6. Fluxo de Caixa e Reposição (Interface Quiosque)
1. **Dinâmica de Botões do Quiosque:**
   - **Estoque (Entrada):** Serve exclusivamente para o Vendedor cadastrar/dar entrada em novos produtos que chegaram.
   - **Venda (Saída):** Funciona para dar "baixa" no sistema. O Vendedor tira uma foto do produto vendido (ex: caneca) para registrar a saída.
   - **Reposição:** Uma lista gerada a partir das "Vendas (Saídas)" do dia/período. Essa lista será compartilhada com o gestor para guiar a reposição do estoque físico daquele quiosque.

## 7. Princípio do Documento Vazio (Just-in-Time)
1. **Evitar Poluição de Informação:** Para garantir foco, arquivos de documentação para interfaces de usuários secundários (Ex: `Interface_Boss.md`, `Interface_Marketing.md` e `Interface_Quiosque.md`) deverão permanecer **completamente vazios** até o momento exato em que suas respectivas interfaces (botões e lógicas de código) comecem a ser efetivamente programadas.
