from langchain_core.messages import AIMessage, HumanMessage
import streamlit as st
import requests
import hashlib
from datetime import datetime
import tempfile
from pathlib import Path
import os

# Configuração inicial
os.chdir(os.path.abspath(os.curdir))

# Função para gerar um identificador de conversa
def conversaID():
    data_legivel = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    hash_id = hashlib.sha256(data_legivel.encode('utf-8')).hexdigest()
    return hash_id[:8]

# URL do backend FastAPI (ajuste conforme necessário)
API_URL = "https://seinfra-dwgwbrfscfbpdugu.eastus2-01.azurewebsites.net/seinfra/"
#"seinfra-dwgwbrfscfbpdugu.eastus2-01.azurewebsites.net"

# Função para salvar o arquivo temporariamente
# def save_uploaded_file(uploaded_file):
#     file_extension = Path(uploaded_file.name).suffix
#     with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
#         temp_file.write(uploaded_file.read())
#         return temp_file.name

# Função para simular o caminho do arquivo (já que não podemos acessar o caminho diretamente)
def get_file_name(uploaded_file):
    return uploaded_file if uploaded_file else "Nenhum arquivo selecionado."

def save_uploaded_file(uploaded_file):
    temp_dir = "/home/site/temp"  # Diretório persistente no Azure Web App
    os.makedirs(temp_dir, exist_ok=True)  # Garante que o diretório existe

    temp_file_path = os.path.join(temp_dir, uploaded_file.name)  # Caminho completo do arquivo

    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(uploaded_file.getbuffer())  # Salva corretamente o conteúdo

    return temp_file_path  # Retorna o caminho correto do arquivo salvo




# Função para enviar prompt para a API
def enviar_prompt_api(prompt, session_id, chat_history):
    try:
        headers = {'Content-Type': 'application/json'}

        # 🔎 DEBUG: Verifica se o arquivo está salvo no session_state
        print(f"🚀 Enviando prompt: {prompt}")
        print(f"📂 Arquivo no session_state: {st.session_state.get('arquivo_orcamento', 'Nenhum arquivo')}")

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
    st.session_state["etapa"] = "inicio"  # Estados: "inicio" → "aguardando_pdf" → "analise_feita"

# Função para resetar tudo
def resetar_tudo():
    st.session_state.clear()  # Apaga tudo do session_state
    st.session_state["hash_id"] = conversaID()
    st.session_state["chat_history"] = []
    st.session_state["messages"] = [{"role": "assistant", "content": "Olá, sou o AIstein, assistente digital da SEINFRA. Como posso ajudar?"}]
    st.session_state["etapa"] = "inicio"
    st.rerun()

# Layout da barra lateral
with st.sidebar:
    st.image('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRgcOUfw-4BV2YMHyaOIecFKJCuz6uURut4mg&s', use_container_width="auto")

    # Botão para resetar tudo (zera chat e reinicia do zero)
    if st.button("🧹 Resetar Tudo"):
        resetar_tudo()

    # Passo 1: Analisar Orçamento
    if st.session_state["etapa"] == "inicio":
        if st.button("📄 Analisar Orçamento"):
            st.session_state["prompt"] = "Vou te passar um arquivo PDF com o orçamento de uma construtora. Quero que extraia as informações contidas neste arquivo."
            st.session_state["etapa"] = "aguardando_pdf"

    # Passo 2: Upload de PDF só aparece após clicar em "Analisar Orçamento"
    if st.session_state["etapa"] in ["aguardando_pdf", "analise_feita"]:
        uploaded_file = st.file_uploader("📂 Envie o arquivo PDF do orçamento", type=["pdf"])

        # if uploaded_file:
        #     temp_file_path = save_uploaded_file(uploaded_file)  # Salva o arquivo corretamente
        #     st.write(f"📂 Arquivo salvo temporariamente em: `{temp_file_path}`")  # Debug para ver onde foi salvo
        #     st.session_state["arquivo_orcamento"] = temp_file_path
        #     st.session_state["prompt"] = f"Arquivo {uploaded_file.name} carregado. Extraia as informações do orçamento."
        #     st.session_state["etapa"] = "analise_feita"

        if uploaded_file:
            # Salvando o arquivo corretamente na pasta /tmp/
            temp_file_path = os.path.join(tempfile.gettempdir(), uploaded_file.name)

            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(uploaded_file.getbuffer())

            # Debug: Exibir informações
            st.write(f"📂 Arquivo salvo temporariamente em: `{temp_file_path}`")
            st.write("📂 Arquivos no diretório temporário:", os.listdir(tempfile.gettempdir()))

            # Atualiza o session_state corretamente
            st.session_state["arquivo_orcamento"] = temp_file_path
            st.session_state["prompt"] = f"Arquivo `{uploaded_file.name}` carregado. Extraia as informações do orçamento."

            # Atualizar a etapa corretamente
            st.session_state["etapa"] = "analise_feita"



    # Passo 3: Comparação com a Tabela de Insumos (sempre visível após análise)
    if st.session_state["etapa"] in ["analise_feita", "comparacao_realizada"]:
        if st.button("📊 Comparar com Tabela de Insumos"):
            st.session_state["prompt"] = "Agora que extraímos as informações do PDF com o orçamento, vamos comparar com a nossa tabela de insumos que está em nossa base de dados."
            st.session_state["etapa"] = "comparacao_realizada"
            st.rerun()


    # Novo Botão: Verificar Outro Documento (não apaga histórico, só reinicia a análise)
    if st.session_state["etapa"] in ["analise_feita", "comparacao_realizada"]:
        if st.button("🔄 Verificar Outro Documento"):
            st.session_state["etapa"] = "aguardando_pdf"  # Volta para a etapa de upload
            st.session_state.pop("arquivo_orcamento", None)  # Remove o arquivo antigo
            st.session_state["prompt"] = "Envie um novo documento para análise."  # Mensagem automática
            st.rerun()

st.title("🗨️ Assistente Digital - SEINFRA")

# Exibir mensagens na interface do chat
for msg in st.session_state.messages:
    st.chat_message(msg["role"], avatar="👤").write(msg["content"])

# Disparar prompt automaticamente se houver ação
if "prompt" in st.session_state and st.session_state["prompt"]:
    prompt = st.session_state["prompt"]
    st.session_state["prompt"] = None  # Reset para evitar loops

    # Exibir prompt no chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user", avatar="🤓").write(prompt)

    # Enviar prompt para API
    hash_id = st.session_state["hash_id"]
    with st.spinner("O assistente está processando sua solicitação..."):
        response = enviar_prompt_api(prompt, hash_id, st.session_state["chat_history"])

        # Adicionar resposta ao chat
        st.session_state.messages.append({"role": "assistant", "content": response["resposta"]})
        st.chat_message("assistant", avatar="👤").write(response["resposta"])
