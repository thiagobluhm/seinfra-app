import streamlit as st
import os
import fitz  # PyMuPDF
from openai import OpenAI
from docx import Document
import re
from io import BytesIO
from dotenv import load_dotenv
from streamlit import session_state as ss
from streamlit_pdf_viewer import pdf_viewer

# 🔹 Carregar variáveis de ambiente
load_dotenv()
secretk = os.environ.get("OPENAI_API_KEY")
cliente_openai = OpenAI(api_key=secretk)

# 🔹 Função para extrair texto do PDF
def extract_content(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    extracted_data = []
    for page_num, page in enumerate(doc, start=1):
        extracted_data.append({
            "page_number": page_num,
            "text": page.get_text(),
            "link": f"#page={page_num}"
        })
    return extracted_data

# 🔹 Função para identificar palavras-chave no texto
def find_keywords(text, keywords):
    return [kw for kw in keywords if kw.lower() in text.lower()]

# 🔹 Função para gerar resumos via OpenAI
def generate_summary(text):
    prompt = f"Resuma o seguinte texto em poucas frases mantendo os pontos principais:\n\n{text}"
    try:
        response = cliente_openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é um assistente que resume textos de forma objetiva."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Erro ao gerar resumo: {e}"

# 🔹 Processamento do PDF
def process_pdf(pdf_bytes):
    keywords = [
        "Governo Federal", "Governo do Estado do Ceará", "Ceará", "infraestrutura",
        "saúde", "educação", "segurança pública", "investimento", "ministro", 
        "governador", "prefeito", "política", "infraestrutura urbana", "mobilidade urbana",
        "transporte público", "energia renovável", "obras públicas", "hospital", 
        "escolas públicas", "recursos federais", "recursos estaduais", "moradia", 
        "habitação", "economia", "desenvolvimento regional", "assistência social", 
        "meio ambiente", "água potável", "saneamento básico", "pontes", "rodovias", 
        "ferrovias", "aeroportos", "portos", "logística", "segurança alimentar", 
        "orçamento público", "políticas públicas", "emendas parlamentares", 
        "licitação", "contratos públicos", "parcerias público-privadas", 
        "inovação tecnológica", "tecnologia", "saúde pública", "sistema único de saúde",
        "vacinação", "doenças infecciosas", "crise hídrica", "ministério", 
        "agricultura", "turismo", "indústria", "comércio exterior", "universidades"
    ]
    extracted_data = extract_content(pdf_bytes)
    filtered_data = []
    
    for page in extracted_data:
        detected_keywords = find_keywords(page["text"], keywords)
        if detected_keywords:
            summary = generate_summary(page["text"])
            filtered_data.append({
                "page_number": page["page_number"],
                "summary": summary,
                "keywords": ", ".join(detected_keywords)
            })
    return filtered_data

# 🔹 Streamlit Interface
st.set_page_config(page_title="Clipapptor - IA para Resumo de PDFs", layout="wide")
st.title("📑 Clipapptor - IA para Resumo de PDFs")

# Sidebar com Upload e Botão
with st.sidebar:
    uploaded_file = st.file_uploader("📤 Faça upload do PDF", type=["pdf"], key='pdf')
    if st.button("📄 Gerar Clippings do Jornal") and uploaded_file:
        with st.spinner("Processando PDF..."):
            resumos = process_pdf(uploaded_file.getvalue())
        ss.resumos = resumos  # Armazena resumos na sessão

# Exibir PDF ao lado
col1, col2 = st.columns([2, 3])

with col1:
    if ss.get('pdf'):
        pdf_viewer(input=ss.pdf.getvalue(), width=700)

with col2:
    if ss.get('resumos'):
        for resumo in ss.resumos:
            st.markdown(f"### Página {resumo['page_number']}")
            st.write(f"**Palavras-chave:** {resumo['keywords']}")
            st.write(f"**Resumo:** {resumo['summary']}")
            st.markdown("---")
    else:
        st.warning("Aguardando geração de clipping...")