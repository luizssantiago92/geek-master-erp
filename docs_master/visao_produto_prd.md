# Geek Master - Product Requirements Document (PRD)

## 1. Visão Geral
Sistema de gestão O2O, automação de relatórios e CRM para quiosque de varejo físico. O foco é capturar dados do cliente através de um Catálogo Web Dinâmico e finalizar o ciclo de venda no ambiente físico, monitorado pelo bot "Piticão" no Telegram.

## 2. Níveis de Acesso (RBAC)
- **Nível 1 (Quiosque):** Vendedores. Permissão para registrar saída de estoque e consultar produtos via bot.
- **Nível 2 (Marketing):** Focado em ferramentas de promoção, banners, vitrine e criação de cópias. (Disparos via WhatsApp previstos para fase futura).
- **Nível 3 (Chefia):** Gerente 1, Gerente 2, Gerente 3. Acesso a aprovação de pedidos e dashboards executivos.
- **Nível 4 (ADM):** Administrador Master. Controle de sistema, manutenção, logs, testes sandbox e gestão de usuários.

## 3. Fluxo de Catálogo e Encomendas (O MVP)
- **Cadastro Progressivo:** Login inicial na plataforma Web. Captura posterior de CPF, Endereço e Preferências Pessoais apenas no momento de fechar a encomenda.
- **Motor de Notificação:** Pedidos geram alerta imediato no Telegram da Chefia para aprovação.
- **Fechamento de Ciclo Flexível:** A encomenda é fechada no balcão físico. O vendedor dá baixa no sistema, permitindo upsell ou remoção de itens na hora da compra física de forma integrada ao pedido online.
- **Lista de Desejos:** Clientes podem favoritar itens na plataforma online.

## 4. Atualização de Estoque (Assíncrona)
O fluxo de atualização se baseia em uma estratégia de **Clonagem de Catálogos** (Piticas, Zona Criativa e Moça do Pop). O catálogo web refletirá essa fonte da verdade (Single Source of Truth), e o vendedor fará os cadastros e associações sem travar o atendimento local.
