from openai import OpenAI
import streamlit as st
#CHAVE

from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from langchain.agents import initialize_agent, Tool, AgentType

# LIBS LANGCHAIN
from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine

import psycopg2 as psy2
from langchain.chains import LLMChain
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import pandas as pd
from sqlalchemy import text
from langchain_experimental.tools import PythonAstREPLTool
import numpy as np
from langchain.output_parsers.openai_tools import JsonOutputKeyToolsParser
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_core.tools import tool
from langchain.tools.retriever import create_retriever_tool
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.callbacks import StdOutCallbackHandler

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain.agents import AgentExecutor
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

#import dspy
import openai
from openai import OpenAI

import pandas as pd
import os
import json
import hashlib
from tqdm import tqdm
import chromadb
#import weaviate
#from dspy.retrieve.weaviate_rm import WeaviateRM
import uuid

import base64
import requests

import tiktoken
encoding = tiktoken.get_encoding("cl100k_base")
encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
from dotenv import load_dotenv
#import logging
#logging.basicConfig(level=logging.DEBUG)
import logging
from hashlib import sha256
from time import time
from datetime import datetime

from xtractaVision import XtractaVision
import connDBPSQL
from buscador import Buscador

# DSECRET KEY diretamente no arquivo .ENV
load_dotenv()
# Certifique-se de que a chave da API seja configurada como variável de ambiente
secretk = os.environ.get("OPENAI_API_KEY")
openai.api_key = secretk
# Configurando o modelo de linguagem com LangChain
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

try:
    # Configurando o modelo de linguagem (por exemplo, GPT-4)
    llm = ChatOpenAI(model="gpt-4o-2024-11-20", temperature=0.4, max_tokens=4096)
    print("Modelo configurado com sucesso.")
except Exception as e:
    print(f"Erro ao configurar o modelo: {e}")


# VAMOS TROCAR POR SESSION...

def data_legivel():
    data_legivel = datetime.fromtimestamp(datetime.timestamp(datetime.now())).strftime('%Y-%m-%d %H:%M:%S')
    return data_legivel, f"Data e hora do inicio da conversa: {data_legivel}"

hash_id = ''
def conversaID():
    # DATACAO E HASH ID PARA SESSION E HISTORICO DE CONVERSAS
    datalegivel, _ = data_legivel()
    hash_id = hashlib.sha256(datalegivel.encode('utf-8')).hexdigest()  # Gera o hash usando SHA-256

    return hash_id[1]
    
##### CAIXA DE FERRAMENTAS ##################################################################
# Função para usar o retriever como uma ferramenta
@tool
def buscar_documento_PLANOSSERVICOS(query: str) -> Tool:
    """
        Query and compare unit prices from the Input Table of the Ceará State Infrastructure Secretariat (Seinfra).
    
        This function retrieves data from the Input Table.
        Users can query items by code to obtain regulated prices and compare them with budgeted values, ensuring compliance and effective cost control.
        
        Args:
            item_code (str): The code identifying the input item, such as "C2820", representing specific 
            materials, labor, or equipment from the Input Table.
            
            budgeted_value (float): The project’s budgeted unit price for the input, to be compared 
            with the regulated price from the Input Table.
        
        Returns:
            dict: Includes the regulated unit price (`input_price`), the budgeted price (`budgeted_price`), 
            the price difference (`difference`), and a `status` indicating if the budgeted price is "Above", "Below", or "Within Range".
        Important:    
            Read the provided work instructions and extract all the details about the requested topic. Do not summarize or exclude any related information.

    """

    # libraries
    from langchain_chroma import Chroma
    from langchain_openai import OpenAIEmbeddings
    from langchain_text_splitters import CharacterTextSplitter
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_community.document_loaders.merge import MergedDataLoader
    from langchain.chains.combine_documents import create_stuff_documents_chain
    from langchain_core.prompts import ChatPromptTemplate
    from langchain.chains import create_retrieval_chain,  RetrievalQA
    
    diretorio = "dados_vetorizados_SEINFRA"
    chromadb_ = Chroma(collection_name="planos_de_servicos_028___ENC_SOCIAIS_114_15", embedding_function=OpenAIEmbeddings(), persist_directory=diretorio)

    retriever = chromadb_.as_retriever(search_type="similarity", search_kwargs={"k":5})
    qa_chain = RetrievalQA.from_chain_type(
        llm=OpenAI(), retriever=retriever, return_source_documents=True
    )
    
    results = qa_chain.run(query)

    #results = retriever_.invoke(query)
    # If no results are found, provide a message indicating that
    
    if not results:
        return "No relevant documents were found for the provided query."

    # Format the results and return them
    formatted_results = "\n\n".join([doc.page_content for doc in results])
    return formatted_results

