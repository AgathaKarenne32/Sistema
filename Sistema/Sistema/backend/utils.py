from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

# Função para converter os dados para o formato usado na comunicação entre os endpoints
def jsonc(item, cod=200):
    jcomp = jsonable_encoder(item)
    return JSONResponse(
        content=jcomp,
        media_type="application/json",
        status_code=cod
    )