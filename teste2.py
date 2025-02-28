# from langchain_community.document_loaders import PyPDFDirectoryLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.llms import OpenAI
# #from langchain.vectorstores import Pinecone
# from langchain.chains import RetrievalQA
# from langchain.prompts import PromptTemplate
# from langchain_community.vectorstores import Chroma
# import os
# from langchain_openai import ChatOpenAI
# from langchain_community.llms import OpenAI
# # libraries
# from langchain_text_splitters import CharacterTextSplitter
# from langchain_community.embeddings import OpenAIEmbeddings
# from langchain_community.document_loaders import PyPDFLoader
# from langchain_community.document_loaders.merge import MergedDataLoader
# from langchain.chains.combine_documents import create_stuff_documents_chain
# from langchain_core.prompts import ChatPromptTemplate
# from langchain.chains import create_retrieval_chain,  RetrievalQA
# from chromadb.config import Settings
# from chromadb import Client
# from dotenv import load_dotenv
# import openai
import os
# from langchain.document_loaders import PyPDFDirectoryLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.vectorstores import Chroma
# import pandas as pd

# os.chdir(os.path.abspath(os.curdir))

# df = pd.read_csv('Tabela_de_Insumos_028___ENC_SOCIAIS_114_15_2.xlsx.csv')
# print(df.loc[:1, '2'])



# # DSECRET KEY diretamente no arquivo .ENV
# load_dotenv()
# # Certifique-se de que a chave da API seja configurada como variável de ambiente
# secretk = os.environ.get("OPENAI_API_KEY")
# openai.api_key = secretk
# # Configurando o modelo de linguagem com LangChain
# client = OpenAI(api_key=secretk)
# llm = ChatOpenAI(model="gpt-4o", temperature=0.1, max_tokens=2048)

# # # Diretório onde estão os PDFs
# pdf_directory = "pdfs_"
# persist_directory = "dados_vetorizados_SEINFRA" # Diretório para persistência do banco ChromaDB

# # # Configuração da Função de Embedding
# embedding_function = OpenAIEmbeddings(
#      model="text-embedding-3-large",
#      openai_api_key=secretk  # Substitua pela sua chave OpenAI
#  )

# Carregar documentos do diretório
# loader = PyPDFDirectoryLoader(pdf_directory)
# documents = loader.load()

# # Evitar repetição de arquivos
# unique_files = set()

# # Processar cada documento
# print("Iniciando o processamento dos PDFs...\n")

# for doc in documents:
#     source = doc.metadata['source']
#     filename = os.path.basename(source)  # Nome do arquivo
#     collection_name = os.path.splitext(filename)[0]  # Remove a extensão .pdf

#     # Evitar processar o mesmo arquivo mais de uma vez
#     if collection_name in unique_files:
#         print(f"Arquivo '{filename}' já foi processado. Ignorando...\n")
#         continue

#     print(f"Processando arquivo: {source}")
#     print(f"Collection: {collection_name}")

#     # Adicionar o arquivo processado ao conjunto de arquivos únicos
#     unique_files.add(collection_name)

#     # Dividir o documento em chunks
#     text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#     text_chunks = text_splitter.split_documents([doc])

#     print(f"Total de chunks criados: {len(text_chunks)}")

#     # Criar uma collection no ChromaDB
#     Chroma.from_documents(
#         documents=text_chunks,
#         embedding=embedding_function,
#         collection_name=collection_name,
#         persist_directory=persist_directory
#     )

#     print(f"Collection '{collection_name}' criada com sucesso!\n")

# print("Processamento concluído. Todas as collections foram criadas!")

# # Consulta (query)

# vectordb = Chroma(
#         collection_name="Tabela_de_Insumos_028___ENC_SOCIAIS_114_15",
#         embedding_function=embedding_function,
#         persist_directory=persist_directory,
#     )

# # retriever = vectordb.as_retriever(search_kwargs={"k": 10})
# # simple_query = "SERVIÇOS DE SONDAGEM GEOTÉCNICA MISTA EM ROCHA"
# # results = retriever.get_relevant_documents(simple_query)
# # for doc in results:
# #     print(f"\n{doc.page_content}\n{'*'*80}\n")

# results = vectordb.similarity_search(
#     query="SERVIÇOS DE SONDAGEM", k=5
# )
# print("Resultados encontrados:")
# for i, doc in enumerate(results):
#     print(f"Documento {i+1}:\n{doc.page_content}\n{'-'*80}")

# # Caminho para salvar txt
# output_file = "dados_extraidos_chromadb.txt"

# # Recuperar todos os documentos da collection
# all_docs = vectordb.get()["documents"]

# # Salvar os documentos em um arquivo TXT
# with open(output_file, "w", encoding="utf-8") as f:
#     for i, doc in enumerate(all_docs):
#         f.write(f"Documento {i+1}:\n{doc}\n{'-'*80}\n")

# print(f"Todos os dados da collection Tabela_de_Insumos_028___ENC_SOCIAIS_114_15 foram salvos em '{output_file}'.")


# query = """preciso que consulte a tabela de insumos e traga informacoes sobre o SERVIÇOS DE SONDAGEM GEOTÉCNICA MISTA EM ROCHA, 
#            preciso obter informacoes sobre este insumo e similares a ele."""

# # Criar um retriever
# retriever = vectordb.as_retriever(search_kwargs={"k": 3})  # Retornar os 5 resultados mais relevantes

# # Criar a cadeia para responder às perguntas
# qa_chain = RetrievalQA.from_chain_type(
#     llm=llm,
#     chain_type="refine",  # Estratégia de recuperação: map_reduce para processar documentos longos
#     retriever=retriever,
#     return_source_documents=True  # Retorna os documentos de origem
# )

# # Função para formatar a resposta do LLM
# def process_llm_response(llm_response):
#     print("\n**Resposta:**\n")
#     print(llm_response['result'])  # Resposta do modelo
#     print('\n**Fontes:**\n')
#     for source in llm_response["source_documents"]:
#         print(f"- {source.metadata['source']}")  # Mostra a origem dos documentos utilizados

# # # Executar a consulta e processar a resposta
# llm_response = qa_chain.invoke({"query": query})  # Passa a query para a chain
# process_llm_response(llm_response)


import pandas as pd
from sqlalchemy import text
from connDBPSQL import ConexaoDB
import unicodedata
from dotenv import load_dotenv


load_dotenv()

usuario, pass_ = os.environ.get("USUARIO"), os.environ.get("PGPWD")
host = os.environ.get("HOST")
database = 'seinfra'
conn = ConexaoDB(usuario, pass_, host, port='5432', database=database)
engine = conn.getEngine()


# Verificar se a engine foi criada com sucesso
if engine:
    try:
        with engine.connect() as connection:
            # Query parametrizada para evitar SQL Injection
            query = text("SELECT * FROM public.tabela_de_insumos WHERE insumo = :insumo")
            params = {"insumo": "I2505"}  # Parâmetro seguro
            result = connection.execute(query, params)

            # Processar os resultados em um DataFrame
            df = pd.DataFrame(result.fetchall(), columns=result.keys()) if result else pd.DataFrame()
            
            # Imprimir os resultados no formato JSON estruturado
            print(df.to_dict(orient="records"))

    except Exception as e:
        print(f"Erro ao consultar os dados: {e}")
else:
    print("Não foi possível estabelecer conexão com o banco de dados.")