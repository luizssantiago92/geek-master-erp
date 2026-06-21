import os
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client
import random
import string

load_dotenv()

URL = os.getenv("SUPABASE_URL")
KEY = os.getenv("SUPABASE_KEY")

if not URL or not KEY:
    raise ValueError("Variáveis SUPABASE_URL ou SUPABASE_KEY não encontradas no .env")

# Cliente Supabase usando a Service Role Key (para ignorar RLS nas checagens primárias)
supabase: Client = create_client(URL, KEY)

def get_funcionario_by_telegram_id(telegram_id: str):
    """Retorna o funcionário se o telegram_id estiver registrado, senão None."""
    try:
        response = supabase.table("funcionarios").select("*").eq("telegram_id", str(telegram_id)).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Erro ao buscar funcionário: {e}")
        return None

def validar_e_usar_codigo(telegram_id: str, telegram_name: str, codigo: str):
    """
    Verifica se o código é válido. Se for, registra o funcionário, 
    marca o código como usado e retorna (True, mensagem).
    Retorna (False, mensagem_erro) se o código for inválido.
    """
    try:
        # 1. Buscar o código no banco
        response = supabase.table("codigos_acesso").select("*").eq("codigo", codigo).eq("usado", False).execute()
        
        if not response.data:
            return False, "❌ Código inválido, já utilizado ou não existe."
        
        codigo_db = response.data[0]
        
        # 2. Verificar expiração
        expira_em_str = codigo_db["expira_em"]
        expira_em = datetime.fromisoformat(expira_em_str.replace("Z", "+00:00"))
        
        if datetime.now(expira_em.tzinfo) > expira_em:
            return False, "❌ Este código de acesso expirou. Solicite um novo ao seu gestor."
            
        nivel = codigo_db["nivel_acesso"]
        
        # 3. Registrar o funcionário
        # Pega o nome customizado se existir, caso contrário usa o do Telegram
        nome_final = codigo_db.get("nome_atribuido")
        if not nome_final:
            nome_final = telegram_name
            
        cargos = {1: "Quiosque (Vendedor)", 2: "Marketing", 3: "Boss", 4: "Administrador"}
        cargo = cargos.get(nivel, "Desconhecido")
        
        novo_funcionario = {
            "telegram_id": str(telegram_id),
            "nome": nome_final,
            "cargo": cargo,
            "nivel_acesso": nivel,
            "ativo": True,
            "medalhao": codigo_db.get("medalhao")
        }
        res_func = supabase.table("funcionarios").insert(novo_funcionario).execute()
        
        # 4. Marcar o código como usado
        supabase.table("codigos_acesso").update({"usado": True}).eq("id", codigo_db["id"]).execute()
        
        return True, f"✅ Cadastro realizado com sucesso!\nVocê foi registrado como: **{nome_final}**\nCargo: **{cargo}**"
    except Exception as e:
        print(f"Erro ao usar código de acesso: {e}")
        return False, "❌ Erro interno ao validar o código."

def validar_codigo_teste(codigo: str):
    """Valida um código de teste sem registrar o funcionário no banco. Apenas consome o código e retorna o nível."""
    try:
        response = supabase.table("codigos_acesso").select("*").eq("codigo", codigo).eq("usado", False).execute()
        
        if not response.data:
            return None # Código não existe ou já usado
            
        codigo_db = response.data[0]
        
        # Verificar se não está expirado
        expira = datetime.fromisoformat(codigo_db["expira_em"].replace("Z", "+00:00"))
        if datetime.now(expira.tzinfo) > expira:
            return None # Código expirado
            
        # Marcar como usado
        supabase.table("codigos_acesso").update({"usado": True}).eq("id", codigo_db["id"]).execute()
        
        return codigo_db["nivel_acesso"]
    except Exception as e:
        print(f"Erro ao validar código de teste: {e}")
        return None

def registrar_master_admin(telegram_id: str, telegram_name: str):
    """Registra o primeiro usuário como ADM (Nível 4)."""
    try:
        novo_funcionario = {
            "telegram_id": str(telegram_id),
            "nome": telegram_name,
            "cargo": "Administrador Master",
            "nivel_acesso": 4,
            "ativo": True,
            "medalhao": "Gold"
        }
        supabase.table("funcionarios").insert(novo_funcionario).execute()
        return True
    except Exception as e:
        print(f"Erro ao registrar master admin: {e}")
        return False

