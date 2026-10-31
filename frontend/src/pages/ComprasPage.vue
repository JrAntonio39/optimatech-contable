<template>
  <q-page padding>
    <div class="row items-center q-mb-md"><div><div class="text-h5">Compras</div><div class="text-caption text-grey-7">Registro de compras e IVA crédito fiscal</div></div><q-space/><q-btn v-if="auth.tienePermiso('compras.crear')" color="primary" icon="add" label="Nueva compra" @click="abrirCompra"/></div>
    <q-banner v-if="error" class="bg-red-1 text-red q-mb-md" rounded>{{ error }}</q-banner><q-banner v-if="mensaje" class="bg-blue-1 text-blue-10 q-mb-md" rounded>{{ mensaje }}</q-banner>
    <q-card class="opti-card"><q-table :rows="compras" :columns="columns" row-key="id" :loading="cargando" no-data-label="No hay compras registradas">
      <template #body-cell-total="p"><q-td :props="p">{{ dinero(p.value) }}</q-td></template><template #body-cell-estado="p"><q-td :props="p"><q-badge :color="colorEstado(p.value)">{{ p.value }}</q-badge></q-td></template>
      <template #body-cell-acciones="p"><q-td :props="p"><q-btn v-if="p.row.estado==='BORRADOR'&&auth.tienePermiso('compras.aprobar')" dense flat color="primary" icon="send" label="Enviar" :loading="enviando===p.row.id" @click="enviar(p.row)"/></q-td></template>
    </q-table></q-card>
    <q-dialog v-model="dialog"><q-card style="width:900px;max-width:95vw"><q-card-section class="row items-center"><div class="text-h6">Nueva compra</div><q-space/><q-btn v-close-popup flat round icon="close"/></q-card-section>
      <q-card-section class="row q-col-gutter-sm"><div class="col-12 col-sm-3"><q-input v-model="form.numero" label="Número de documento (opcional)" placeholder="Ej.: CCF-001-00001234" hint="Vacío: se asigna COMP-[año]-0001 automáticamente." maxlength="30" outlined dense/></div><div class="col-12 col-sm-2"><q-select v-model="form.tipo_doc" :options="['CCF','FCON','TICKET']" label="Tipo" outlined dense/></div><div class="col-12 col-sm-3"><q-input v-model="form.fecha" type="date" label="Fecha" outlined dense/></div><div class="col-12 col-sm-4"><q-select v-model="form.proveedor_id" :options="proveedores" option-value="id" option-label="nombre" emit-value map-options label="Proveedor" outlined dense/></div><div class="col-12 col-sm-6"><q-select v-model="form.sucursal_id" :options="sucursales" option-value="id" option-label="nombre" emit-value map-options label="Sucursal" outlined dense/></div><div class="col-12 col-sm-6"><q-select v-model="form.periodo_id" :options="periodos" option-value="id" :option-label="p=>String(p.anio)" emit-value map-options label="Período contable" outlined dense/></div></q-card-section>
      <q-card-section>
        <div class="row items-center q-mb-sm"><div class="text-subtitle1">Detalle</div><q-space/><q-btn flat color="primary" icon="add" label="Agregar línea" @click="form.detalles.push(lineaVacia())"/></div>
        <div v-for="(line,i) in form.detalles" :key="i" class="q-mb-md">
          <div class="row q-col-gutter-sm items-center">
            <div class="col-12 col-md-4"><q-input v-model="line.descripcion" label="Descripción" outlined dense/></div>
            <div class="col-4 col-md-2"><q-input v-model.number="line.cantidad" type="number" min="0.01" step="0.01" label="Cantidad" outlined dense/></div>
            <div class="col-4 col-md-2"><q-input v-model.number="line.precio_unitario" type="number" min="0.01" step="0.01" label="Precio unitario" outlined dense/></div>
            <div class="col-10 col-md-3"><q-select v-model="line.cuenta_codigo" :options="cuentas" option-value="codigo" :option-label="cuentaLabel" emit-value map-options label="Cuenta de activo/gasto" outlined dense/></div>
            <div class="col-2 col-md-1"><q-btn flat round color="negative" icon="delete" :disable="form.detalles.length===1" @click="form.detalles.splice(i,1)"/></div>
            <div class="col-12 col-md-4"><q-select v-model="line.tipo_iva" :options="tiposIva" option-value="value" option-label="label" emit-value map-options label="Clasificación del IVA" hint="Solo las compras gravadas calculan IVA crédito fiscal." outlined dense/></div>
          </div>
        </div>
        <div class="text-right text-subtitle2">
          <div>Compras gravadas {{ dinero(baseGravada) }}</div>
          <div>Compras exentas {{ dinero(baseExenta) }} · No sujetas {{ dinero(baseNoSujeta) }}</div>
          <div>IVA crédito fiscal 13% {{ dinero(iva) }}</div>
          <strong>Total {{ dinero(totalCompra) }}</strong>
        </div>
        <div class="text-caption text-grey-7">Selecciona la clasificación que aparece en el comprobante del proveedor. El IVA se calcula únicamente sobre líneas gravadas.</div>
      </q-card-section>
      <q-card-actions align="right"><q-btn flat label="Cancelar" v-close-popup/><q-btn color="primary" label="Guardar borrador" :loading="guardando" @click="guardar"/></q-card-actions></q-card></q-dialog>
  </q-page>
