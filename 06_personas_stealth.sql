-- ==============================================================================
-- 6. MASTER GEEK - GAMIFICAÇÃO E PERSONAS
-- ==============================================================================

-- 1. Adicionar coluna Persona na tabela de funcionários
ALTER TABLE public.funcionarios ADD COLUMN persona VARCHAR(50) DEFAULT 'Padrão';
