from fastapi import FastAPI, Request
from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel, Field
from aistenbot_v12910_seinfra import agenteIA
import logging
from fastapi.middleware.gzip import GZipMiddleware
from fastapi import FastAPI, UploadFile, File
from pathlib import Path
from contextlib import asynccontextmanager
from tiktoken import encoding_for_model
from hashlib import sha256
import json, os

# Configurar logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# CRIANDO CARREGANDO OS TOKENS
CACHE_FILE = "token_cache.json"

# Carregar cache de arquivo
def carregar_cache():
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}  # Se o arquivo não existir, retorna um cache vazio

# Salvar cache em arquivo
def salvar_cache():
    with open(CACHE_FILE, "w") as f:
        json.dump(token_cache, f, indent=4)

# Inicializar cache
token_cache = carregar_cache()

# TRABALHANDO O CACHE PARA TOKENS

# Função para tokenizar texto
def tokenizar_texto(texto, modelo="gpt-4o"):
    encoding = encoding_for_model(modelo)
    return encoding.encode(texto)

# Gerar hash para identificar prompts
def gerar_hash(texto):
    hash_value = sha256(texto.encode("utf-8")).hexdigest()
    logging.info(f"Gerando hash para texto: '{texto}' -> Hash: {hash_value}")
    return hash_value

# Função para buscar no cache
def buscar_tokens_no_cache(prompt):
    chave = gerar_hash(prompt)

    # Garantir que o cache está atualizado com o arquivo
    global token_cache
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            token_cache = json.load(f)

    # Verificar se a chave existe no cache e retornar os tokens
    if chave in token_cache and "tokens" in token_cache[chave]:
        tokens = token_cache[chave]["tokens"]
        logging.info(f"Buscando tokens no cache. Chave: {chave} -> Tokens encontrados: {tokens}")
        return tokens
    else:
        logging.info(f"Buscando tokens no cache. Chave: {chave} -> Tokens não encontrados.")
        return None


# Função para salvar no cache
def salvar_tokens_no_cache(prompt, tokens):
    chave = gerar_hash(prompt)
    token_cache[chave] = {"tokens": tokens}

    # Salvar o cache no arquivo
    salvar_cache()

    logging.info(f"Tokens salvos no cache. Chave: {chave} -> Tokens: {tokens}")


# Lifespan substituindo on_event
@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Servidor FastAPI iniciado com sucesso.")
    yield
    logging.info("Encerrando servidor FastAPI. Limpando recursos...")

# Aplicação FastAPI
app = FastAPI(lifespan=lifespan)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Modelo de entrada da API
class PromptRequest(BaseModel):
    prompt: str = Field(..., description="O prompt enviado pelo cliente.")
    session_id: str = Field(..., description="O ID único para identificar a sessão.")
    chat_history: list = Field(
        ...,
        description="Histórico de conversas anterior em formato de lista, contendo mensagens do usuário e do assistente.",
    )

# Função para desserializar o histórico de chat
def desserializar_chat_history(chat_history):
    desserializado = []
    for message in chat_history:
        if message.get("role") == "user":
            desserializado.append(HumanMessage(content=message["content"]))
        elif message.get("role") == "assistant":
            desserializado.append(AIMessage(content=message["content"]))
    return desserializado

# Função para serializar o histórico de chat
def serializar_chat_history(chat_history):
    """
    Converte o histórico de objetos LangChain (HumanMessage/AIMessage) para o formato de dicionário {role, content}.
    """
    return [
        {"role": "user", "content": msg.content} if isinstance(msg, HumanMessage)
        else {"role": "assistant", "content": msg.content}
        for msg in chat_history
    ]

# Função para estender a memória
def extensao_memoria(c, p, r):
    """
    Atualiza o histórico de memória com novas mensagens no formato LangChain.
    """
    c.append(HumanMessage(content=p))
    c.append(AIMessage(content=r))


# Diretório onde os arquivos PDF estão armazenados dentro do container (volume montado)
STORAGE_DIR = "/app/arquivospdfs"

# Variável em memória para armazenar o histórico de conversas
historico_memoria = {}

# Testando a API com GET
@app.get("/")
def read_root():
    return {"message": "Servidor FastAPI está funcionando!"}


# Listar Arquivos *****************************************************************************
@app.get("/listar_arquivos")
def listar_arquivos():
    if os.path.exists(STORAGE_DIR):
        arquivos = [f for f in os.listdir(STORAGE_DIR) if f.endswith(".pdf")]
        return {"arquivos": arquivos}
    return {"arquivos": []}

# Endpoint para processar o prompt
@app.post("/seinfra/")
async def processar_prompt_api(request: PromptRequest):
    try:
        logging.info(f"Recebendo requisição com prompt: {request.prompt}")

        # Verificar tokens no cache
        tokens_existentes = buscar_tokens_no_cache(request.prompt)
        if tokens_existentes:
            logging.info("Tokens encontrados no cache. Evitando nova tokenização.")
        else:
            logging.info("Tokens não encontrados no cache. Tokenizando o texto.")
            logging.info(f"Prompt recebido para tokenização: '{request.prompt}'")
            tokens = tokenizar_texto(request.prompt)
            salvar_tokens_no_cache(request.prompt, tokens)
            logging.info(f"Tokens salvos: {tokens}")

        # Receber dados do cliente
        prompt = request.prompt
        session_id = request.session_id

        # Verificar se o histórico já existe na memória
        if session_id not in historico_memoria:
            historico_memoria[session_id] = []
            logging.info(f"Nova sessão criada: {session_id}")

        # Validar e desserializar o histórico
        if not isinstance(request.chat_history, list):
            return {"erro": "O campo 'chat_history' deve ser uma lista válida."}

        chat_history = desserializar_chat_history(request.chat_history)
        logging.info(f"Histórico recebido: {chat_history}")

        # Atualiza o histórico na memória com as mensagens atuais
        historico_memoria[session_id].extend(chat_history)
        logging.info(f"Histórico atualizado na memória para sessão {session_id}")

        # Chamar a função do core que processa o prompt
        logging.info("Chamando o agente para processar o prompt...")
        resposta = agenteIA(prompt, session_id, historico_memoria[session_id])
        logging.debug(f"Resposta gerada pelo agente: {resposta}")

        # Extender a memória com a nova interação
        extensao_memoria(historico_memoria[session_id], prompt, resposta)

        if "arquivo_orcamento" in historico_memoria[session_id]:
            caminho_arquivo = historico_memoria[session_id]["arquivo_orcamento"]
            if os.path.exists(caminho_arquivo):
                logging.info(f"✅ Arquivo encontrado na API: {caminho_arquivo}")
            else:
                logging.error(f"❌ ERRO: Arquivo NÃO encontrado em {caminho_arquivo}")

        # Serializar o histórico para retorno
        chat_history_serializado = [
            {"role": "user", "content": msg.content} if isinstance(msg, HumanMessage)
            else {"role": "assistant", "content": msg.content}
            for msg in historico_memoria[session_id]
        ]

        # Retornar a resposta e o histórico atualizado
        return {"resposta": resposta, "chat_history": chat_history_serializado}

    except Exception as e:
        logging.error(f"Erro ao processar a requisição: {e}", exc_info=True)
        return {
            "resposta": "Ops! Estamos com algum probleminha. Tente novamente mais tarde. Se o problema persistir, contate o suporte.",
            "erro": str(e),
        }

