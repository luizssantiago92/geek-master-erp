# Estratégia de Catálogo: Clonagem de Sites

A estratégia original de realizar *Web Scraping* em tempo real em sites como o da Funko foi oficialmente **descontinuada** por questões técnicas e de bloqueios.

A nova arquitetura oficial para a popularização do banco de dados do **Geek Master** baseia-se na **clonagem estrutural e de catálogo** de 3 sites principais de produtos Geeks:

1. `piticas.com.br`
2. `zonacriativa.com.br`
3. `mocadopop.com.br`

## Como vai funcionar
- A plataforma irá utilizar a base de dados extraída ou clonada destes três sites.
- Todos os produtos disponibilizados no sistema (para Venda, Estoque ou Encomenda) terão como *Single Source of Truth* (Fonte Única de Verdade) o catálogo unificado destas 3 lojas.
- As informações como imagens, nome, franquia e preços-base serão referenciados a partir desse clone para alimentar nosso Supabase de forma estática e estável.