# Função para usar o retriever como uma ferramenta
@tool
def buscar_documento_TABELA_INSUMOS(sql_query: str) -> str:

    """
        This agent always performs SQL SELECT queries from the Seinfra table 'public.tabela_de_insumos' to analyze data inputs.

        Columns:
            "insumo": input's id (e.g., I7406)
            "descricao": input's description
            "unidade": unit measure data(e.g., UN, M)
            "valor": input's value
            "categoria": input's category 

        NOTICE:
            Use double quotes for column names only.
            Do not use double quotes for table names or schema names. Example: Use `public.tabela_de_insumos`
            Return only data that exists in the database.

        GUIDELINES:
            This function compares contractor-provided input prices with Seinfra's regulated prices, using both input codes and descriptions. 
            The agent analyzes the provided data, verifies values, calculates differences, and flags discrepancies.
            If the query returns no results, the agent must:
                - Perform **orthographic correction** (including restoring accents like é, ã, ç) to align Brazil's grammar and retry the search.
            Always answer in table format when possible.

    """
    import pandas as pd
    from sqlalchemy import text
    from connDBPSQL import ConexaoDB
    load_dotenv()
    usuario, pass_ = os.environ.get("USUARIO"), os.environ.get("PGPWD")
    database = os.environ.get("DATABASE")
    #usuario, pass_ = "postgres", "postgres"
    host = os.environ.get("HOST")
    conn = ConexaoDB(usuario, pass_, host, port='5432', database=database)
    #conn = ConexaoDB(usuario, pass_)
    engine = conn.getEngine()
    print(f"SQL Query Executada: {sql_query}")

    try:
        with engine.connect() as connection:
            # Executar a query e obter os dados
            result = connection.execute(text(sql_query)).fetchall()         
            # Processar o resultado como um DataFrame para facilitar o retorno
            df = pd.DataFrame(result) if result else pd.DataFrame()
            return df.to_dict(orient="records")  # Retorna um JSON estruturado

    except Exception as e:
        return f"Erro ao consultar os dados: {e}"

@tool
def buscar_documento_COMPOSICOES(query: str) -> Tool:
    """
        Retrieve and process composition data for the Ceará State Infrastructure Secretariat (Seinfra).
    
        This function manages composition data for Seinfra, overseeing areas like transport, 
        logistics, urban mobility, and energy. Compositions are regulatory tools used to 
        supervise construction projects and assign monetary values based on standards in the 
        composition tables.
        
        Args:
            composition_id (str): Identifier linking specific construction tasks to regulatory 
            values in the composition table.
            
            query_details (dict): Information about the construction project, including type, 
            location, and costs, for accurate composition data retrieval.
        
        Returns:
            dict: Contains composition details such as description, values, and regulatory requirements. 
            Returns a default response if no matching composition is found.
    """


    # libraries
    from langchain_chroma import Chroma
    from langchain_openai import OpenAIEmbeddings
    
    diretorio = "dados_vetorizados"
    chromadb_ = Chroma(collection_name="composicoes_028___ENC_SOCIAIS_114_15", embedding_function=OpenAIEmbeddings(), persist_directory=diretorio)

    results = chromadb_.similarity_search(
        query=query
    )
    
    #results = retriever_.invoke(query)
    # If no results are found, provide a message indicating that
    
    if not results:
        return "No relevant documents were found for the provided query."

    # Format the results and return them
    formatted_results = "\n\n".join([doc.page_content for doc in results])
    return formatted_results

