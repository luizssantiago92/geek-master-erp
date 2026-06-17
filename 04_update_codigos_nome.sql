-- Adiciona a coluna 'nome_atribuido' à tabela 'codigos_acesso'
-- Assim, o ADM pode definir o nome do usuário antes dele se cadastrar.
ALTER TABLE codigos_acesso ADD COLUMN nome_atribuido VARCHAR(255);
