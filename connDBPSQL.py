# LIBS LANGCHAIN
from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine

class ConexaoDB():
    def __init__(self, username, password, host="localhost", port='5433', database='postgres'):
        # Configuração da URI de conexão
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.database = database
        self.DATABASE_URI = f'postgresql+psycopg2://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}'

    def getEngine(self):
        self.engine = create_engine(self.DATABASE_URI, connect_args={"options": "-c client_encoding=UTF8"})

        try:
            connection = self.engine.connect()
            connection.close()
            return self.engine
        except Exception as e:
            print(f"Erro na conexão: {e}")
            return e



#############################################################################################
# TESTAR SCRIPT #############################################################################
# import os 
# from sqlalchemy import text
# from dotenv import load_dotenv
# load_dotenv()

# usuario, pass_ = os.environ.get("USUARIO"), os.environ.get("PGPWD")
# database = os.environ.get("DATABASE")
# #usuario, pass_ = "postgres", "postgres"
# host = os.environ.get("HOST")
# conn = ConexaoDB(usuario, pass_, host, port='5432', database=database)
# #conn = ConexaoDB(usuario, pass_)
# engine = conn.getEngine()
# sql_query = "SELECT * FROM public.tabela_de_insumos WHERE descricao ILIKE '%SONDAGEM GEOTÉCNICA%'" 
# print(f"SQL Query Executada: {sql_query}")

# with engine.connect() as connection:
#     result = connection.execute(text(sql_query)).fetchall()      
#     print(result)