# Função para usar o retriever como uma ferramenta
@tool
def pesquisa_web(query: str) -> Tool:
    """
        This tool automates the process of retrieving information from Google searches and accessing specific websites. 
        It intelligently performs a Google search, retrieves relevant links, accesses them, and extracts the content found.

        Capabilities:
            - Perform Google searches for specific topics or queries.
            - Access websites directly from the search results and extract their content.
            - Summarize the extracted content or provide relevant details for the user query.

        **Important**: It adheres to legal restrictions, avoiding searches or content related to prohibited topics under Brazilian law.

        Functions:
            * buscador.buscarGoogle(query): Searches Google based on the user query and retrieves relevant links.
            * buscador.acessarWebsite(link): Accesses the specified link and extracts content.

        Args:
            query (str): The search phrase or website URL.

        Returns:
            str: A summary or detailed information extracted from the target website or search results.
    """

    buscador = Buscador()

    if "google":
        resultado = buscador.buscarGoogle(query)
    elif "website":
        resultado = buscador.buscarWebsite(query)
    else:
        resultado = "Tente explicar melhor qual o tipo de pesquisa deseja fazer."
    
    return resultado
    
@tool
def extrair_dados_documento(image_path: str) -> str:
    """
    Workflow Overview: Captures product names and quantities from images or PDFs for use in a construction materials store. 
    The process involves converting images to base64 or extracting text from PDFs to generate purchase lists ALWAYS USE XtractaVision.

    ATTENTION: 
            NEVER EVER USE OpenAI for this task.

    Arguments:
        image_path (str): Path to the image or PDF containing the item list.

    Returns:
        * PRODUCT_NAMES: Names of products extracted from the document.
        * QUANTITIES: Quantities for each product, if available.
        * RAW_TEXT: Full extracted text for reference.

    User Interaction:
        * Users may specify whether they need product details or total quantities.
        * Ensure accurate recognition of product names and quantities for effective stock management.

    Additional Context:
        Designed to assist inventory management in a construction materials store by streamlining purchase entries and restocking.
    """

    # CHAMANDO A CLASSE DE EXTRACAO 
    extrator = XtractaVision(secretk, llm)
    texto = extrator.Xtracta(image_path)
    
    return texto

@tool
def validar_e_melhorar_resultados(resultados: str) -> str:
    """
    Ferramenta para validar e melhorar a apresentação de resultados.
    - Detecta inconsistências.
    - Propõe melhorias, como reorganização em tabelas ou gráficos.
    - Expõe uma análise crítica da clareza e relevância.
    """

    import pandas as pd
    import json

    feedback = []

    # Validação inicial
    if not resultados.strip():
        return "⚠️ Os resultados estão vazios. É necessário revisá-los."

    # Tentar converter resultados para uma estrutura manipulável (JSON/Tabela)
    try:
        if resultados.startswith("{") or resultados.startswith("["):
            # Assumindo que os dados podem ser JSON
            data = json.loads(resultados)
            df = pd.DataFrame(data)
            feedback.append("✅ Dados convertidos para tabela com sucesso.")
            feedback.append(df.to_string(index=False))
        else:
            feedback.append("ℹ️ Os resultados estão em texto livre. Considere estruturá-los em tabelas.")
    except Exception:
        feedback.append("⚠️ Não foi possível converter os resultados para uma tabela. Verifique o formato.")

    # Análise crítica
    feedback.append("📋 Análise crítica:")
    if len(resultados.split()) < 50:
        feedback.append("🔍 Os resultados parecem breves. Considere adicionar mais detalhes.")
    elif len(resultados.split()) > 300:
        feedback.append("🔍 Os resultados são extensos. Avalie se podem ser resumidos.")
    else:
        feedback.append("🔍 O volume dos resultados parece adequado.")

    # Retornar o feedback formatado
    return "\n".join(feedback)


