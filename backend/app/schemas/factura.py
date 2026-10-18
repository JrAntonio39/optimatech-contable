from pydantic import BaseModel, Field
import uuid

class IdentificacionFactura(BaseModel):
    version: int = 2
    ambiente: str 
    tipoDte: str    
    numeroControl: str    
    codigoGeneracion: str = Field(default_factory=lambda: str(uuid.uuid4()).upper())
    tipoModelo: int
    tipoOperacion: int
    tipoContingencia: str | None = None
    motivoContin: str | None = None
    fechaEmi: str 
    horaEmi: str 
    tipoMoneda: str

class ItemFactura(BaseModel):
    numItem: int
    tipoItem: int
    numDocumento: int | None = None
    cantidad: int 
    codigo: str
    codTributo: str | None = None
    uniMedida: int
    descripcion: str
    precioUni: float
    montoDescu: float = 0.00
    ventaNoSuj: float = 0.00
    ventaExenta: float = 0.00
    ventaGravada: float
    tributos: dict | None = None 
    psv: float = 0.00
    noGravado: float = 0.00
    ivaItem: float

class DireccionParticipante(BaseModel):
    departamento: str 
    municipio: str 
    distrito: str 
    complemento: str 

class ParticipanteFactura(BaseModel):
    nit: str | None = None 
    nrc: str 
    nombre: str
    codActividad: str 
    descActividad: str 
    direccion: DireccionParticipante
    telefono: str 
    correo: str 

class EmisorFactura(ParticipanteFactura):
    nombreComercial: str 
    codEstable: str | None = None 
    codPuntoVenta: str | None = None     

class ReceptorFactura(ParticipanteFactura):
    tipoDocumento: str
    numDocumento: str 

class PagosResumenFactura(BaseModel):
    codigo: str 
    montoPago: float = 0.00 
    pagosReferencia: float | None = None 
    plazo: float | None = None
    periodo: float | None = None    

class ResumenFactura(BaseModel):
    totalNoSuj: float = 0.00
    totalExenta: float = 0.00
    totalGravada: float = 0.00
    subTotalVentas: float = 0.00
    descuNoSuj: float = 0.00
    descuExenta: float = 0.00
    descuGravada: float = 0.00
    porcentajeDescuento: float = 0.00
    totalDescu: float = 0.00
    tributos: list = []
    subTotal: float = 0.00
    ivaRete: float = 0.00
    reteRenta: float = 0.00
    montoTotalOperacion: float = 0.00
    totalNoGravado: float = 0.00
    totalPagar: float = 0.00
    totalLetras: str 
    totalIva: float = 0.00 
    saldoFavor: float = 0.00 
    condicionOperacion: int 
    pagos: PagosResumenFactura
    numPagoElectronico: int | None = None 

class FacturaElectronica(BaseModel):
    identificacion: IdentificacionFactura
    documentoRelacionado: dict | None = None
    emisor: EmisorFactura  
    receptor: ReceptorFactura
    otrosDocumentos: dict | None = None
    ventaTerceros: dict | None = None
    cuerpoDocumento: list[ItemFactura]
    resumen: ResumenFactura
    extension: dict | None = None
    apendice: dict | None = None
