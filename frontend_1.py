import streamlit as st
import requests
import hashlib
from datetime import datetime
import os

# Configuração inicial
os.chdir(os.path.abspath(os.curdir))

# Função para gerar um identificador de conversa
def conversaID():
    data_legivel = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    hash_id = hashlib.sha256(data_legivel.encode('utf-8')).hexdigest()
    return hash_id[:8]

# URL do backend FastAPI
API_URL = "https://seinfra-dwgwbrfscfbpdugu.eastus2-01.azurewebsites.net/seinfra/"
FILES_DIR = "/app/files"  # Pasta onde os arquivos estão armazenados dentro do container

# Função para listar arquivos na pasta de documentos
def listar_arquivos():
    try:
        return [f for f in os.listdir(FILES_DIR) if f.endswith(".pdf")]
    except Exception as e:
        st.error(f"Erro ao listar arquivos: {e}")
        return []

# Função para enviar prompt para a API
def enviar_prompt_api(prompt, session_id, chat_history):
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(
            API_URL,
            headers=headers,
            json={"prompt": prompt, "session_id": session_id, "chat_history": chat_history},
            timeout=300,
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"resposta": "Erro na API", "chat_history": chat_history}
    except requests.Timeout:
        return {"resposta": "Erro: Tempo limite atingido.", "chat_history": chat_history}
    except requests.ConnectionError:
        return {"resposta": "Erro: Problema de conexão.", "chat_history": chat_history}
    except Exception as e:
        return {"resposta": f"Erro inesperado: {e}", "chat_history": chat_history}

# Inicializa sessão se necessário
if "hash_id" not in st.session_state:
    st.session_state["hash_id"] = conversaID()

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Olá, sou o AIstein, assistente digital da SEINFRA. Como posso ajudar?"}]

if "etapa" not in st.session_state:
    st.session_state["etapa"] = "inicio"  # Estados: "inicio" → "selecionando_arquivo" → "analise_feita"

# Função para resetar tudo
def resetar_tudo():
    st.session_state.clear()
    st.session_state["hash_id"] = conversaID()
    st.session_state["chat_history"] = []
    st.session_state["messages"] = [{"role": "assistant", "content": "Olá, sou o AIstein, assistente digital da SEINFRA. Como posso ajudar?"}]
    st.session_state["etapa"] = "inicio"
    st.rerun()

# Layout da barra lateral
with st.sidebar:
    st.image('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRgcOUfw-4BV2YMHyaOIecFKJCuz6uURut4mg&s', use_container_width="auto")

    if st.button("🧹 Resetar Tudo"):
        resetar_tudo()

    # Passo 1: Selecionar Arquivo
    if st.session_state["etapa"] == "inicio":
        if st.button("📄 Selecionar Arquivo para Análise"):
            st.session_state["etapa"] = "selecionando_arquivo"
            st.rerun()

    # Passo 2: Escolher um arquivo da pasta
    if st.session_state["etapa"] == "selecionando_arquivo":
        arquivos_disponiveis = listar_arquivos()
        if arquivos_disponiveis:
            arquivo_selecionado = st.selectbox("Escolha um arquivo para análise:", arquivos_disponiveis)
            if st.button("📂 Iniciar Análise"):
                st.session_state["arquivo_orcamento"] = os.path.join(FILES_DIR, arquivo_selecionado)
                st.session_state["etapa"] = "analise_feita"
                st.rerun()
        else:
            st.warning("Nenhum arquivo disponível para análise.")

    # Passo 3: Comparação com a Tabela de Insumos
    if st.session_state["etapa"] == "analise_feita":
        if st.button("📊 Comparar com Tabela de Insumos"):
            st.session_state["prompt"] = "Agora que extraímos as informações do orçamento, vamos comparar com nossa Tabela de Insumos."
            st.session_state["etapa"] = "comparacao_realizada"
            st.rerun()

st.title("🗨️ Assistente Digital - SEINFRA")

# Exibir mensagens na interface do chat
for msg in st.session_state.messages:
    st.chat_message(msg["role"], avatar="👤").write(msg["content"])

# Disparar prompt automaticamente se houver ação
if "prompt" in st.session_state and st.session_state["prompt"]:
    prompt = st.session_state["prompt"]
    st.session_state["prompt"] = None

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user", avatar="🤓").write(prompt)

    hash_id = st.session_state["hash_id"]
    with st.spinner("O assistente está processando sua solicitação..."):
        response = enviar_prompt_api(prompt, hash_id, st.session_state["chat_history"])
        st.session_state.messages.append({"role": "assistant", "content": response["resposta"]})
        st.chat_message("assistant", avatar="👤").write(response["resposta"])
