# Master Geek - Product Requirements Document (PRD)

## 1. Visão Geral
Sistema de gestão O2O, automação de relatórios e CRM para quiosque de varejo físico. O foco é capturar dados do cliente através de um Catálogo Web Dinâmico e finalizar o ciclo de venda no ambiente físico, monitorado pelo bot "Piticão" no Telegram.

## 2. Níveis de Acesso (RBAC)
- **Nível 1 (Quiosque):** Vendedores. Permissão para ler QR Code de notas fiscais, registrar saída de estoque via foto e consultar produtos.
- **Nível 2 (Marketing):** Disparo de cupons e gestão da comunidade do WhatsApp.
- **Nível 3 (Chefia):** Gysele, Bruno, Natan. Acesso a aprovação de pedidos e dashboards executivos.
- **Nível 4 (ADM):** Luiz / Equipe. Manutenção, logs e gestão de usuários.

## 3. Fluxo de Catálogo e Encomendas (O MVP)
- **Cadastro Progressivo:** Login inicial social (Google/Email). Captura posterior de CPF, Endereço e Preferências Pessoais (Franquias favoritas como Star Wars, Marvel, etc.) apenas no momento de fechar encomenda.
- **Motor de Notificação:** Pedidos geram alerta imediato no Telegram da Chefia. Após aprovação, envia código de 4 dígitos (ex: iFood) via WhatsApp Oficial do cliente.
- **Fechamento de Ciclo Flexível:** A encomenda é fechada no balcão físico. O vendedor emite a DANFE NFC-e com o CPF do cliente, tira foto do QR Code e envia ao Telegram. O sistema processa o QR Code, extrai o CPF, cruza com a encomenda e dá baixa com os valores reais (permitindo upsell ou remoção de itens na hora da compra).
- **Lista de Desejos e Cupons:** Clientes podem favoritar itens; cupons exclusivos são gerados apenas para membros da comunidade VIP.

## 4. Atualização de Estoque (Assíncrona)
Vendedor tira foto do produto + EAN no balcão. O sistema registra localmente e um job em background raspa dados oficiais (Zona Criativa, Piticas, Funko) para atualizar o catálogo web sem travar o atendimento.