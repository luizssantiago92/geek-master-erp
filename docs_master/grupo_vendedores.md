# Grupo de Vendas (Telegram) - Especificações

## Objetivo
Criar um ambiente gamificado e organizado em um grupo do Telegram focado exclusivamente nos vendedores (Nível 2). O objetivo é registrar vendas diárias, acompanhar metas e distribuir pontos, estimulando a equipe através de um ranking transparente. O bot "Piticão" fará a leitura automática de hashtags (comandos) dentro deste grupo.

## 1. Níveis de Acesso (Nova Estrutura)
Para suportar o Vendedor individual, a hierarquia de usuários será atualizada:
1. **Quiosque** (Equipamento físico/Gerente - Concentra as vendas e o estoque da unidade)
2. **Vendedor** (Usuário pessoa física que pertence a um Quiosque)
3. **Marketing**
4. **Boss**
5. **Administrador**

### Vinculação Vendedor -> Quiosque
Durante a geração do Código de Acesso do Vendedor (Nível 2) no "Controle de Sistema", o fluxo será:
1. Admin solicita gerar acesso para Vendedor.
2. Bot pergunta: "Qual o nome do Vendedor?"
3. Bot lista todos os Quiosques ativos (Nível 1) e pergunta: "A qual Quiosque este vendedor pertence?"
4. O Admin seleciona o botão do Quiosque.
5. O código é gerado. Ao ser utilizado, o Vendedor será cadastrado no banco vinculado ao `quiosque_id` escolhido. Na lista de usuários ativos, ele aparecerá como `[Nome] (Vendedor)`.

## 2. Comandos no Grupo (Hashtags)
O bot ficará "ouvindo" as mensagens no grupo em busca de hashtags específicas para computar os dados:

### Para os Vendedores (Nível 2)
*   **`#vendas R$ [valor]`**: Registra a venda individual do dia. O bot entende variações como `#venda`, `R$`, `,00`, etc.
    *   *Ação do Bot:* Soma o valor nas vendas diárias do Vendedor e também nas vendas totais do Quiosque ao qual ele pertence.
    *   *Gamificação:* A cada R$ 10.000,00 vendidos, o Vendedor ganha 100 pontos.

### Para Administradores / Boss / Quiosque (Níveis 1, 4 e 5)
Apenas usuários com permissões gerenciais podem utilizar as seguintes hashtags:
*   **`#metadoria R$ [valor]`**: Define a meta de vendas para o dia atual.
*   **`#metadomes R$ [valor]`**: Define a meta total do mês.
*   **`#vendadoquiosquedia R$ [valor], [DD/MM]`**: Lança o valor total de vendas do quiosque em uma data específica de forma retroativa (útil para tapar buracos de vendedores que não usaram o grupo ou falhas no sistema).

## 3. Fluxo de Edição de Mensagens e Correção
Caso um vendedor digite o valor errado (ex: `#vendas 5000` em vez de `500`), ele poderá simplesmente editar a mensagem diretamente no Telegram. O bot Piticão será programado para escutar edições de mensagens (`edited_message`), recalculando e corrigindo o valor no banco de dados automaticamente.

## 4. Novas Tabelas (Supabase)
Serão necessárias as seguintes tabelas no banco de dados para suportar a funcionalidade:
*   **`vendas_diarias`**: Registra cada lançamento de venda (ID do vendedor, ID do quiosque, valor, data do lançamento).
*   **`metas`**: Registra as metas diárias e mensais estipuladas.
*   **`pontos_vendedores`**: Consolida os pontos que cada vendedor acumula com suas vendas (100 pontos a cada 10k).

## 5. Próximos Passos (Integração Futura)
No próximo mês, as informações de vendas e metas que hoje serão imputadas via grupo poderão ser consultadas ou extraídas através da integração com o número central do WhatsApp Business da empresa. Todos os registros estarão unificados no Supabase, facilitando o desenvolvimento de um Dashboard Web (Painel de Ajustes) para visualização das métricas.
