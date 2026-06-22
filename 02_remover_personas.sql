-- Script de migração para remover a funcionalidade de Personas
-- Execute este script no SQL Editor do Supabase.

-- 1. Remover a coluna 'persona' da tabela funcionarios
ALTER TABLE public.funcionarios DROP COLUMN IF EXISTS persona;

-- 2. Deletar a tabela de ranking de personas
DROP TABLE IF EXISTS public.persona_ranking;

-- Migração concluída com sucesso!
