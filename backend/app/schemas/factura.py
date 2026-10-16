from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime

class FacturaBase(BaseModel):
    numero:str = Field(min_length=1, max_length=30)
    tipo_dte:str = Field(min_length=1, max_length=10)
    estado:str = Field(min_length=1, max_length=20)
    cliente_id:int 
    sucursal_id:int
    periodo_id:int
    asiento_id:int

class FacturaCreate(FacturaBase):
    pass

class FacturaResponse(FacturaBase):
    model_config = ConfigDict(from_attributes=True)

    id:int
    fecha:date
    creado_en:datetime
    dte_json:str


