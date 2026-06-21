-- Adiciona a coluna 'ativo' à tabela 'funcionarios'
-- O valor padrão é TRUE, para que todos os usuários já existentes continuem com acesso.
ALTER TABLE funcionarios ADD COLUMN ativo BOOLEAN DEFAULT TRUE;
