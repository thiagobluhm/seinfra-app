from langchain_chroma import Chroma
from langchain.schema import Document  # Para criar objetos Document
from langchain_openai import OpenAIEmbeddings
import pymupdf
import os 
import pandas as pd
from uuid import uuid4
from dotenv import load_dotenv

os.chdir(os.path.abspath(os.curdir))

load_dotenv()
# openai sk
#CHAVE
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
CHROMA_PERSIST_DIRECTORY = "dados_vetorizados_SEINFRA"

def load_xlsx_with_categories(xlsx_path):
    """
    Carrega dados do arquivo XLSX e adiciona categorias baseadas nos títulos de seção.
    """
    documents = []
    try:
        # Carregar o XLSX em um DataFrame
        df = pd.read_excel(xlsx_path, header=None)

        # Novo DataFrame para os dados estruturados
        structured_data = []
        current_cotacao = None

        for index, row in df.iterrows():
            # Identificar categorias
            if pd.isna(row[1]) and pd.isna(row[2]) and pd.isna(row[3]):
                current_cotacao = row[0].split(" / ")[1].strip() if " / " in str(row[0]) else None
            elif current_cotacao and row[0] != "Insumo":
                structured_data.append({
                    "Cotação": current_cotacao,
                    "Insumo": row[0],
                    "descrição": row[1],
                    "Unidade": row[2],
                    "Valor (R$)": row[3],
                })

        # Criar documentos
        for _, row in pd.DataFrame(structured_data).iterrows():
            insumo = row["Insumo"]
            descricao = row["descrição"]
            unidade = row["Unidade"]
            valor = row["Valor (R$)"]
            categoria = row["Cotação"]

            # Validar dados antes de criar o documento
            if pd.notna(descricao) and pd.notna(categoria):
                #  documents.append(
                #      Document(
                #          insumo=f"{insumo},{descricao}, {unidade}, {valor}, {categoria}",
                #          metadata={"source": "insumos"}
                #      )
                #  )
                documents.append([insumo, descricao, unidade, valor, categoria])

    except Exception as e:
        print(f"Erro ao processar XLSX {xlsx_path}: {e}")

    pd.DataFrame(documents).to_csv(f'final-{os.path.basename(xlsx_path)}.csv', index=False, encoding="utf-8-sig")
    return documents

def store_in_chroma(documents, collection_name):
    """
    Armazena os documentos vetorizados no ChromaDB.
    """
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large", openai_api_key=OPENAI_API_KEY)

    # Inicializar Chroma
    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=CHROMA_PERSIST_DIRECTORY,
    )

    # Limpar coleção existente
    try:
        ids = vector_store.get()["ids"]
        if ids:
            vector_store.delete(ids=ids)
            print(f"Documentos removidos da coleção '{collection_name}'.")
    except Exception as e:
        print(f"Erro ao limpar coleção '{collection_name}': {e}")

    # Adicionar novos documentos
    try:
        uuids = [str(uuid4()) for _ in range(len(documents))]
        vector_store.add_documents(documents, ids=uuids)
        print(f"{len(documents)} documentos armazenados na coleção '{collection_name}' com sucesso!")
        stored_data = vector_store.get()
        print(f"Embeddings armazenados: {stored_data['embeddings']}")
    except Exception as e:
        print(f"Erro ao armazenar documentos na coleção '{collection_name}': {e}")


def process_documents(xlsx_paths):
    """
    Processa uma lista de arquivos XLSX e os armazena no ChromaDB.
    """
    for xlsx_path in xlsx_paths:
        collection_name = os.path.splitext(os.path.basename(xlsx_path))[0]
        print(f"Processando '{xlsx_path}' na coleção '{collection_name}'...")
        documents = load_xlsx_with_categories(xlsx_path)
        print(f"Documentos extraídos: {len(documents)} entradas.")
        if documents:
            #store_in_chroma(documents, collection_name)
            print(f"Documento finalizado {collection_name}")
        else:
            print(f"Nenhum documento utilizável encontrado em '{xlsx_path}'.")


# Lista de arquivos XLSX
xlsx_paths = [
    "Tabela_de_Insumos_028___ENC_SOCIAIS_114_15_2.xlsx"
]

# Processar arquivos
process_documents(xlsx_paths)
