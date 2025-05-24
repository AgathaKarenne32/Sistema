
from pydantic import BaseModel

# Classe que representa o cliente
class Cliente(BaseModel):
    name: str
    balance: float
    purchases: float
    cash_advance: float
    credit_limit: float
    payments: float

    def __str__(self):
        return f'Cliente: {self.name}'

class Resposta(BaseModel):
    nome: str
    cluster: int
    resposta: str