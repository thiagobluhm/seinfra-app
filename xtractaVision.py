import base64
import requests
import pymupdf  # PyMuPDF

class XtractaVision:
    def __init__(self, skopenai, llm):
        self.secretk = skopenai
        self.llm = llm
        self.textos = []

    # Function to encode the image
    def encode_image(self, image):
        """
        Converts an image file to a base64 encoded string.

        Args:
            image (str): Path to the image file.

        Returns:
            str: Base64 encoded string of the image.
        """
        with open(image, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def extract_text_from_pdf(self, pdf_path):
        """
        Extracts text from a PDF file.

        Args:
            pdf_path (str): Path to the PDF file.

        Returns:
            str: Extracted text from the PDF.
        """

        text = ""
        with pymupdf.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
        return text

    def XtractaVisionII(self, file_path):
        """
        Extracts text from an image or PDF using OpenAI Assistant and the GPT-4o-mini model.

        Args:
            file_path (str): Path to the image or PDF file.

        Returns:
            list: Extracted texts from the file.
        """
        try:
            # Check if the file is a PDF
            if file_path.lower().endswith('.pdf'):
                
                extracted_text = self.extract_text_from_pdf(file_path)
                self.textos.append(extracted_text)
                return self.textos
            
            # If it's not a PDF, assume it's an image
            else:
                # Getting the base64 string
                
                base64_image = self.encode_image(file_path)

                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.secretk}"
                }

                payload = {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": """
                                        Você é um excelente analista financeiro e muito detalhista. Sua tarefa é ler documentos 
                                        que são passados para você e retirar as principais informações contidas neles.
                                        Responda apenas com o texto extraído. Não invente nada. Responda em português do Brasil.
                                    """
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    "max_tokens": 500
                }

                response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                resp = response.json()
                self.textos.append(resp['choices'][0]['message']['content'])

                return self.textos
        
        except Exception as e:
            print(f"ERRO: {e}")
            return e
        

    def Xtracta(self, image):
        return self.XtractaVisionII(image)