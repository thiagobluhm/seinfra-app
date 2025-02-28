from transformers import CLIPProcessor, CLIPModel, CLIPTokenizer
from PIL import Image
import os 
os.chdir(os.path.abspath(os.curdir))
import torch

class ValidatorVITImgTexto:
    # def __init__(self):
    #     # Carregar o modelo CLIP
    #     self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14", force_download=True)
    #     self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14", force_download=True)
    #     self.tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-large-patch14")  # Adiciona o tokenizer oficial
    def __init__(self, model_path="openai/clip-vit-large-patch14"):
        """
        Inicializa o validador e carrega o modelo CLIP de um caminho local se disponível.
        Caso contrário, tenta baixar.
        """
        # Verifica se o modelo local existe
        if os.path.exists(model_path):
            print("✅ Modelo encontrado localmente. Carregando...")
            self.clip_model = CLIPModel.from_pretrained(model_path)
            self.clip_processor = CLIPProcessor.from_pretrained(model_path)
            self.tokenizer = CLIPTokenizer.from_pretrained(model_path)
        else:
            print("🔽 Modelo não encontrado. Tentando baixar e salvar no diretório...")
            self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14", cache_dir=model_path)
            self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14", cache_dir=model_path)
            self.tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-large-patch14", cache_dir=model_path)

    #@staticmethod
    def truncate_text(self, text, max_length=77):
        """
        Trunca o texto garantindo que ele tenha no máximo `max_length` tokens, usando o tokenizer do CLIP.
        """
        tokens = self.tokenizer(text, truncation=True, max_length=max_length, return_tensors="pt")
        return self.tokenizer.decode(tokens["input_ids"][0], skip_special_tokens=True)  # Converte tokens de volta para string

    def get_top_k_texts(self, image, texts, k=3):
        """
        Retorna os `k` textos mais relevantes para a imagem com base nas pontuações do CLIP.
        """
        relevance_scores = []
        for text in texts:
            relevance_score = self.validate(image, text)
            relevance_scores.append((text, relevance_score))

        # Ordenar por relevância em ordem decrescente
        relevance_scores.sort(key=lambda x: x[1], reverse=True)

        # Retornar os top-k textos
        return relevance_scores[:k]

    def validate(self, image, descricao):
        """
        Usa CLIP para validar a relevância da imagem com relação ao texto.
        """
        descricao_truncada = self.truncate_text(descricao)

        # Abrir a imagem, se necessário
        if isinstance(image, str):  # Caminho da imagem
            image = Image.open(image)

        # Preparar os dados para o modelo CLIP
        inputs = self.clip_processor(text=[descricao_truncada], images=image, return_tensors="pt", padding=True)

        # Verificando as dimensões antes de rodar o modelo
        print(f"Tamanho do input_ids: {inputs['input_ids'].shape}")  # Deve ser (1, <=77)

        # Fazer a inferência com o modelo CLIP
        outputs = self.clip_model(**inputs)
        logits_per_image = outputs.logits_per_image  # Similaridade entre imagem e texto
        probabilities = torch.softmax(logits_per_image, dim=1)  # Converter em probabilidades

        relevance_score = probabilities[0][0].item()  # Pontuação de relevância
        return relevance_score