def gerar_novo_codigo(id_criador: str, nivel_acesso: int, nome_atribuido: str = None, medalhao: str = None, is_tester: bool = False):
    """Gera um novo código de acesso aleatório válido por 30 minutos, podendo pré-definir o nome do usuário e o medalhão."""
    try:
        import secrets
        letras = {1: 'Q', 2: 'M', 3: 'B', 4: 'A'}
        letra_nivel = letras.get(nivel_acesso, 'X')
        numero_aleatorio = secrets.randbelow(10000)
        
        prefixo = "TST" if is_tester else "PTC"
        codigo = f"{prefixo}-{numero_aleatorio:04d}{letra_nivel}"
        
        expiracao = (datetime.utcnow() + timedelta(minutes=30)).isoformat()
        
        novo_codigo = {
            "codigo": codigo,
            "nivel_acesso": nivel_acesso,
            "criado_por": id_criador,
            "expira_em": expiracao,
            "nome_atribuido": nome_atribuido,
            "medalhao": medalhao,
            "usado": False
        }
        
        supabase.table("codigos_acesso").insert(novo_codigo).execute()
        return codigo
    except Exception as e:
        print(f"Erro ao gerar novo código: {e}")
        return None

def get_todos_funcionarios():
    """Retorna todos os funcionários cadastrados no sistema."""
    try:
        response = supabase.table("funcionarios").select("*").execute()
        return response.data
    except Exception as e:
        print(f"Erro ao buscar todos os funcionários: {e}")
        return []

def deletar_funcionario(id_funcionario: str):
    """Deleta um funcionário do banco de dados (Revogar Acesso)."""
    try:
        response = supabase.table("funcionarios").delete().eq("id", id_funcionario).execute()
        return True
    except Exception as e:
        print(f"Erro ao deletar funcionário: {e}")
        return False

def alterar_status_funcionario(id_funcionario: str, novo_status: bool):
    """Suspende (False) ou Ativa (True) um funcionário existente."""
    try:
        response = supabase.table("funcionarios").update({"ativo": novo_status}).eq("id", id_funcionario).execute()
        return True if response.data else False
    except Exception as e:
        print(f"Erro ao alterar status: {e}")
        return False

# ==============================================================================
# AUTORIZAÇÕES MEDALHÃO
# ==============================================================================

def criar_solicitacao_autorizacao(solicitante_id: str, acao_alvo: str):
    """Cria um pedido de autorização pendente para o usuário Silver."""
    try:
        nova_auth = {
            "solicitante_id": solicitante_id,
            "acao_alvo": acao_alvo,
            "status": "PENDENTE"
        }
        response = supabase.table("autorizacoes").insert(nova_auth).execute()
        if response.data:
            return response.data[0]['id']
        return None
    except Exception as e:
        print(f"Erro ao criar solicitação de autorização: {e}")
        return None

def atualizar_autorizacao(auth_id: str, status: str, autorizador_id: str, expira_em: str = None):
    """O Gold responde à solicitação atualizando o status."""
    try:
        update_data = {
            "status": status,
            "autorizador_id": autorizador_id,
            "atualizado_em": datetime.utcnow().isoformat()
        }
        if expira_em:
            update_data["expira_em"] = expira_em
            
        supabase.table("autorizacoes").update(update_data).eq("id", auth_id).execute()
        return True
    except Exception as e:
        print(f"Erro ao atualizar autorização: {e}")
        return False

def get_autorizacao_por_id(auth_id: str):
    """Busca os detalhes de um pedido de autorização específico."""
    try:
        response = supabase.table("autorizacoes").select("*, solicitante:funcionarios(telegram_id, nome)").eq("id", auth_id).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Erro ao buscar autorização: {e}")
        return None

def verificar_autorizacao_valida(solicitante_id: str, acao_alvo: str):
    """Verifica se o usuário possui alguma permissão vigente (Única, Diária ou Livre) para essa ação."""
    try:
        response = supabase.table("autorizacoes").select("*") \
            .eq("solicitante_id", solicitante_id) \
            .in_("status", ["AUTORIZADO_UNICA", "AUTORIZADO_DIA", "AUTORIZADO_LIVRE"]) \
            .execute()
            
        if not response.data:
            return False
            
        for auth in response.data:
            # Se for específica e não bater, ignora
            if auth["acao_alvo"] != acao_alvo and auth["acao_alvo"] != "ALL":
                continue
                
            # Verifica o tipo de autorização
            if auth["status"] == "AUTORIZADO_LIVRE":
                return True
                
            if auth["status"] == "AUTORIZADO_DIA":
                if auth["expira_em"]:
                    expira = datetime.fromisoformat(auth["expira_em"].replace("Z", "+00:00"))
                    if datetime.now(expira.tzinfo) <= expira:
                        return True
                        
        return False
    except Exception as e:
        print(f"Erro ao verificar autorizações: {e}")
        return False

