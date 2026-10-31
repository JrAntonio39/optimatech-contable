<template>
  <q-page padding>
    <div class="row items-center q-mb-md">
      <div>
        <div class="text-h5">Facturación</div>
        <div class="text-caption text-grey-7">FE consumidor final y CCF · clientes e integración contable</div>
      </div>
      <q-space />
      <q-btn flat color="secondary" icon="refresh" label="Actualizar" :loading="actualizandoLista" :disable="cargando || actualizandoLista || guardando || enviando !== null || eliminando !== null || dialog || dialogEliminar" @click="actualizarLista" />
      <q-btn v-if="auth.tienePermiso('facturas.crear')" color="primary" icon="add" label="Nueva factura" @click="abrirFactura" />
    </div>

    <q-banner v-if="error && !dialog" class="bg-red-1 text-red q-mb-md" rounded>{{ error }}</q-banner>
    <q-banner v-if="mensaje" class="bg-blue-1 text-blue-10 q-mb-md" rounded>{{ mensaje }}</q-banner>
    <q-card class="opti-card">
      <q-table :rows="facturas" :columns="columns" row-key="id" :loading="cargando || actualizandoLista" no-data-label="No hay facturas registradas">
        <template #body-cell-total="props"><q-td :props="props">{{ dinero(props.value) }}</q-td></template>
        <template #body-cell-estado="props"><q-td :props="props"><q-badge :color="colorEstado(props.value)">{{ props.value }}</q-badge></q-td></template>
        <template #body-cell-acciones="props">
          <q-td :props="props" class="q-gutter-xs">
            <q-btn dense flat color="primary" icon="picture_as_pdf" label="PDF" :loading="pdfCargando===props.row.id" @click="generarPdf(props.row)" />
            <q-btn v-if="props.row.estado==='BORRADOR' && auth.tienePermiso('facturas.aprobar')" dense flat color="primary" icon="send" label="Enviar a contabilidad" :loading="enviando===props.row.id" @click="enviar(props.row)" />
            <q-btn v-if="props.row.estado==='BORRADOR' && auth.tienePermiso('facturas.eliminar')" dense flat color="negative" icon="delete" label="Eliminar borrador" :loading="eliminando===props.row.id" :disable="eliminando!==null || enviando===props.row.id" @click="abrirEliminar(props.row)" />
          </q-td>
        </template>
      </q-table>
    </q-card>

    <q-dialog v-model="dialogEliminar">
      <q-card style="width: 480px; max-width: 94vw">
        <q-card-section class="text-h6">Eliminar factura en borrador</q-card-section>
        <q-banner v-if="errorEliminar" dense class="bg-red-1 text-red q-mx-md" rounded>{{ errorEliminar }}</q-banner>
        <q-card-section>
          ¿Eliminar la factura <strong>{{ facturaEliminar?.numero }}</strong>?
          Se borrarán sus líneas. La acción quedará registrada en auditoría y no se puede deshacer.
          Solo se permite porque todavía no se ha enviado a contabilidad.
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancelar" :disable="eliminando !== null" v-close-popup />
          <q-btn color="negative" label="Eliminar borrador" :loading="eliminando !== null" @click="eliminarBorrador" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="dialog" @hide="limpiarError">
      <q-card class="factura-dialog" style="width: 1000px; max-width: 96vw">
        <q-card-section class="row items-center"><div class="text-h6">Nueva factura</div><q-space/><q-btn v-close-popup flat round icon="close" /></q-card-section>
        <q-banner v-if="error" dense class="bg-red-1 text-red q-mx-md q-mb-sm" rounded>{{ error }}</q-banner>
        <q-card-section class="row q-col-gutter-sm">
          <div class="col-12 col-sm-3"><q-input v-model="form.numero" label="Número interno" placeholder="FAC-2026-0001" hint="Formato obligatorio: FAC-AAAA-0001 (prefijo, año y 4 dígitos)." maxlength="13" outlined dense /></div>
          <div class="col-12 col-sm-3"><q-select v-model="form.tipo_dte" :options="tiposFactura" option-value="value" option-label="label" emit-value map-options label="Tipo de documento" outlined dense /></div>
          <div class="col-12 col-sm-3"><q-input v-model="form.fecha" type="date" label="Fecha" outlined dense /></div>
          <div class="col-12 col-sm-3"><q-select v-model="form.cliente_id" :options="clientes" option-value="id" option-label="nombre" emit-value map-options label="Cliente" outlined dense /></div>
          <div class="col-12 col-sm-3"><q-select v-model="form.sucursal_id" :options="sucursales" option-value="id" option-label="nombre" emit-value map-options label="Sucursal emisora" outlined dense /></div>
          <div class="col-12 col-sm-3"><q-select v-model="form.periodo_id" :options="periodos" option-value="id" :option-label="p=>String(p.anio)" emit-value map-options label="Período contable" outlined dense /></div>
          <div class="col-12 col-sm-3"><q-select v-model="form.condicion_operacion" :options="condicionesPago" option-value="value" option-label="label" emit-value map-options label="¿Cuándo se paga?" hint="Contado = ahora; crédito = después" persistent-hint outlined dense /></div>
          <div class="col-12 col-sm-3"><q-select v-model="form.forma_pago" :options="formasPago" option-value="value" option-label="label" emit-value map-options label="¿Cómo se paga?" hint="Efectivo, tarjeta, transferencia o cheque" persistent-hint outlined dense /></div>
          <div v-if="form.condicion_operacion==='CREDITO'" class="col-12 col-sm-3"><q-input v-model.number="form.plazo_pago" type="number" min="1" max="365" label="Plazo de pago (días)" outlined dense /></div>
          <div v-if="form.condicion_operacion!=='CREDITO'" class="col-12 col-sm-6"><q-select v-model="form.cuenta_pago_codigo" :options="cuentasPago" option-value="codigo" :option-label="c=>`${c.codigo} · ${c.nombre}`" emit-value map-options label="Cuenta que recibe el pago" outlined dense /></div>
          <template v-if="form.tipo_dte==='CCF'">
            <div class="col-12 text-caption text-grey-6 q-pt-sm">La fecha de arriba es la emisión de la factura. Si hubo una nota de remisión previa, registra su número y la fecha propia de esa nota; si no hubo, deja ambos campos vacíos.</div>
            <div class="col-12 col-sm-6"><q-input v-model="form.nota_remision_numero" label="Número de nota de remisión (opcional)" placeholder="Ej.: NR-2026-0001" outlined dense /></div>
            <div class="col-12 col-sm-6"><q-input v-model="form.nota_remision_fecha" type="date" label="Fecha de emisión de la nota" :disable="!form.nota_remision_numero" outlined dense /></div>
          </template>
        </q-card-section>
        <q-card-section>
          <div class="row items-center q-mb-sm"><div class="text-subtitle1">Producto o servicio vendido</div><q-space/><q-btn flat color="primary" icon="add" label="Agregar línea" @click="form.detalles.push(lineaVacia(cuentaIngresoPredeterminada))" /></div>
          <q-banner v-if="!cuentas.length" dense rounded class="bg-orange-1 text-orange-10 q-mb-sm">
            No hay cuentas de ingreso disponibles. Revisa que el catálogo tenga cuentas hoja de ingresos (clase 5).
          </q-banner>
          <div v-for="(line,index) in form.detalles" :key="index" class="q-mb-md">
            <div class="row q-col-gutter-sm items-center">
              <div class="col-12 col-md-3"><q-select v-model="line.producto_codigo" :options="productosServicios" option-value="codigo" option-label="etiqueta" emit-value map-options label="Producto/servicio del catálogo" clearable @update:model-value="codigo => aplicarProducto(line,codigo)" outlined dense /></div>
              <div class="col-4 col-md-2"><q-input v-model.number="line.cantidad" type="number" min="0.01" step="0.01" label="Cantidad (2 decimales)" @blur="redondearLinea(line,'cantidad')" outlined dense /></div>
              <div class="col-8 col-md-2"><q-select v-model="line.unidad_medida" :options="unidadesMedida" option-value="value" option-label="label" emit-value map-options label="Unidad de medida" hint="Unidad = pieza; Servicio = trabajo" outlined dense /></div>
              <div class="col-6 col-md-2"><q-input v-model.number="line.precio_unitario" type="number" min="0.01" step="0.01" label="Precio unitario" @blur="redondearLinea(line,'precio_unitario')" outlined dense /></div>
              <div class="col-10 col-md-2"><q-select v-model="line.cuenta_codigo" :options="cuentas" option-value="codigo" option-label="etiqueta" emit-value map-options label="Cuenta de ingreso" hint="Cuenta contable de la venta" :rules="[val => !!val || 'Selecciona una cuenta de ingreso']" :disable="!cuentas.length || !!line.producto_codigo" outlined dense /></div>
              <div class="col-2 col-md-1"><q-btn flat round color="negative" icon="delete" :disable="form.detalles.length===1" @click="form.detalles.splice(index,1)" /></div>
              <div class="col-12 col-md-8"><q-input v-model="line.descripcion" label="Descripción detallada en la factura" placeholder="Ej. Desarrollo de sistema de inventario a la medida" outlined dense /></div>
              <div class="col-12 col-md-4"><q-select v-model="line.tipo_venta" :options="tiposVenta" option-value="value" option-label="label" emit-value map-options label="Clasificación de la venta" hint="Solo marca exenta/no sujeta si aplica" outlined dense /></div>
            </div>
          </div>
          <div class="factura-resumen text-right text-subtitle2">
            <div>Ventas gravadas {{ dinero(baseGravada) }}</div>
            <div>Ventas exentas {{ dinero(baseExenta) }} · No sujetas {{ dinero(baseNoSujeta) }}</div>
            <div>IVA 13% {{ dinero(iva) }}</div>
            <strong>Total {{ dinero(totalFactura) }}</strong>
          </div>
        </q-card-section>
        <q-card-actions align="right"><q-btn flat label="Cancelar" v-close-popup/><q-btn color="primary" label="Guardar borrador" :disable="!cuentas.length || form.detalles.some(linea => !linea.cuenta_codigo)" :loading="guardando" @click="guardarFactura" /></q-card-actions>
      </q-card>
    </q-dialog>

    <section v-if="facturaPdf" id="factura-imprimible" class="factura-print">
      <header class="factura-print__header">
        <div>
          <div class="factura-print__brand">OptimaTech</div>
          <div class="factura-print__sub">Sistema Contable · {{ facturaPdf.factura.sucursal }}</div>
        </div>
        <div class="factura-print__title">
          <strong>{{ tipoFacturaLabel(facturaPdf.factura.tipo_dte) }}</strong>
          <span>N.º interno {{ facturaPdf.factura.numero }}</span>
          <span>Fecha {{ fechaFmt(facturaPdf.factura.fecha) }} · {{ horaFmt(facturaPdf.factura.creado_en) }}</span>
        </div>
      </header>
      <section class="factura-print__parties">
        <div>
          <h2>EMISOR</h2>
          <strong>{{ facturaPdf.factura.emisor_nombre || 'OptimaTech' }}</strong>
          <div v-if="facturaPdf.factura.nombre_comercial">{{ facturaPdf.factura.nombre_comercial }}</div>
          <div v-if="facturaPdf.factura.giro">Giro: {{ facturaPdf.factura.giro }}</div>
          <div v-if="facturaPdf.factura.emisor_nit">NIT: {{ facturaPdf.factura.emisor_nit }}</div>
          <div v-if="facturaPdf.factura.emisor_nrc">NRC: {{ facturaPdf.factura.emisor_nrc }}</div>
          <div>{{ facturaPdf.factura.sucursal_direccion || 'Dirección no configurada' }}</div>
        </div>
        <div>
          <h2>CLIENTE</h2>
          <strong>{{ facturaPdf.factura.cliente }}</strong>
          <div v-if="facturaPdf.factura.cliente_nit">NIT: {{ facturaPdf.factura.cliente_nit }}</div>
          <div v-if="facturaPdf.factura.cliente_nrc">NRC: {{ facturaPdf.factura.cliente_nrc }}</div>
          <div v-if="facturaPdf.factura.cliente_giro">Giro: {{ facturaPdf.factura.cliente_giro }}</div>
          <div>{{ facturaPdf.factura.cliente_direccion || 'Dirección no registrada' }}</div>
          <div v-if="facturaPdf.factura.cliente_email">Correo: {{ facturaPdf.factura.cliente_email }}</div>
        </div>
      </section>
      <table class="factura-print__table">
        <thead><tr><th>Cant.</th><th>Unidad</th><th>Descripción</th><th>Clasificación</th><th>Precio unitario</th><th>Venta</th></tr></thead>
        <tbody>
          <tr v-for="(linea, index) in facturaPdf.detalles" :key="index">
            <td>{{ Number(linea.cantidad).toFixed(2) }}</td>
            <td>{{ linea.unidad_medida }}</td>
            <td>{{ linea.descripcion }}</td>
            <td>{{ tipoVentaLabel(linea.tipo_venta) }}</td>
            <td class="factura-print__number">{{ dinero(linea.precio_unitario) }}</td>
            <td class="factura-print__number">{{ dinero(linea.importe) }}</td>
          </tr>
        </tbody>
      </table>
      <div class="factura-print__totals">
        <div><span>Ventas gravadas</span><strong>{{ dinero(facturaPdf.gravada) }}</strong></div>
        <div><span>Ventas exentas</span><strong>{{ dinero(facturaPdf.exenta) }}</strong></div>
        <div><span>Ventas no sujetas</span><strong>{{ dinero(facturaPdf.no_sujeta) }}</strong></div>
        <div><span>IVA (13%)</span><strong>{{ dinero(facturaPdf.iva) }}</strong></div>
        <div class="factura-print__grand-total"><span>Total</span><strong>{{ dinero(facturaPdf.total) }}</strong></div>
      </div>
      <div class="factura-print__payment">
        <strong>Condición:</strong> {{ facturaPdf.factura.condicion_operacion }}
        <span v-if="facturaPdf.factura.forma_pago"> · <strong>Forma de pago:</strong> {{ facturaPdf.factura.forma_pago }}</span>
        <span v-if="facturaPdf.factura.plazo_pago"> · <strong>Plazo:</strong> {{ facturaPdf.factura.plazo_pago }} días</span>
      </div>
      <div v-if="facturaPdf.factura.nota_remision_numero" class="factura-print__payment">
        <strong>Nota de remisión:</strong> {{ facturaPdf.factura.nota_remision_numero }} · {{ fechaFmt(facturaPdf.factura.nota_remision_fecha) }}
      </div>
      <footer class="factura-print__footer">
        <span>Estado contable: {{ facturaPdf.factura.estado }}</span>
        <span class="factura-print__stamp"><span>OPTIMATECH</span><strong>REGISTRO INTERNO</strong><small>{{ facturaPdf.factura.numero }}</small></span>
      </footer>
    </section>
  </q-page>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { api } from '@/services/api.js'
