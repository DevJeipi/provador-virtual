import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import fal_client
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

# Configuração de CORS (Permite que sua loja Shopify acesse este backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://shallow.com.br"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de dados que vamos receber
class TryOnRequest(BaseModel):
    human_image_url: str  # Foto do cliente (já hospedada)
    garment_image_url: str # Foto do produto (da Shopify)
    description: str = "clothing" # Descrição opcional

@app.post("/generate")
async def generate_tryon(request: TryOnRequest):
    try:
        print("Recebendo pedido...")
        
        # Envia para a fal.ai usando o modelo Cat-VTON (ótimo custo-benefício)
        handler = await fal_client.submit_async(
            "fal-ai/cat-vton",
            arguments={
                "human_image_url": request.human_image_url,
                "garment_image_url": request.garment_image_url,
                "cloth_type": "upper", # Pode ser 'upper', 'lower' ou 'overall'
                # Dica: Você pode passar isso dinamicamente do frontend
            },
        )

        # Aguarda o resultado
        result = await handler.get()
        
        # O resultado vem como um dicionário com a URL da imagem
        print(f"Gerado: {result}")
        return result

    except Exception as e:
        print(f"Erro: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)