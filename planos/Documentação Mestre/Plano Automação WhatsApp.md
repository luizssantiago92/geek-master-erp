# Plano Automação WhatsApp

## 1. Objetivo e Função
O módulo de Automação do WhatsApp (ainda a ser implementado) será o canal de atendimento primário (Linha de Frente) para clientes da loja. Atuará respondendo dúvidas, consultando a disponibilidade de produtos e guiando o cliente.

## 2. Tipos de Usuário
- **Cliente:** Qualquer pessoa que envie uma mensagem para o número de WhatsApp da loja. Interage puramente via texto/áudio com a IA.

## 3. Funcionamento e Etapas (Projeção)

1. **Recepção:** O cliente envia uma mensagem. O sistema intercepta e direciona para uma Inteligência Artificial (LLM).
2. **Integração com o Supabase:** Quando o cliente perguntar "Você tem o Funko do Luffy?", a IA do WhatsApp conectará ao banco de dados `produtos` e lerá APENAS itens com `status_publicacao = 'PUBLICADO'`.
3. **Respostas Estruturadas:** A IA formulará respostas baseadas no que existe em estoque (no banco) e poderá enviar links direcionando o cliente para a página do produto no Site Catálogo.

## 4. Questões em Aberto / Pendências a Resolver
- **Fluxo de Venda Final:** Quando o cliente decide comprar, a automação do WhatsApp finalizará o pedido gerando um link de pagamento/Pix, ou apenas atuará como suporte e direcionará o cliente para o Checkout do Site Catálogo?
- **Gerenciamento de Estoque:** Atualmente não temos coluna de `quantidade_estoque`. Como o bot do WhatsApp saberá se um item esgotou para evitar falsas promessas de venda? Isso exigirá adição de controle de estoque no Painel Administrativo.
- **Transbordo para Humano:** Será necessário definir a regra de quando a IA desiste e chama um vendedor humano.
