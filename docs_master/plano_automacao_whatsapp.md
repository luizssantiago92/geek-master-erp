# Plano Futuro: Automação WhatsApp

Este documento armazena o planejamento futuro para a integração do sistema com o WhatsApp, focado principalmente nas ações do **Nível 2 (Marketing)** e no motor de notificações.

## 1. Visão Geral
No futuro, o ERP integrará com APIs do WhatsApp para automatizar a comunicação com o cliente e gerir comunidades VIP.

## 2. Tecnologias Previstas
- **WhatsApp API Oficial:** Para notificações diretas (1:1), como alertas de "pedido pronto para retirada" e envio de códigos de segurança (ex: código de 4 dígitos tipo iFood).
- **API Não-Oficial / WebSockets:** Para gestão de grupos e envio em massa de comunicações para a Comunidade do WhatsApp (ex: disparo de cupons).

## 3. Fluxo de Notificação
- O motor de notificação do sistema enviará um alerta via WhatsApp para o cliente assim que um pedido for aprovado pela Chefia.
- Cupons e campanhas poderão ser disparados através do número central do sistema (Piticão).

> **Status:** Em planejamento. Esta funcionalidade será implementada em uma etapa futura (Fase 2 ou 3) do projeto.
