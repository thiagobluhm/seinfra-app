import shutil
import os

# # Diretório do ChromaDB
chroma_db_dir = "dados_vetorizados_SEINFRA"  # Substitua pelo diretório correto

# Deleta o diretório se existir
if os.path.exists(chroma_db_dir):
    shutil.rmtree(chroma_db_dir)
    print(f"Banco de dados ChromaDB no diretório '{chroma_db_dir}' foi deletado com sucesso!")
else:
    print("O diretório especificado não existe.")

# from langchain_community.document_loaders import PyPDFLoader

# # Carregar o PDF
# loader = PyPDFLoader("pdfs_/Tabela_de_Insumos_028___ENC_SOCIAIS_114_15.pdf")
# docs = loader.load()

# # Caminho para salvar o conteúdo em um arquivo .txt
# output_file = "output_tabela_insumos.txt"

# # Escrever o conteúdo do PDF no arquivo de texto
# with open(output_file, "w", encoding="utf-8") as f:
#     for doc in docs:
#         f.write(doc.page_content)  # Escreve o conteúdo da página
#         f.write("\n\n")  # Adiciona uma quebra de linha entre páginas

# print(f"Conteúdo do PDF salvo em '{output_file}'.")



from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import OpenAI
#from langchain.vectorstores import Pinecone
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_chroma import Chroma
import os
from langchain_openai import ChatOpenAI
from openai import OpenAI
# libraries
from langchain_chroma import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders.merge import MergedDataLoader
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain,  RetrievalQA
from chromadb.config import Settings
from chromadb import Client
from dotenv import load_dotenv
import openai


# DSECRET KEY diretamente no arquivo .ENV
load_dotenv()

# Certifique-se de que a chave da API seja configurada como variável de ambiente
secretk = os.environ.get("OPENAI_API_KEY")
openai.api_key = secretk
# Configurando o modelo de linguagem com LangChain
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
llm = ChatOpenAI(model="gpt-4o", temperature=0.1, max_tokens=2048)

# # Carregar todos os PDFs do diretório
# loader = PyPDFDirectoryLoader("pdfs_")
# documents = loader.load()

# # Iterar sobre os documentos e imprimir os nomes dos arquivos
# print("Nomes dos arquivos PDF encontrados:\n")
# files_ = []
# for doc in documents:
#     source = doc.metadata.get('source', 'Nome do arquivo não encontrado')
#     filename = os.path.basename(source)  # Extrai apenas o nome do arquivo
#     files_.append(filename)
    
# print(set(files_))

# from pymupdf import pymupdf

# # Carregar o PDF
# pdf_path = "pdfs_/Tabela_de_Insumos_028___ENC_SOCIAIS_114_15.pdf"
# doc = pymupdf.open(pdf_path)  # Abre o PDF com PyMuPDF

# # Calcular o número de caracteres por página
# num_paginas = len(doc)  # Total de páginas no PDF
# total_caracteres = sum(len(doc[i].get_text()) for i in range(num_paginas))

# # Média de caracteres por página
# media_caracteres_pagina = total_caracteres / num_paginas if num_paginas > 0 else 0

# # Resultado
# print(f"Número total de caracteres: {total_caracteres}")
# print(f"Número médio de caracteres por página: {media_caracteres_pagina:.2f}")

# Configurações
# pdf_path = "pdfs_/Tabela_de_Insumos_028___ENC_SOCIAIS_114_15.pdf"
# persist_directory = "dados_vetorizados_SEINFRA"
# collection_name = "Tabela_de_Insumos_028___ENC_SOCIAIS_114_15"

# # Carregar o PDF
# loader = PyPDFLoader(pdf_path)
# docs = loader.load()

# # Dividir em chunks
# text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
# text_chunks = text_splitter.split_documents(docs)

# # Configurar embeddings
# embedding_function = OpenAIEmbeddings(
#     model="text-embedding-3-large",
#     openai_api_key=secretk
# )

# # Recriar a collection
# vectordb = Chroma.from_documents(
#     documents=text_chunks,
#     embedding=embedding_function,
#     collection_name=collection_name,
#     persist_directory=persist_directory
# )

# print(f"Collection '{collection_name}' reindexada com sucesso!")