import { operacionesService } from '@/services/operacionesService.js'

const auth=useAuthStore()
const facturas=ref([]), clientes=ref([]), productosServicios=ref([]), sucursales=ref([]), periodos=ref([]), cuentas=ref([]), cuentasCobrar=ref([]), cuentasPago=ref([])
const cargando=ref(false), actualizandoLista=ref(false), guardando=ref(false), enviando=ref(null), eliminando=ref(null), facturaEliminar=ref(null), dialogEliminar=ref(false), errorEliminar=ref(''), pdfCargando=ref(null), facturaPdf=ref(null), error=ref(''), mensaje=ref(''), dialog=ref(false)
const tiposFactura=[{label:'Factura electrónica · consumidor final (FE)',value:'FCON'},{label:'Comprobante de crédito fiscal (CCF)',value:'CCF'}]
const hoy=()=>{const d=new Date();return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`}
const lineaVacia=(cuentaCodigo='',productoCodigo=null)=>({descripcion:'',cantidad:1,unidad_medida:'UNIDAD',precio_unitario:0,tipo_venta:'GRAVADA',producto_codigo:productoCodigo,cuenta_codigo:cuentaCodigo})
const condicionesPago=[{label:'Contado',value:'CONTADO'},{label:'Crédito',value:'CREDITO'}]
const formasPago=[{label:'Efectivo',value:'EFECTIVO'},{label:'Tarjeta',value:'TARJETA'},{label:'Transferencia',value:'TRANSFERENCIA'},{label:'Cheque',value:'CHEQUE'}]
const tiposVenta=[{label:'Gravada con IVA',value:'GRAVADA'},{label:'Exenta',value:'EXENTA'},{label:'No sujeta',value:'NO_SUJETA'}]
const unidadesMedida=[{label:'Unidad',value:'UNIDAD'},{label:'Servicio',value:'SERVICIO'},{label:'Hora',value:'HORA'},{label:'Mes',value:'MES'},{label:'Licencia',value:'LICENCIA'},{label:'Equipo',value:'EQUIPO'},{label:'Kit',value:'KIT'}]
const nuevoForm=()=>({numero:'',tipo_dte:'CCF',fecha:hoy(),cliente_id:null,sucursal_id:null,periodo_id:null,condicion_operacion:'CONTADO',forma_pago:'EFECTIVO',plazo_pago:null,cuenta_pago_codigo:'1.1.1.01',nota_remision_numero:'',nota_remision_fecha:null,detalles:[lineaVacia()]})
const form=ref(nuevoForm())
let refreshFacturasTimer = null
watch(form,()=>{if(dialog.value&&error.value)error.value=''}, {deep:true})
function limpiarError(){error.value=''}
const cuentaIngresoPredeterminada=computed(()=>cuentas.value.find(c=>c.codigo==='5.1.1.01')?.codigo||cuentas.value[0]?.codigo||'')
const clienteSeleccionado=computed(()=>clientes.value.find(c=>c.id===form.value.cliente_id)||null)
const clienteCcfCompleto=computed(()=>!!clienteSeleccionado.value?.nit&&!!clienteSeleccionado.value?.nrc&&!!clienteSeleccionado.value?.giro&&!!clienteSeleccionado.value?.direccion)
const importeLinea=linea=>Math.round(((Number(linea.cantidad)||0)*(Number(linea.precio_unitario)||0)+Number.EPSILON)*100)/100
const baseGravada=computed(()=>form.value.detalles.filter(l=>l.tipo_venta==='GRAVADA').reduce((s,l)=>s+importeLinea(l),0))
const baseExenta=computed(()=>form.value.detalles.filter(l=>l.tipo_venta==='EXENTA').reduce((s,l)=>s+importeLinea(l),0))
const baseNoSujeta=computed(()=>form.value.detalles.filter(l=>l.tipo_venta==='NO_SUJETA').reduce((s,l)=>s+importeLinea(l),0))
const subtotal=computed(()=>baseGravada.value+baseExenta.value+baseNoSujeta.value)
const iva=computed(()=>Math.round((baseGravada.value*0.13+Number.EPSILON)*100)/100)
const totalFactura=computed(()=>subtotal.value+iva.value)
const columns=[{name:'numero',label:'Número',field:'numero',align:'left',sortable:true},{name:'fecha',label:'Fecha',field:'fecha',sortable:true},{name:'cliente',label:'Cliente',field:'cliente',align:'left'},{name:'tipo_dte',label:'Documento',field:'tipo_dte',format:v=>v==='CCF'?'CCF · Crédito fiscal':'FE · Consumidor final'},{name:'total',label:'Total',field:'total',align:'right'},{name:'estado',label:'Estado',field:'estado'},{name:'acciones',label:'Acciones',field:'id',align:'right'}]
const dinero=v=>new Intl.NumberFormat('es-SV',{style:'currency',currency:'USD'}).format(Number(v)||0)
const fechaFmt=v=>{if(!v)return '';const [y,m,d]=String(v).slice(0,10).split('-');return `${d}/${m}/${y}`}
const horaFmt=v=>v?new Intl.DateTimeFormat('es-SV',{hour:'2-digit',minute:'2-digit'}).format(new Date(v)):''
const tipoFacturaLabel=v=>v==='CCF'?'COMPROBANTE DE CRÉDITO FISCAL':'FACTURA DE CONSUMIDOR FINAL'
const tipoVentaLabel=v=>({GRAVADA:'Gravada',EXENTA:'Exenta',NO_SUJETA:'No sujeta'}[v]||'Gravada')
const colorEstado=v=>v==='VIGENTE'?'positive':v==='PENDIENTE'?'orange':'grey'
async function cargar(){
  cargando.value=true;error.value=''
  try{
    const [f,c,ps,s,p,a,r,ef]=await Promise.all([
      operacionesService.facturas(),operacionesService.clientes(),operacionesService.productosServicios(),
      api.get('/api/sucursales'),api.get('/api/periodos'),api.get('/api/cuentas?q=5.'),
      api.get('/api/cuentas?q=1.1.3.'),api.get('/api/cuentas?q=1.1.1.')
    ])
    facturas.value=f.facturas
    clientes.value=c.clientes.filter(x=>x.estado==='ACTIVO')
    productosServicios.value=ps.productos.map(x=>({...x,etiqueta:`${x.linea_negocio} · ${x.nombre}`}))
    sucursales.value=s.sucursales
    periodos.value=p.periodos.filter(x=>x.estado==='ABIERTO')
    const padres=new Set(a.cuentas.map(x=>x.codigo_padre))
    cuentas.value=a.cuentas.filter(x=>x.codigo?.startsWith('5.')&&!padres.has(x.codigo)).map(x=>({...x,etiqueta:`${x.codigo} · ${x.nombre}`}))
    const padresCxC=new Set(r.cuentas.map(x=>x.codigo_padre))
    cuentasCobrar.value=r.cuentas.filter(x=>x.codigo.startsWith('1.1.3.')&&!padresCxC.has(x.codigo))
    const padresPago=new Set(ef.cuentas.map(x=>x.codigo_padre))
    cuentasPago.value=ef.cuentas.filter(x=>x.codigo.startsWith('1.1.1.')&&!padresPago.has(x.codigo))
    for(const linea of form.value.detalles){if(!linea.cuenta_codigo)linea.cuenta_codigo=cuentaIngresoPredeterminada.value}
  }catch(e){error.value=e.message}finally{cargando.value=false}
}
function abrirFactura(){
  limpiarError()
  form.value=nuevoForm()
  form.value.detalles=[lineaVacia(cuentaIngresoPredeterminada.value)]
  form.value.periodo_id=periodos.value[0]?.id||null
  form.value.sucursal_id=auth.usuario?.sucursal_id||sucursales.value[0]?.id||null
  form.value.cuenta_pago_codigo=cuentasPago.value[0]?.codigo||'1.1.1.01'
  dialog.value=true
}
function aplicarProducto(linea,codigo){
  const producto=productosServicios.value.find(x=>x.codigo===codigo)
  if(!producto){linea.producto_codigo=null;return}
  linea.descripcion=producto.nombre
  linea.unidad_medida=producto.unidad_medida
  linea.cuenta_codigo=producto.cuenta_ingreso_codigo
}
function redondearLinea(linea,campo){
  const valor=Number(linea[campo])
  if(Number.isFinite(valor))linea[campo]=Number(valor.toFixed(2))
}
async function guardarFactura(){
  error.value=''
  for(const linea of form.value.detalles){redondearLinea(linea,'cantidad');redondearLinea(linea,'precio_unitario')}
  form.value.numero=String(form.value.numero||'').trim().toUpperCase()
  if(!/^FAC-\d{4}-\d{4}$/.test(form.value.numero)){error.value='El número interno debe tener el formato FAC-AAAA-0001. Ejemplo: FAC-2026-0001.';return}
  if(!form.value.cliente_id||!form.value.sucursal_id||!form.value.periodo_id){error.value='Selecciona cliente, sucursal y período contable.';return}
  if(form.value.tipo_dte==='CCF'&&!clienteCcfCompleto.value){error.value='Para un CCF, el cliente debe tener nombre, NIT, NRC, giro o actividad y dirección. Completa sus datos en la sección “Clientes”.';return}
  const numeroRemision=String(form.value.nota_remision_numero||'').trim()
  const fechaRemision=String(form.value.nota_remision_fecha||'').trim()
  if(numeroRemision&&!fechaRemision){error.value='Ingresaste el número de una nota de remisión. Completa también su fecha o borra el número si no corresponde.';return}
  const lineaInvalida=form.value.detalles.findIndex(linea=>!linea.descripcion?.trim()||linea.descripcion.trim().length<2||!(Number(linea.cantidad)>0)||!(Number(linea.precio_unitario)>0)||!linea.cuenta_codigo)
  if(lineaInvalida!==-1){
    const linea=form.value.detalles[lineaInvalida]
    error.value=!linea.cuenta_codigo?`Selecciona un producto del catálogo o una cuenta de ingreso para la línea ${lineaInvalida+1}.`:!linea.descripcion?.trim()||linea.descripcion.trim().length<2?`Escribe qué producto o servicio vendiste en la línea ${lineaInvalida+1}.`:!(Number(linea.cantidad)>0)?`Indica una cantidad mayor que cero en la línea ${lineaInvalida+1}.`:`Indica un precio mayor que cero en la línea ${lineaInvalida+1}.`
    return
  }
  if(!form.value.forma_pago){error.value='Selecciona la forma de pago.';return}
  guardando.value=true
  try{
    await operacionesService.crearFactura(form.value)
    dialog.value=false;mensaje.value='Factura guardada como borrador.'
    await cargar()
  }catch(e){error.value=e.message}finally{guardando.value=false}
}
async function generarPdf(row){pdfCargando.value=row.id;error.value='';try{facturaPdf.value=await operacionesService.factura(row.id);await nextTick();window.print()}catch(e){error.value=`No se pudo preparar el PDF. (${e.message})`}finally{pdfCargando.value=null}}
async function enviar(row){enviando.value=row.id;error.value='';try{const r=await operacionesService.enviarFactura(row.id);mensaje.value=`Asiento ${r.asiento_codigo} pendiente de aprobación. Apruébalo en Control.`;await cargar()}catch(e){error.value=e.message}finally{enviando.value=null}}
function abrirEliminar(row){errorEliminar.value='';facturaEliminar.value=row;dialogEliminar.value=true}
async function eliminarBorrador(){
  const row=facturaEliminar.value
  if(!row)return
  eliminando.value=row.id;errorEliminar.value=''
  try{
    await operacionesService.eliminarFactura(row.id)
    dialogEliminar.value=false
    facturaEliminar.value=null
    mensaje.value=`La factura ${row.numero} en borrador fue eliminada.`
    await cargar()
  }catch(e){errorEliminar.value=e.message}
  finally{eliminando.value=null}
}
async function refrescarFacturas(){
  if(document.visibilityState!=='visible'||cargando.value||actualizandoLista.value||guardando.value||enviando.value!==null||eliminando.value!==null||dialog.value||dialogEliminar.value)return
  try{const result=await operacionesService.facturas();facturas.value=result.facturas}catch(e){error.value=e.message}
}
async function actualizarLista(){
  if(dialog.value||dialogEliminar.value||guardando.value||enviando.value!==null||eliminando.value!==null||actualizandoLista.value)return
  actualizandoLista.value=true;error.value=''
  try{const result=await operacionesService.facturas();facturas.value=result.facturas}catch(e){error.value=e.message}finally{actualizandoLista.value=false}
}
function refrescarAlVolver(){if(document.visibilityState==='visible')refrescarFacturas()}
onMounted(()=>{
  cargar()
  refreshFacturasTimer=window.setInterval(refrescarFacturas,5000)
  window.addEventListener('focus',refrescarAlVolver)
  document.addEventListener('visibilitychange',refrescarAlVolver)
})
onUnmounted(()=>{if(refreshFacturasTimer)window.clearInterval(refreshFacturasTimer);window.removeEventListener('focus',refrescarAlVolver);document.removeEventListener('visibilitychange',refrescarAlVolver)})
</script>

<style>
.factura-print { display: none; }
.factura-dialog { max-height: 92vh; overflow-y: auto; }
.factura-dialog .q-field__native, .factura-dialog .q-field__input { min-width: 0; }
.factura-dialog .q-select__selection { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

@media print {
  @page { size: A4; margin: 0; }
  body * { visibility: hidden !important; }
  #factura-imprimible, #factura-imprimible * { visibility: visible !important; }
  #factura-imprimible {
    display: block !important;
    position: fixed;
    inset: 12mm;
    width: auto;
    min-height: 273mm;
    box-sizing: border-box;
    color: #17233a;
    font: 11px Arial, sans-serif;
  }
  .factura-print__header { display: flex; justify-content: space-between; gap: 20px; border-bottom: 3px solid #009688; padding: 0 0 14px; }
  .factura-print__brand { color: #006e83; font-size: 24px; font-weight: 700; }
  .factura-print__sub { color: #52627a; margin-top: 4px; }
  .factura-print__title { display: grid; gap: 5px; text-align: right; }
  .factura-print__title strong { color: #006e83; font-size: 15px; }
  .factura-print__parties { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin: 24px 0; }
  .factura-print__parties > div { border: 1px solid #cbd5e1; border-radius: 6px; padding: 10px; line-height: 1.55; }
  .factura-print__parties h2 { color: #007f8b; font-size: 10px; margin: 0 0 7px; }
  .factura-print__table { border-collapse: collapse; width: 100%; }
  .factura-print__table th { background: #e8f5f6 !important; color: #006e83; print-color-adjust: exact; -webkit-print-color-adjust: exact; }
  .factura-print__table th, .factura-print__table td { border-bottom: 1px solid #d7dee8; padding: 8px 6px; text-align: left; }
  .factura-print__table th:first-child { width: 12%; }
  .factura-print__table th:nth-child(3), .factura-print__table th:nth-child(4) { text-align: right; }
  .factura-print__number { text-align: right !important; white-space: nowrap; }
  .factura-print__totals { margin: 18px 0 0 auto; width: 250px; }
  .factura-print__totals > div { display: flex; justify-content: space-between; padding: 5px 0; }
  .factura-print__grand-total { border-top: 2px solid #007f8b; color: #006e83; font-size: 15px; }
  .factura-print__payment { margin-top: 18px; color: #34445d; }
  .factura-print__footer { border-top: 1px solid #cbd5e1; color: #52627a; display: flex; align-items: flex-start; justify-content: space-between; gap: 14px; margin-top: 28px; padding-top: 8px; font-size: 9px; }
  .factura-print__stamp { display: inline-grid; gap: 2px; border: 2px solid #007f8b; color: #006e83; padding: 7px 12px; text-align: center; transform: rotate(-3deg); }
  .factura-print__stamp strong { font-size: 10px; letter-spacing: .08em; }
  .factura-print__stamp small { color: #52627a; }
}

@media (max-width: 700px) {
  .factura-dialog { max-height: 96vh; }
}
</style>