</template>
<script setup>
import {computed,onMounted,onUnmounted,ref} from 'vue'
import {useQuasar} from 'quasar'
import {useAuthStore} from '@/stores/auth.js'
import {api} from '@/services/api.js'
import {operacionesService} from '@/services/operacionesService.js'
const $q=useQuasar(),auth=useAuthStore();const compras=ref([]),proveedores=ref([]),sucursales=ref([]),periodos=ref([]),cuentas=ref([]),error=ref(''),mensaje=ref(''),cargando=ref(false),guardando=ref(false),enviando=ref(null),dialog=ref(false)
const hoy=()=>new Date().toISOString().slice(0,10),lineaVacia=()=>({descripcion:'',cantidad:1,precio_unitario:0,cuenta_codigo:null,tipo_iva:'GRAVADA'}),nuevo=()=>({numero:'',tipo_doc:'CCF',fecha:hoy(),proveedor_id:null,sucursal_id:null,periodo_id:null,detalles:[lineaVacia()]})
const form=ref(nuevo()),importeLinea=linea=>Math.round(((Number(linea.cantidad)||0)*(Number(linea.precio_unitario)||0)+Number.EPSILON)*100)/100
let refreshComprasTimer=null
const baseGravada=computed(()=>form.value.detalles.filter(line=>line.tipo_iva==='GRAVADA').reduce((sum,line)=>sum+importeLinea(line),0))
const baseExenta=computed(()=>form.value.detalles.filter(line=>line.tipo_iva==='EXENTA').reduce((sum,line)=>sum+importeLinea(line),0))
const baseNoSujeta=computed(()=>form.value.detalles.filter(line=>line.tipo_iva==='NO_SUJETA').reduce((sum,line)=>sum+importeLinea(line),0))
const subtotal=computed(()=>baseGravada.value+baseExenta.value+baseNoSujeta.value),iva=computed(()=>Math.round((baseGravada.value*.13+Number.EPSILON)*100)/100),totalCompra=computed(()=>subtotal.value+iva.value)
const tiposIva=[{label:'Gravada con IVA',value:'GRAVADA'},{label:'Exenta',value:'EXENTA'},{label:'No sujeta',value:'NO_SUJETA'}]
const columns=[{name:'numero',label:'Documento',field:'numero',align:'left',sortable:true},{name:'fecha',label:'Fecha',field:'fecha',sortable:true},{name:'proveedor',label:'Proveedor',field:'proveedor',align:'left'},{name:'tipo_doc',label:'Tipo',field:'tipo_doc'},{name:'total',label:'Total',field:'total',align:'right'},{name:'estado',label:'Estado',field:'estado'},{name:'acciones',label:'Acciones',field:'id',align:'right'}],dinero=v=>new Intl.NumberFormat('es-SV',{style:'currency',currency:'USD'}).format(Number(v)||0)
const colorEstado=estado=>({VIGENTE:'positive',PENDIENTE:'warning',BORRADOR:'grey-7',RECHAZADO:'negative',ANULADA:'grey-7'})[estado]||'grey-7'
async function cargar(){cargando.value=true;error.value='';try{const [c,p,s,per,a]=await Promise.all([operacionesService.compras(),operacionesService.proveedores(),api.get('/api/sucursales'),api.get('/api/periodos'),api.get('/api/cuentas')]);compras.value=c.compras;proveedores.value=p.proveedores.filter(x=>x.estado==='ACTIVO');sucursales.value=s.sucursales;periodos.value=per.periodos.filter(x=>x.estado==='ABIERTO');const cuentasApi=(a.cuentas||[]).map(x=>({...x,codigo:x.codigo??x.cuenta_codigo,nombre:x.nombre??x.cuenta_nombre??x.descripcion}));const padres=new Set(cuentasApi.map(x=>x.codigo_padre));cuentas.value=cuentasApi.filter(x=>x.codigo&&((x.codigo.startsWith('1.')||x.codigo.startsWith('4.')))&&!padres.has(x.codigo))}catch(e){error.value=e.message}finally{cargando.value=false}}
function cuentaLabel(cuenta){if(!cuenta)return '';return [cuenta.codigo,cuenta.nombre].filter(Boolean).join(' · ')}
function abrirCompra(){form.value=nuevo();form.value.periodo_id=periodos.value[0]?.id||null;form.value.sucursal_id=auth.usuario?.sucursal_id||sucursales.value[0]?.id||null;dialog.value=true}
async function guardar(){guardando.value=true;error.value='';try{const result=await operacionesService.crearCompra(form.value);dialog.value=false;mensaje.value=`Compra ${result.numero} guardada como borrador.`;$q.notify({type:'positive',message:'Compra registrada'});await cargar()}catch(e){error.value=e.message}finally{guardando.value=false}}
async function enviar(row){enviando.value=row.id;error.value='';try{const r=await operacionesService.enviarCompra(row.id);mensaje.value=`Asiento ${r.asiento_codigo} pendiente de aprobación. Apruébalo en Control.`;await cargar()}catch(e){error.value=e.message}finally{enviando.value=null}}
async function refrescarCompras(){if(document.visibilityState!=='visible'||cargando.value||guardando.value||enviando.value!==null||dialog.value)return;try{const result=await operacionesService.compras();compras.value=result.compras}catch(e){error.value=e.message}}
onMounted(()=>{cargar();refreshComprasTimer=window.setInterval(refrescarCompras,15000)})
onUnmounted(()=>{if(refreshComprasTimer)window.clearInterval(refreshComprasTimer)})
</script>
