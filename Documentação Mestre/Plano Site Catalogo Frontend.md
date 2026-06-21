# Plano Site Catálogo Frontend (Público)

## 1. Objetivo e Função
O Frontend do Site não atua como um e-commerce tradicional com vendas diretas online, mas sim como um **Catálogo de Encomendas para Retirada Física**. Sua principal função é exibir os produtos que estão no estoque, incentivar o cliente a criar sua lista e enviar uma solicitação de reserva para buscar no quiosque.

## 2. Tipos de Usuário
- **Visitantes Anônimos:** Clientes que apenas navegam pela vitrine, olham os lançamentos, as opções de parcelamento e preços.
- **Clientes Logados:** Clientes que efetuaram cadastro na plataforma e podem montar o carrinho de encomendas.

## 3. Autenticação e Perfil do Cliente
1. **Login:** Acesso facilitado via botões rápidos (Google e Facebook) ou cadastro padrão por E-mail.
2. **Cadastro Completo Obrigatório:** Para realizar encomendas, o sistema exige um perfil detalhado do cliente para controle de contato e preferências:
   - **Dados Básicos:** Nome Completo, CPF, Data de Nascimento (para verificar idade).
   - **Contato:** Número de telefone e confirmação se o número possui WhatsApp, além do e-mail.
   - **Preferências:** Um campo dedicado para o cliente listar suas franquias e personagens favoritos (ajuda na curadoria futura).

## 4. Navegação e Regras de Negócio na Vitrine
1. **Filtro de Visibilidade:** O site consome os dados do Supabase. Somente produtos com `status_publicacao = 'PUBLICADO'` aparecem. Produtos com a tag `[TESTE]` inseridos pelo robô são sumariamente ocultados.
2. **Edição de Preços:** Os valores visíveis na vitrine são definidos exclusivamente pela equipe interna através do Painel de Backend.
3. **Escassez e Limites:** Devido ao modelo de negócio baseado em itens de coleção e estoques limitados, o site impõe uma trava sistêmica de **máximo de 3 unidades** do mesmo produto por cliente na mesma encomenda.
4. **Regras de Parcelamento (Informativo Visual):** Na página do produto e no carrinho, o site exibe as condições de pagamento que o cliente encontrará lá no balcão físico:
   - Pagamento em até **5x sem juros no Cartão de Crédito**.
   - **Restrição de Parcela Mínima:** O valor de cada parcela não pode ser menor que R$ 60,00. (Ex: para parcelar em 2x, o total da reserva deve ser no mínimo R$ 120,00).

## 5. Carrinho de Encomendas e Finalização
1. **Montagem da Lista:** O cliente adiciona itens à sua lista/carrinho (sujeito à regra de escassez).
2. **Cupons de Desconto:** No carrinho, haverá um campo de cupom. (O sistema lerá uma tabela no banco de dados para checar a validade e abater o valor do total. Estratégia pensada para tracionar a futura comunidade de fãs no WhatsApp).
3. **Seleção de Quiosque:** O cliente escolhe em qual unidade física (Quiosque) ele deseja buscar sua encomenda.
4. **Validação de Cadastro:** Ao clicar em "Enviar Encomenda":
   - Se o cadastro estiver completo: A solicitação é enviada e cai na fila do Backend Administrativo da loja.
   - Se o cadastro estiver incompleto: O fluxo é travado e o usuário é redirecionado para a página de Perfil com um alerta solicitando o preenchimento dos dados (CPF, idade, etc) faltantes.
5. **Pagamento (Presencial):** O site não processa o dinheiro. O cliente consolida seu pedido de forma online, garantindo a reserva, mas passará o cartão ou pagará via Pix pessoalmente no momento da retirada no quiosque.

## 6. Questões em Aberto / Pendências a Resolver
*(Nenhum conflito atual. O fluxo do site foi redesenhado 100% como catálogo de reserva física. Nenhuma funcionalidade de e-commerce real existirá.)*
