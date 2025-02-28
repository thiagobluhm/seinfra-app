from langchain_chroma import Chroma
from langchain.schema import Document  # Para criar objetos Document
from langchain_openai import OpenAIEmbeddings
import pymupdf
import os 
os.chdir(os.path.abspath(os.curdir))


secretk = os.environ.get("OPENAI_API_KEY")

# Função para carregar e extrair texto de um PDF
def load_pdf_content(pdf_path):
    """
    Carrega e extrai o conteúdo do PDF e o organiza em objetos Document.

    Args:
        pdf_path (str): Caminho para o arquivo PDF.

    Returns:
        list: Lista de objetos Document contendo o texto e metadados.
    """
    documents = []
    try:
        with pymupdf.open(pdf_path) as pdf_file:  # Usando pymupdf (PyMuPDF)
            for page_num in range(pdf_file.page_count):
                page = pdf_file.load_page(page_num)
                text = page.get_text("text").strip()
                if text:
                    # Criar um objeto Document para cada página
                    documents.append(
                        Document(
                            page_content=text,
                            metadata={"source": pdf_path, "page": page_num + 1}
                        )
                    )
    except Exception as e:
        print(f"Erro ao processar PDF {pdf_path}: {e}")
    return documents

# Função para armazenar conteúdo vetorializado no ChromaDB
def store_in_chroma(documents):
    """
    Armazena os documentos vetorizados no ChromaDB.

    Args:
        documents (list): Lista de objetos Document.
    """
    # Inicializa o modelo de embeddings
    embeddings = OpenAIEmbeddings(openai_api_key=secretk)

    # Inicializa o ChromaDB
    vector_store = Chroma(
        collection_name='insumos',
        embedding_function=embeddings,
        persist_directory='dados_vetorizados',  # Diretório onde o banco será armazenado
    )
    
    # Armazena os documentos no ChromaDB
    vector_store.add_documents(documents)
    print("Documentos armazenados no ChromaDB com sucesso!")

# Função para carregar e armazenar conteúdo de várias URLs e PDFs
def process_documents(pdf_paths):
    """
    Processa uma lista de PDFs, extrai o conteúdo e o armazena no ChromaDB.

    Args:
        pdf_paths (list): Lista de caminhos de arquivos PDF.
    """
    all_documents = []
    
    # Iterar sobre cada PDF e carregar o conteúdo
    for pdf_path in pdf_paths:
        documents = load_pdf_content(pdf_path)
        all_documents.extend(documents)  # Adiciona todos os documentos extraídos do PDF à lista
    
    # Armazena todos os documentos no ChromaDB com embeddings
    if all_documents:
        store_in_chroma(all_documents)
    else:
        print("Nenhum documento válido encontrado para armazenamento.")

# Lista de caminhos dos PDFs que você deseja processar
pdf_paths = [
    "Tabela_de_Insumos_028___ENC_SOCIAIS_114_15.pdf"
    # Adicione outros PDFs aqui
]

# Processar os PDFs e armazenar no ChromaDB
process_documents(pdf_paths)