##### FINAL DE CAIXA DE FERRAMENTAS #########################################################
##### CONEXAO COM A CAIXA DE FERRAMENTAS, CRIACAO DE CHAT_HISTORY LIST E A FUNCAO DE EXTENDER BATE PAPO :) ...
# Conexão com ferramentas principais
tools = [
    buscar_documento_TABELA_INSUMOS,
    pesquisa_web,
    extrair_dados_documento
]
llmtools = llm.bind_tools(tools)

# Conexão com ferramentas do validador
tools_val = [validar_e_melhorar_resultados]
llmtools_val = llm.bind_tools(tools_val)

#### Busca no historico
def buscar_no_historico(chat_history, chave):
    """
    Busca informações específicas no histórico do agente.
    """
    for mensagem in chat_history:
        if isinstance(mensagem, dict) and chave in mensagem:
            return mensagem[chave]
    return None

# Agente Validador
def agenteValidador(resultado_agente_1, chat_history):
    prompt_validador = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                Você é um agente reflexivo responsável por validar a saída da ferramenta 'buscar_documento_TABELA_INSUMOS'.
                Sua tarefa é analisar a saída fornecida, identificar erros ou inconsistências, e sugerir melhorias ou correções.
                Realize o raciocínio passo a passo para justificar suas decisões. Reflita sobre cada etapa e inclua ações sugeridas antes de fornecer a validação final.
                """
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    agent_validador = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_to_openai_tool_messages(
                x["intermediate_steps"]
            ),
            "chat_history": lambda x: x["chat_history"],
        }
        | prompt_validador
        | llmtools_val
        | OpenAIToolsAgentOutputParser()
    )

    agent_executor_validador = AgentExecutor(agent=agent_validador, tools=tools_val, verbose=True)

    try:
        resultado = agent_executor_validador.invoke(
            {"input": resultado_agente_1, "chat_history": chat_history}
        )
        return resultado['output']
    except Exception as e:
        print(f"ERRO NO AGENTE VALIDADOR: {e}")
        return "Erro no agente validador."

def agenteValidadorReAct(resultado_agente_1, chat_history):
    """
    Agente reAct: Valida e melhora os resultados com base em reflexão e iteração.
    Usa dados previamente armazenados no histórico para evitar redundâncias.
    """

    # Verificar se a validação já foi realizada no histórico
    validacao_previa = buscar_no_historico(chat_history, "validacao")
    if validacao_previa:
        logging.info("Validação já realizada previamente. Reutilizando dados do histórico.")
        return validacao_previa

    # Prompt atualizado
    prompt_validador = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                Você é um agente reflexivo e crítico. Sua tarefa é:
                1. Validar os resultados fornecidos.
                2. Propor melhorias na apresentação, como tabelas ou gráficos.
                3. Fornecer análises críticas sobre a clareza e relevância dos dados.
                Reutilize informações disponíveis no histórico sempre que possível.
                """
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "Por favor, valide e melhore os seguintes resultados: {input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    # Configuração do agente
    agent_reAct = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_to_openai_tool_messages(
                x["intermediate_steps"]
            ),
            "chat_history": lambda x: x["chat_history"],
        }
        | prompt_validador
        | llmtools_val
        | OpenAIToolsAgentOutputParser()
    )

    agent_executor_validador_react = AgentExecutor(
        agent=agent_reAct, tools=tools_val, verbose=True
    )

    # Processo iterativo
    try:
        reflexoes = []
        resultado_atual = resultado_agente_1

        for iteracao in range(3):  # Limitar iterações
            logging.info(f"[Iteração {iteracao + 1}] Validando resultado: {resultado_atual}")

            # Invocar a tool para validar
            reflexao = agent_executor_validador_react.invoke(
                {"input": resultado_atual, "chat_history": chat_history}
            )

            # Registrar no histórico
            chat_history.append({"validacao": reflexao["output"]})

            # Verificar se os resultados estão validados
            if "validado com sucesso" in reflexao["output"].lower():
                logging.info("Resultados validados com sucesso.")
                return reflexao["output"]

            # Atualizar resultado atual
            resultado_atual = reflexao["output"]
            reflexoes.append(reflexao["output"])

        # Após 3 iterações, retornar último resultado
        logging.warning("Validação incompleta após 3 tentativas.")
        return f"Validação incompleta. Última reflexão: {reflexoes[-1]}"

    except Exception as e:
        logging.error(f"Erro no agente validador: {e}")
        return f"Erro ao validar os resultados: {e}"

