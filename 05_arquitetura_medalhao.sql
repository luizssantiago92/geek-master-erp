-- ==============================================================================
-- 5. MASTER GEEK - ARQUITETURA MEDALHÃO (GOLD / SILVER)
-- ==============================================================================

-- 1. Adicionar colunas de Medalhão nas tabelas existentes
ALTER TABLE public.funcionarios ADD COLUMN medalhao VARCHAR(10);
ALTER TABLE public.codigos_acesso ADD COLUMN medalhao VARCHAR(10);

-- O Master Admin criado inicialmente sempre será Gold
UPDATE public.funcionarios SET medalhao = 'Gold' WHERE nivel_acesso = 4 AND medalhao IS NULL;

-- 2. Tabela de Autorizações Condicionais (Cartório de Delegação)
CREATE TABLE public.autorizacoes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    solicitante_id UUID REFERENCES public.funcionarios(id) ON DELETE CASCADE NOT NULL,
    acao_alvo VARCHAR(255) NOT NULL, -- Ex: 'gerar_codigo_1', 'revogar_acesso', ou 'ALL'
    status VARCHAR(50) DEFAULT 'PENDENTE', -- 'PENDENTE', 'AUTORIZADO_UNICA', 'AUTORIZADO_DIA', 'AUTORIZADO_LIVRE', 'NEGADO'
    autorizador_id UUID REFERENCES public.funcionarios(id) ON DELETE SET NULL, -- Quem aprovou
    expira_em TIMESTAMPTZ, -- Nulo para Livre ou Única, setado para fim do dia em 'AUTORIZADO_DIA'
    criado_em TIMESTAMPTZ DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ DEFAULT NOW()
);

-- Habilitar RLS
ALTER TABLE public.autorizacoes ENABLE ROW LEVEL SECURITY;

-- Políticas
CREATE POLICY "Funcionários podem ler autorizações"
ON public.autorizacoes FOR SELECT
USING (public.is_funcionario());

CREATE POLICY "Funcionários podem criar autorizações"
ON public.autorizacoes FOR INSERT
WITH CHECK (public.is_funcionario());

CREATE POLICY "Apenas Gold pode atualizar autorizações"
ON public.autorizacoes FOR UPDATE
USING (
    EXISTS (
        SELECT 1 FROM public.funcionarios
        WHERE id = auth.uid() AND medalhao = 'Gold'
    )
);
