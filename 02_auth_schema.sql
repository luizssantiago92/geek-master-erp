-- ==============================================================================
-- 2. MASTER GEEK - TABELA DE CÓDIGOS DE ACESSO (ZERO TRUST)
-- ==============================================================================

-- ==========================================
-- Tabela: codigos_acesso (Domínio de Identidade/Segurança)
-- ==========================================
CREATE TABLE public.codigos_acesso (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    codigo VARCHAR(255) UNIQUE NOT NULL,
    nivel_acesso INTEGER CHECK (nivel_acesso >= 1 AND nivel_acesso <= 4) NOT NULL,
    usado BOOLEAN DEFAULT FALSE,
    -- Opcional: Relaciona quem gerou o código (Nulo para códigos master)
    criado_por UUID REFERENCES public.funcionarios(id) ON DELETE SET NULL,
    -- Validade do código (Ex: 30 minutos a partir da criação)
    expira_em TIMESTAMPTZ NOT NULL,
    criado_em TIMESTAMPTZ DEFAULT NOW()
);

-- Habilitar RLS OBRIGATÓRIO
ALTER TABLE public.codigos_acesso ENABLE ROW LEVEL SECURITY;

-- ==========================================
-- POLÍTICAS DE SEGURANÇA (RLS - Row Level Security)
-- ==========================================

-- Funcionários (apenas ADMs ou Chefia) podem consultar códigos para gestão
CREATE POLICY "Funcionários podem ler códigos de acesso"
ON public.codigos_acesso FOR SELECT
USING (public.is_funcionario());

-- Apenas funcionários logados podem gerar novos códigos
CREATE POLICY "Apenas funcionários podem criar códigos"
ON public.codigos_acesso FOR INSERT
WITH CHECK (public.is_funcionario());

-- Nota: A validação e marcação do código como "usado" na hora de registrar
-- um novo funcionário pelo Telegram será feita utilizando o Service Role Key
-- do Supabase (ignora RLS), já que o usuário ainda não está autenticado quando usa o código.