# TRABALHANDO O CACHE PARA TOKENS
# CRIANDO CARREGANDO OS TOKENS
#######################################################################################################
# Carregar cache de arquivo
CACHE_FILE = "token_cache.json"
def carregar_cache():
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}  # Se o arquivo não existir, retorna um cache vazio

# Inicializar cache
token_cache = carregar_cache()

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

# Agente Principal
def agenteIA(usuario_prompt, hash_id, chat_history):

    # Verificar tokens no cache
    tokens_existentes = buscar_tokens_no_cache(usuario_prompt)
    if tokens_existentes:
        logging.info("Tokens encontrados no cache para o agente principal.")
    else:
        logging.info("Tokens não encontrados no cache. Tokenizando...")


    MEMORY_KEY = "chat_history"
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                AIsten é um assistente digital poderoso desenvolvido por Thiago Bluhm para apoiar as operações da Secretaria de Infraestrutura do Ceará (Seinfra).
                Projetado especificamente para as necessidades da Seinfra, o AIsten gerencia e analisa dados relacionados a projetos de infraestrutura,
                fornecendo insights e executando tarefas de forma eficiente.
                """
            ),
            MessagesPlaceholder(variable_name=MEMORY_KEY),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    agent = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_to_openai_tool_messages(
                x["intermediate_steps"]
            ),
            MEMORY_KEY: lambda x: x[MEMORY_KEY],
        }
        | prompt
        | llmtools
        | OpenAIToolsAgentOutputParser()
    )

    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    try:
        resultado = agent_executor.invoke(
            {"input": usuario_prompt, "chat_history": chat_history}
        )
        return resultado['output']
    except Exception as e:
        print(f"ERRO NO AGENTE PRINCIPAL: {e}")
        return "Erro no agente principal."

# Fluxo atualizado para incluir o agente reflexivo
def fluxoDeAgentes(usuario_prompt, chat_history):
    # Verificar se a resposta já está no histórico
    resposta_previa = buscar_no_historico(chat_history, usuario_prompt)
    if resposta_previa:
        logging.info("Resposta encontrada no histórico. Reutilizando dados.")
        return resposta_previa

    # Agente Principal
    resultado_agente_1 = agenteIA(usuario_prompt, hash_id="hash1", chat_history=chat_history)
    chat_history.append({"usuario": "role", "content": usuario_prompt})

    # Agente Validador
    resultado_validador = agenteValidadorReAct(resultado_agente_1, chat_history)
    chat_history.append({"validacao": resultado_validador})

    # Sugerir ações baseadas no contexto
    if "diferença significativa" in resultado_validador.lower():
        sugestoes = (
            "Percebi que há diferenças significativas nos valores. "
            "Gostaria de saber mais sobre os itens com maior discrepância?"
        )
        chat_history.append({"sugestao": sugestoes})
        return {"resposta": resultado_validador, "sugestao": sugestoes}

    return resultado_validador

# # Execução
# if __name__ == "__main__":
#     usuario_prompt = "Buscar documento na tabela de insumos contendo erro para validação."
#     chat_history = []

#     resultado_final = fluxoDeAgentes(usuario_prompt, chat_history)
#     print(f"Resultado Final: {resultado_final}")

