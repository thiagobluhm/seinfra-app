import streamlit as st
import requests
import hashlib
from datetime import datetime
import os

# 🔗 URL do backend FastAPI (ajuste conforme a URL real do Web App na Azure)
API_URL = "https://seinfra-dwgwbrfscfbpdugu.eastus2-01.azurewebsites.net"

# 🔎 Função para listar arquivos do backend
def listar_arquivos():
    try:
        response = requests.get(f"{API_URL}/listar_arquivos")

        # Verifica se a resposta é JSON antes de tentar acessar
        if response.status_code == 200:
            try:
                data = response.json()
                return data.get("arquivos", [])  # Retorna a lista de arquivos ou uma lista vazia
            except ValueError:
                st.error("Erro ao processar resposta da API (não é um JSON válido).")
                return []
        else:
            st.error(f"Erro na requisição ({response.status_code}): {response.text}")
            return []
    except requests.RequestException as e:
        st.error(f"Erro ao buscar arquivos: {e}")
        return []

# 🔎 Função para gerar um identificador de conversa
def conversaID():
    data_legivel = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    hash_id = hashlib.sha256(data_legivel.encode('utf-8')).hexdigest()
    return hash_id[:8]

# 📩 Função para enviar prompt para a API
def enviar_prompt_api(prompt, session_id, chat_history):
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(
            f"{API_URL}/seinfra/",
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

# 🛠️ Inicializa sessão se necessário
if "hash_id" not in st.session_state:
    st.session_state["hash_id"] = conversaID()

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Olá, sou o AIstein, assistente digital da SEINFRA. Como posso ajudar?"}]

if "etapa" not in st.session_state:
    st.session_state["etapa"] = "inicio"

# 🔄 Função para resetar tudo
def resetar_tudo():
    st.session_state.clear()
    st.session_state["hash_id"] = conversaID()
    st.session_state["chat_history"] = []
    st.session_state["messages"] = [{"role": "assistant", "content": "Olá, sou o AIstein, assistente digital da SEINFRA. Como posso ajudar?"}]
    st.session_state["etapa"] = "inicio"
    st.rerun()

# 📌 Layout da barra lateral
with st.sidebar:
    st.image('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRgcOUfw-4BV2YMHyaOIecFKJCuz6uURut4mg&s', use_container_width="auto")

    if st.button("🧹 Resetar Tudo"):
        resetar_tudo()

    # 🔎 Passo 1: Analisar Orçamento
    if st.session_state["etapa"] == "inicio":
        if st.button("📄 Analisar Orçamento"):
            st.session_state["prompt"] = "Vou te passar um arquivo PDF com o orçamento de uma construtora. Quero que extraia as informações contidas neste arquivo."
            st.session_state["etapa"] = "aguardando_pdf"

    # 📂 Passo 2: Selecionar um arquivo existente no volume do container
    if st.session_state["etapa"] in ["aguardando_pdf", "analise_feita"]:
        arquivos_disponiveis = listar_arquivos()

        arquivo_selecionado = st.selectbox("📂 Selecione um arquivo para análise:", arquivos_disponiveis)

        if arquivo_selecionado and arquivo_selecionado != "Nenhum arquivo disponível":
            st.session_state["arquivo_orcamento"] = arquivo_selecionado
            st.session_state["prompt"] = f"Arquivo `{arquivo_selecionado}` selecionado. Extraia as informações do orçamento."
            st.session_state["etapa"] = "analise_feita"
            st.rerun()

    # 📊 Passo 3: Comparação com a Tabela de Insumos
    if st.session_state["etapa"] in ["analise_feita", "comparacao_realizada"]:
        if st.button("📊 Comparar com Tabela de Insumos"):
            st.session_state["prompt"] = "Agora que extraímos as informações do PDF com o orçamento, vamos comparar com a nossa tabela de insumos que está em nossa base de dados."
            st.session_state["etapa"] = "comparacao_realizada"
            st.rerun()

    # 🔄 Novo Botão: Verificar Outro Documento
    if st.session_state["etapa"] in ["analise_feita", "comparacao_realizada"]:
        if st.button("🔄 Verificar Outro Documento"):
            st.session_state["etapa"] = "aguardando_pdf"
            st.session_state.pop("arquivo_orcamento", None)
            st.session_state["prompt"] = "Selecione um novo documento para análise."
            st.rerun()

# 🏡 Título da página
st.title("🗨️ Assistente Digital - SEINFRA")

# 💬 Exibir mensagens na interface do chat
for msg in st.session_state.messages:
    st.chat_message(msg["role"], avatar="👤").write(msg["content"])

# 🚀 Disparar prompt automaticamente se houver ação
if "prompt" in st.session_state and st.session_state["prompt"]:
    prompt = st.session_state["prompt"]
    st.session_state["prompt"] = None

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user", avatar="🤓").write(prompt)

    # Enviar prompt para API
    hash_id = st.session_state["hash_id"]
    with st.spinner("O assistente está processando sua solicitação..."):
        response = enviar_prompt_api(prompt, hash_id, st.session_state["chat_history"])

        # Adicionar resposta ao chat
        st.session_state.messages.append({"role": "assistant", "content": response["resposta"]})
        st.chat_message("assistant", avatar="👤").write(response["resposta"])
