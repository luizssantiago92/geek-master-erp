# Plano Site Catálogo (React Web App)

## 1. Objetivo e Função
O site possui uma dupla função central:
1. **Vitrine Pública (E-commerce/Catálogo):** É o portal onde os clientes finais visualizarão os produtos disponíveis na loja, com os devidos selos de lançamentos, recomendações e preços.
2. **Painel Administrativo (Aprovação):** É o portal de uso interno onde o lojista revisará e aprovará o que o Bot cadastrou.

## 2. Tipos de Usuário
- **Cliente / Visitante:** Acessa a Home e as Páginas de Produtos. Apenas visualiza produtos que foram aprovados pelo administrador.
- **Administrador:** Acessa a rota oculta `/admin`. Vê o banco de dados inteiro (pendentes e publicados) e faz a curadoria.

## 3. Funcionamento e Etapas (Painel Admin)

1. **Revisão:** O lojista acessa o painel Admin e visualiza uma lista em formato de cards. Os produtos cadastrados recentemente pelo robô aparecem com uma borda amarela e a tag `PENDENTE`.
2. **Edição Rápida:** Em cada card, o lojista pode editar o nome, ajustar o preço puxado da internet, alterar a descrição ou marcar a caixinha "É Lançamento?".
3. **Aprovação Individual ou em Lote:**
   - **Massa/Lote:** No canto superior do card, o lojista marca os checkboxes dos produtos que deseja aprovar simultaneamente. Na barra superior da tela, botões permitem "Salvar Selecionados" (salva edições textuais) e "Enviar Selecionados para Site" (muda o status de todos eles de uma vez).
   - **Individual:** Pode clicar no botão de salvar ou enviar individualmente no rodapé do próprio card do produto.
4. **Segurança de Interface:** Se a URL da imagem de algum produto estiver inacessível, o site exibirá um bloco neutro escrito "Sem Foto", garantindo que o design nunca quebre com ícones nativos de erro do navegador.

## 4. Funcionamento da Vitrine (Cliente)
- **Bloqueio Padrão:** A aplicação React filtra os dados vindos do Supabase. Todo produto cujo `status_publicacao` seja `PENDENTE` é sumariamente ignorado. O mesmo ocorre para produtos cujo nome inicie com a tag `[TESTE]`.
- **Exibição:** Produtos com `status_publicacao = 'PUBLICADO'` vão para a grade da Home.

## 5. Questões em Aberto / Pendências a Resolver
- **Checkout / Reserva:** Como funcionará o ato da compra? Os clientes realizarão checkout no próprio site, ou o site terá um botão "Comprar via WhatsApp" (Catálogo Digital)? Essa definição impactará a criação do Checkout ou a ponte direta com o WhatsApp.
- **Seções Dinâmicas:** Adicionar seções como "Recomendações" baseadas no carrinho do cliente.
