-- ==============================================================================
-- 8. MASTER GEEK - FASE BOT: RANKING DE PERSONAS
-- ==============================================================================

-- Tabela para rastrear quantas vezes cada persona foi selecionada pelos funcionários
CREATE TABLE IF NOT EXISTS public.persona_ranking (
    persona_nome VARCHAR(100) PRIMARY KEY,
    vezes_selecionada INTEGER DEFAULT 0,
    ultima_selecao TIMESTAMPTZ DEFAULT NOW()
);

-- Inserir as 10 personas oficiais com contagem inicial zero (opcional, mas bom para garantir)
INSERT INTO public.persona_ranking (persona_nome, vezes_selecionada) VALUES
    ('Homem-Aranha', 0),
    ('Deadpool', 0),
    ('Batman', 0),
    ('Alfred', 0),
    ('C3PO', 0),
    ('Darth Vader', 0),
    ('Vegeta', 0),
    ('Naruto', 0),
    ('Hermione', 0),
    ('Padrão', 0) -- Piticão
ON CONFLICT (persona_nome) DO NOTHING;
