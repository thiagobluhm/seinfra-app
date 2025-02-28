import bs4
from langchain_community.document_loaders import WebBaseLoader

class Buscador:
    def __init__(self):
        pass

# Função para carregar conteúdo de um site usando WebBaseLoader
    def load_website_content(self, url):
        try:
            loader = WebBaseLoader(url)
            return loader.load()
        except Exception as e:
            print(f"Erro: {e}")
            return None

    def buscarGoogle(self, consulta):
        pesquisa = consulta.replace(" ", "+")
        # Lista de URLs que você deseja processar
        url = f"https://www.google.com.br/search?q={pesquisa}"  

        try:  
            # Processa todas as URLs e armazena o conteúdo
            sitedados = self.load_website_content(url)
            return sitedados
        except Exception as e:
            print(f"Nenhuma informacao foi capturada.")
            return None
        
    def buscarWebsite(self, url):
        try:  
            # Processa todas as URLs e armazena o conteúdo
            url_ = f"https://www.{url}"
            sitedados = self.load_website_content(url_)
            return sitedados
        
        except Exception as e:
            sitedados = "Resultado: Nenhuma informacao foi capturada."
            return sitedados


b = Buscador()
print(b.buscarWebsite("difusar.com.br/grelha-para-insuflamento.php"))