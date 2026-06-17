# Estrutura de Domínios do Supabase

O agente deve focar na criação das tabelas respeitando a seguinte lógica relacional:

1. **Domínio de Identidade:** `funcionarios` (com níveis de acesso 1 a 4), `clientes` (dados sensíveis, preferências e histórico).
2. **Domínio de Catálogo:** `produtos` (EAN, foto, status de scraping), `lista_desejos` (relacionando clientes e produtos).
3. **Domínio de Transação:** `encomendas` (Status: pendente, aguardando_retirada, concluida_com_divergencia, concluida_integral), vinculadas ao `codigo_retirada`.
4. **Domínio de Marketing:** `cupons_comunidade`, `preferencias_tags`.