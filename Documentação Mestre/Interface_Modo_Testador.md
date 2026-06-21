# Interface do Usuário: Modo Testador (Especial Admin)

**Nível de Acesso:** Especial (Acima do Supremo)
**Responsável:** Isolamento de testes de software e validação de novas features.

O Modo Testador não é um "cargo humano", mas sim uma camada de simulação ativada exclusivamente pelo **Admin**. 

## Como é ativado?
Dentro do menu `🛠️ Sistema`, o Admin clica em `Ativar Modo Testador`. A partir desse momento, todas as interações dele com o bot são "enjauladas" (Sandbox).

## Comportamento Obrigatório do Sistema neste Modo:

1. **Isolamento de Banco de Dados:**
   - Tudo o que for cadastrado (ex: Estoque Teste) receberá a tag `[TESTE]` no nome.
   - O status do produto é salvo como `PENDENTE`, garantindo que NUNCA apareça no site do cliente final.

2. **Fluxo Livre de Quebras:**
   - Erros que ocorrerem aqui não disparam alarmes severos para os outros níveis. É o ambiente perfeito para simular falhas. Por exemplo, o Botão `Teste de Imagem Fallback` existe aqui para testar bloqueios propositais de Scraper.

3. **Permanência do Modo:**
   - **Regra de Negócio:** O Modo Testador é uma ferramenta **permanente**. Mesmo após a conclusão e entrega total do software, esse modo existirá. Sempre que uma nova função for criada no futuro, ela será implantada **primeiro no Modo Testador** para o Admin validar, antes de liberar os botões para as interfaces de Boss, Marketing ou Quiosque.

## Ferramentas Disponíveis no Telegram (Modo Testador)
- **📦 Estoque Teste:** Simula o envio de foto/cadastro de produto, mas direcionando para tabelas ou nomes simulados (`[TESTE]`).
- **🔗 Página de Ajustes Teste:** Gera um link mágico que, na interface Web, permite ver claramente quais produtos são "lixo de teste" para poderem ser apagados a qualquer momento com segurança, sem medo de apagar o estoque real.