def get_usuarios_gold(nivel_acesso: int):
    """Retorna todos os usuários com medalhão Gold ESTRITAMENTE do mesmo nível de acesso do solicitante."""
    try:
        response = supabase.table("funcionarios").select("*").eq("medalhao", "Gold").eq("ativo", True).eq("nivel_acesso", nivel_acesso).execute()
        return response.data
    except Exception as e:
        print(f"Erro ao buscar usuários Gold: {e}")
        return []

def atualizar_persona(funcionario_id: str, nova_persona: str) -> bool:
    """Atualiza a persona preferida do funcionário."""
    try:
        response = supabase.table("funcionarios").update({"persona": nova_persona}).eq("id", funcionario_id).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Erro ao atualizar persona: {e}")
        return False

def incrementar_uso_persona(persona_nome: str):
    """Incrementa o contador de vezes que uma persona foi selecionada no ranking."""
    try:
        # Busca o valor atual
        response = supabase.table("persona_ranking").select("vezes_selecionada").eq("persona_nome", persona_nome).execute()
        if response.data:
            atual = response.data[0]["vezes_selecionada"]
            supabase.table("persona_ranking").update({"vezes_selecionada": atual + 1, "ultima_selecao": "now()"}).eq("persona_nome", persona_nome).execute()
        else:
            # Se não existir, cria com 1
            supabase.table("persona_ranking").insert({"persona_nome": persona_nome, "vezes_selecionada": 1}).execute()
    except Exception as e:
        print(f"Erro ao incrementar ranking da persona: {e}")

def get_ranking_personas():
    """Retorna o ranking de personas mais utilizadas."""
    try:
        response = supabase.table("persona_ranking").select("*").order("vezes_selecionada", desc=True).execute()
        return response.data
    except Exception as e:
        print(f"Erro ao buscar ranking de personas: {e}")
        return []

# ==============================================================================
# FASE 5: CATÁLOGO E ESTOQUE
# ==============================================================================

def buscar_produto_por_ean(ean: str):
    """Busca um produto pelo código de barras."""
    try:
        response = supabase.table("produtos").select("*").eq("ean", ean).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Erro ao buscar produto: {e}")
        return None

def cadastrar_produto(ean: str, nome: str, preco_base: float = 0.0):
    """Cadastra um novo produto no catálogo master."""
    try:
        data = {
            "ean": ean,
            "nome": nome,
            "preco_base": preco_base
        }
        response = supabase.table("produtos").insert(data).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Erro ao cadastrar produto: {e}")
        return None

def adicionar_estoque(produto_id: str, quiosque_id: str, quantidade_adicional: int = 1):
    """Adiciona ou atualiza o estoque de um quiosque. Retorna o estoque atualizado."""
    try:
        # Primeiro, tentar buscar se já existe
        response = supabase.table("estoque").select("*").eq("produto_id", produto_id).eq("quiosque_id", quiosque_id).execute()
        
        if response.data:
            # Já existe, faz update
            estoque_atual = response.data[0]
            nova_qtd = estoque_atual['quantidade'] + quantidade_adicional
            update_resp = supabase.table("estoque").update({"quantidade": nova_qtd, "atualizado_em": "now()"}).eq("id", estoque_atual['id']).execute()
            if update_resp.data:
                return update_resp.data[0]
        else:
            # Não existe, cria
            data = {
                "produto_id": produto_id,
                "quiosque_id": quiosque_id,
                "quantidade": quantidade_adicional
            }
            insert_resp = supabase.table("estoque").insert(data).execute()
            if insert_resp.data:
                return insert_resp.data[0]
                
        return None
    except Exception as e:
        print(f"Erro ao atualizar estoque: {e}")
        return None

def buscar_encomendas_pendentes(quiosque_id: str):
    """Busca encomendas pendentes para um quiosque específico, trazendo dados do cliente."""
    try:
        response = supabase.table("encomendas").select("*, clientes(nome, cpf)").eq("quiosque_id", quiosque_id).eq("status", "PENDENTE").execute()
        return response.data
    except Exception as e:
        print(f"Erro ao buscar encomendas pendentes: {e}")
        return []

def baixar_encomenda(encomenda_id: str, valor_final: float) -> bool:
    """Muda o status da encomenda para RETIRADA e salva o valor final."""
    try:
        response = supabase.table("encomendas").update({
            "status": "RETIRADA",
            "valor_final": valor_final,
            "atualizado_em": "now()"
        }).eq("id", encomenda_id).execute()
        return len(response.data) > 0
    except Exception as e:
        return False

def salvar_produto(produto_data: dict) -> bool:
    """Pré-cadastra um produto no catálogo e retorna True se der certo."""
    try:
        response = supabase.table("produtos").insert(produto_data).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Erro ao salvar produto: {e}")
        return False

