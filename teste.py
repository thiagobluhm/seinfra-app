from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
import os
from langchain_openai import ChatOpenAI
from openai import OpenAI
# libraries
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
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

#CHAVE
# DSECRET KEY diretamente no arquivo .ENV
load_dotenv()
# Certifique-se de que a chave da API seja configurada como variável de ambiente
secretk = os.environ.get("OPENAI_API_KEY")
openai.api_key = secretk
# Configurando o modelo de linguagem com LangChain
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Configurando o modelo de linguagem (por exemplo, GPT-4)
llm = ChatOpenAI(model="gpt-4o", temperature=0.4, max_tokens=2048)

# # Diretório onde os dados persistidos estão armazenados
# persist_directory = "dados_vetorizados_SEINFRA"

# # Conectar ao ChromaDB
# vectorstore = Chroma(
#     #collection_name="planos_de_servicos_028___ENC_SOCIAIS_114_15",
#     embedding_function=OpenAIEmbeddings(),
#     persist_directory=persist_directory
# )

# # Listar todas as collections
# client = vectorstore._client  # Acessa o cliente Chroma subjacente
# collections = client.list_collections()


# # Exibir o nome das collections disponíveis
# if collections:
#     print("Collections disponíveis no ChromaDB:")
#     for collection in collections:
#         print(f"- {collection.name}")
# else:
#     print("Nenhuma collection foi encontrada.")


diretorio = "dados_vetorizados_SEINFRA"
embedding_function = OpenAIEmbeddings(
    model="text-embedding-3-large",  # Nome do modelo
    openai_api_key=secretk  # Substitua pela sua chave da OpenAI
)
chromadb_ = Chroma(collection_name="Tabela_de_Insumos_028___ENC_SOCIAIS_114_15", 
                   embedding_function=embedding_function, 
                   persist_directory=diretorio)

retriever = chromadb_.as_retriever(search_type="similarity", 
                                   search_kwargs={"k":5}
                                   )
qa_chain = RetrievalQA.from_chain_type(
    llm=llm, retriever=retriever, return_source_documents=True
)
query = """preciso que consulte a tabela de insumos e traga informacoes sobre o serviço de SONDAGEM GEOTÉCNICA MISTA EM SOLOS, 
           preciso obter informacoes sobre este insumo e similares a ele. Coloque em tabela."""
results = qa_chain.invoke({"query": query})  
# Processar os resultados
if not results['source_documents']:
    print("No relevant documents were found for the provided query.")
else:
    # Formatar os resultados e exibi-los
    print("Result:")
    print(results['result'])  # Resposta gerada pelo LLM
    print("\nSource Documents:")
    for doc in results['source_documents']:
        print(doc.page_content)  # Conteúdo de cada documento recuperado


# # Format the results and return them
# formatted_results = "\n\n".join([doc.page_content for doc in results])

# Formatando os resultados
# formatted_results = []
# for doc in results:
#     metadata = doc.metadata
#     content = f"""
#                 Description: {doc.page_content.strip()}
#                 Code: {metadata.get("code", "N/A")}
#                 Unit: {metadata.get("unit", "N/A")}
#                 Value: {metadata.get("value", "N/A")}
#                 Category: {metadata.get("category", "N/A")}
#                 Source: {metadata.get("source", "N/A")}
#               """
#     formatted_results.append(content.strip())

# r = ", ".join(formatted_results)
# print(r)

# if __name__ == "__main__":
#     prompt = "verifique e traga informacoes da tabela de insumos sobre SONDAGEM GEOTECNICA MISTA"
#     session_id = "12345"
#     chat_history = [
#         {"role": "user", "content": "Olá!"},
#         {"role": "assistant", "content": "Como posso ajudar você?"}
#     ]

#     # Teste do agente
#     try:
#         resposta = agenteIA(prompt, session_id, chat_history)
#         print("Resposta do agente:", resposta)
#     except Exception as e:
#         print("Erro ao processar agente:", e)


# Inicializa o Chroma client no diretório
chromadb_client = Chroma(persist_directory=diretorio)

# Lista as coleções disponíveis
collections = chromadb_client.list_collections()
print("Collections disponíveis:", collections)
