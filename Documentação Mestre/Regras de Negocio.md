# Regras de Negócio e Restrições do Sistema (Obrigatório)

Este documento dita as leis supremas do projeto Master Geek. A Inteligência Artificial deve **sempre** consultar e obedecer a estas regras antes de tomar decisões estruturais, executar comandos que afetem dados ou alterar lógicas de negócio.

## 1. Regras de Conduta da Inteligência Artificial (Obrigatório)
1. **Intocabilidade da Documentação:** A IA **NÃO PODE** alterar nenhum arquivo `.md` contido na pasta `Documentação Mestre` sem antes propor a mudança e solicitar **permissão explícita** do usuário.
2. **Protocolo de Backup Obrigatório:** Antes de modificar qualquer arquivo da `Documentação Mestre` (após a permissão do usuário), a IA **DEVE OBRIGATORIAMENTE** fazer um `git commit` da versão atual para garantir um ponto de restauração, informando o usuário sobre o backup.
3. **Execução Pós-Análise:** A IA só aplicará as mudanças propostas nos códigos ou nos textos **APÓS** o usuário analisar cuidadosamente e aceitar as edições.

## 2. Regras do Catálogo e Vendas (Site Frontend)
1. **Natureza do Site:** O site é um **Catálogo Online / Lista de Encomendas**, e não um E-commerce tradicional.
2. **Pagamentos:** **Não existe** checkout online com PIX, Cartão ou Boleto no site. O cliente cria um "carrinho de encomendas" e o pagamento é feito **exclusivamente de forma presencial (Física) no ato da retirada** no quiosque.
3. **Escassez:** Um cliente só pode adicionar ao carrinho no máximo **3 unidades** de cada produto.
4. **Regra de Parcelamento Presencial:** 
   - Parcelamento em até **5 vezes sem juros** no cartão de crédito.
   - Valor mínimo da parcela é de **R$ 60,00**. *(Exemplo: Para parcelar em 2x, a compra mínima deve ser de R$ 120,00).*

## 3. Regras de Privacidade e Imagem
1. **Restrição de Nomes:** A IA está estritamente proibida de mencionar nomes de marcas corporativas reais (como a dona da franquia que abriga o quiosque) ou nomes próprios de funcionários nos documentos, logs públicos ou interfaces de clientes. Tudo deve ser tratado como "Master Geek" ou termos genéricos.

## 4. Regras do Chatbot Telegram
1. **Comportamento das Personas:** A IA incorporando as personas (ex: Piticão, Darth Vader) **nunca pode ficar de papo furado**. O tom deve ser temático/divertido, porém estritamente focado e direto ao ponto para direcionar o usuário à ferramenta do ERP corporativo.
2. **Zero-Trust (Sem Conta Aberta):** O bot não aceita cadastros soltos. Todos os usuários precisam de um "Código de Acesso" gerado por um Administrador para vincular o Telegram ID ao banco de dados.

## 5. Regras do Backend (Página de Ajuste de Catálogo)
1. **Autenticação "Telegram Only":** A página de ajustes (antigo Admin) não aceita e-mail e senha. A única porta de entrada é um Link Mágico temporário (JWT) injetado através dos botões no Bot do Telegram.
2. **Gargalo de Publicação:** Funcionários (Quiosque, Boss, Marketing) podem acessar a página para ajustar fotos, corrigir textos e salvar edições. Porém, o ato de alterar o status para `PUBLICADO` (enviar o produto para o site público) é uma **ação de privilégio exclusivo do Administrador**.