def buscar_produto_por_ean(ean: str):
    try:
        response = supabase.table("produtos").select("*").eq("ean", ean).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Erro ao buscar produto por ean: {e}")
        return None

def buscar_encomendas_pendentes(quiosque_id: str):
    try:
        response = supabase.table("encomendas").select("*").eq("quiosque_id", quiosque_id).in_("status", ["PENDENTE", "PRONTO_RETIRADA"]).execute()
        return response.data
    except Exception as e:
        print(f"Erro ao buscar encomendas pendentes: {e}")
        return []

def atualizar_encomenda_status(encomenda_id: str, novo_status: str):
    try:
        supabase.table("encomendas").update({"status": novo_status, "atualizado_em": datetime.utcnow().isoformat()}).eq("id", encomenda_id).execute()
        return True
    except Exception as e:
        print(f"Erro ao atualizar encomenda: {e}")
        return False

def adicionar_perfil_teste(funcionario_id: str, nivel_teste: int):
    try:
        response = supabase.table("funcionarios").select("perfis_teste").eq("id", funcionario_id).execute()
        if response.data:
            perfis = response.data[0].get("perfis_teste") or []
            if nivel_teste not in perfis:
                perfis.append(nivel_teste)
                supabase.table("funcionarios").update({"perfis_teste": perfis}).eq("id", funcionario_id).execute()
        return True
    except Exception as e:
        print(f"Erro ao adicionar perfil teste: {e}")
        return False

def validar_codigo_teste(codigo: str):
    """Verifica se o código de teste é válido e retorna o nível de acesso do perfil simulado."""
    try:
        response = supabase.table("codigos_acesso").select("*").eq("codigo", codigo).eq("usado", False).execute()
        if not response.data:
            return None
            
        cod = response.data[0]
        # Códigos de teste não são marcados como 'usados' para permitir testes repetidos, 
        # mas expiram de qualquer forma após 30 mins
        
        return cod['nivel_acesso']
    except Exception as e:
        print(f"Erro ao validar código teste: {e}")
        return None

# ==============================================================================
# ESTOQUE TESTE
# ==============================================================================

def upload_imagem_produto(file_bytes: bytes, file_name: str) -> str:
    """Faz upload da imagem para o Supabase Storage e retorna a URL pública."""
    try:
        # Nome único para evitar cache/conflitos
        ext = file_name.split('.')[-1]
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        
        res = supabase.storage.from_("produtos").upload(unique_name, file_bytes, {"content-type": f"image/{ext}"})
        if res:
            # Retornar a URL pública
            return f"{URL}/storage/v1/object/public/produtos/{unique_name}"
        return None
    except Exception as e:
        print(f"Erro no upload da imagem: {e}")
        return None

def adicionar_produto_teste(nome: str, franquia: str, preco: float, url_imagem: str = None):
    """Insere um produto de teste na tabela produtos."""
    try:
        # Garante que tem a tag [TESTE] no nome
        if "[TESTE]" not in nome:
            nome = f"[TESTE] {nome}"
            
        ean_mock = f"TESTE{random.randint(10000000, 99999999)}"
        
        data = {
            "ean": ean_mock,
            "nome": nome,
            "franquia": franquia,
            "preco_base": preco,
            "imagem_url": url_imagem
        }
        response = supabase.table("produtos").insert(data).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Erro ao inserir produto teste: {e}")
        return None

def listar_produtos_teste():
    """Retorna apenas os produtos criados para teste."""
    try:
        response = supabase.table("produtos").select("*").like("nome", "%[TESTE]%").order("criado_em", desc=True).execute()
        return response.data
    except Exception as e:
        print(f"Erro ao listar produtos teste: {e}")
        return []

# ==============================================================================
# STORAGE DE IMAGENS
# ==============================================================================

def upload_image_to_storage(image_bytes: bytes, file_name: str, content_type: str = "image/jpeg", bucket: str = "produtos") -> str:
    """
    Faz o upload de uma imagem (em bytes) para o bucket no Supabase.
    Retorna a URL pública da imagem.
    """
    try:
        unique_name = f"{uuid.uuid4().hex}_{file_name}"
        res = supabase.storage.from_(bucket).upload(
            file=image_bytes,
            path=unique_name,
            file_options={"content-type": content_type}
        )
        public_url = supabase.storage.from_(bucket).get_public_url(unique_name)
        return public_url
    except Exception as e:
        print(f"Erro ao fazer upload da imagem {file_name}: {e}")
        return None

def excluir_produto_teste(produto_id: str):
    """Exclui um produto do banco pelo ID."""
    try:
        response = supabase.table("produtos").delete().eq("id", produto_id).execute()
        return True
    except Exception as e:
        print(f"Erro ao excluir produto teste: {e}")
        return False

