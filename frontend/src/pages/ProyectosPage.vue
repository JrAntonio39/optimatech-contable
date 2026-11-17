<template>
  <q-page padding>
    <div class="row items-center q-mb-md">
      <div>
        <div class="text-h5">Proyectos y rentabilidad</div>
        <div class="text-caption text-grey-7">Relaciona ventas, compras y planilla con cada trabajo de OptimaTech.</div>
      </div>
      <q-space />
      <q-btn v-if="auth.tienePermiso('proyectos.rentabilidad')" flat color="primary" icon="assessment" label="Reporte consolidado" :loading="cargandoReporte" @click="abrirReporte" />
      <q-btn flat color="secondary" icon="refresh" label="Actualizar" :loading="cargando" @click="cargarProyectos" />
      <q-btn v-if="auth.tienePermiso('proyectos.crear')" class="q-ml-sm" color="primary" icon="add" label="Nuevo proyecto" @click="abrirNuevo" />
    </div>

    <q-banner v-if="error" class="bg-red-1 text-red q-mb-md" rounded>{{ error }}</q-banner>
    <q-banner v-if="mensaje" class="bg-blue-1 text-blue-10 q-mb-md" rounded>{{ mensaje }}</q-banner>
    <q-banner class="bg-blue-1 text-blue-10 q-mb-md" rounded>
      Las asignaciones son analíticas: solo enlazan líneas contabilizadas y vigentes; no crean ni modifican asientos. Los costos de compras se consideran por su importe de línea antes del IVA.
    </q-banner>

    <q-card class="opti-card">
      <q-table :rows="proyectos" :columns="columnas" row-key="id" :loading="cargando" :filter="filtro" :pagination="{ rowsPerPage: 10 }" no-data-label="No hay proyectos registrados">
        <template #top-right>
          <q-input v-model="filtro" dense outlined debounce="250" placeholder="Buscar proyecto" clearable>
            <template #prepend><q-icon name="search" /></template>
          </q-input>
        </template>
        <template #body-cell-proyecto="p">
          <q-td :props="p">
            <div class="text-weight-medium">{{ p.row.nombre }}</div>
            <div class="text-caption text-grey-7">{{ p.row.codigo }} · {{ tipoLabel(p.row.tipo) }}</div>
          </q-td>
        </template>
        <template #body-cell-cliente="p"><q-td :props="p">{{ p.value || '—' }}</q-td></template>
        <template #body-cell-estado="p">
          <q-td :props="p"><q-badge :color="colorEstado(p.value)">{{ estadoLabel(p.value) }}</q-badge></q-td>
        </template>
        <template #body-cell-acciones="p">
          <q-td :props="p" class="text-right">
            <q-btn flat dense color="secondary" icon="analytics" label="Ver proyecto" @click="abrirDetalle(p.row)" />
            <q-btn v-if="auth.tienePermiso('proyectos.editar')" flat dense color="primary" icon="edit" label="Editar" @click="abrirEdicion(p.row)" />
          </q-td>
        </template>
      </q-table>
    </q-card>

    <q-dialog v-model="dialogProyecto" @hide="errorDialog = ''">
      <q-card style="width: 760px; max-width: 96vw">
        <q-card-section class="row items-center">
          <div class="text-h6">{{ editando ? 'Editar proyecto' : 'Nuevo proyecto' }}</div>
          <q-space /><q-btn v-close-popup flat round icon="close" />
        </q-card-section>
        <q-card-section v-if="errorDialog" class="q-pt-none"><q-banner class="bg-red-1 text-red" rounded>{{ errorDialog }}</q-banner></q-card-section>
        <q-card-section class="row q-col-gutter-sm">
          <div class="col-12 col-sm-4">
            <q-input v-model="form.codigo" label="Código (opcional)" placeholder="Ej.: PRY-0001" hint="Déjalo vacío para asignarlo automáticamente." maxlength="20" outlined dense />
          </div>
          <div class="col-12 col-sm-8"><q-input v-model="form.nombre" label="Nombre del proyecto *" placeholder="Ej.: Instalación CCTV – Cliente X" maxlength="160" outlined dense /></div>
          <div class="col-12 col-sm-6">
            <q-select v-model="form.tipo" :options="tiposProyecto" option-value="value" option-label="label" emit-value map-options label="Tipo de trabajo" outlined dense />
          </div>
          <div v-if="puedeVerClientes" class="col-12 col-sm-6">
            <q-select v-model="form.cliente_id" :options="clientes" option-value="id" option-label="nombre" emit-value map-options clearable label="Cliente (opcional)" outlined dense />
          </div>
          <div class="col-12"><q-input v-model="form.descripcion" type="textarea" autogrow label="Descripción (opcional)" placeholder="Alcance, entregables o notas del trabajo" maxlength="2000" outlined dense /></div>
          <div class="col-12 col-sm-4"><q-input v-model="form.fecha_inicio" type="date" label="Fecha de inicio" outlined dense /></div>
          <div class="col-12 col-sm-4"><q-input v-model="form.fecha_fin" type="date" label="Fecha de cierre" outlined dense /></div>
          <div v-if="editando" class="col-12 col-sm-4">
            <q-select v-model="form.estado" :options="estadosPermitidos" option-value="value" option-label="label" emit-value map-options label="Estado" outlined dense />
          </div>
          <div class="col-12"><q-separator class="q-my-sm" /><div class="text-subtitle2">Presupuesto estimado (opcional)</div><div class="text-caption text-grey-7">Ingresa el total esperado del proyecto por categoría. Si una categoría no aplica, escribe 0. Lo compararás con los movimientos reales aprobados y asignados.</div></div>
          <div class="col-12 col-sm-6 col-md-3"><q-input v-model.number="form.ingreso_estimado" type="number" min="0" step="0.01" label="Ingreso esperado ($)" placeholder="Ej.: 1,500.00" outlined dense clearable /></div>
          <div class="col-12 col-sm-6 col-md-3"><q-input v-model.number="form.costo_directo_estimado" type="number" min="0" step="0.01" label="Costos directos ($)" placeholder="Ej.: 300.00" outlined dense clearable /></div>
          <div class="col-12 col-sm-6 col-md-3"><q-input v-model.number="form.mano_obra_estimada" type="number" min="0" step="0.01" label="Mano de obra ($)" placeholder="Ej.: 450.00" outlined dense clearable /></div>
          <div class="col-12 col-sm-6 col-md-3"><q-input v-model.number="form.costo_indirecto_estimado" type="number" min="0" step="0.01" label="Costos indirectos ($)" placeholder="Ej.: 100.00" outlined dense clearable /></div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancelar" v-close-popup />
          <q-btn color="primary" :label="editando ? 'Guardar cambios' : 'Crear proyecto'" :loading="guardandoProyecto" @click="guardarProyecto" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="dialogDetalle">
      <q-card class="bg-page text-primary" style="width: 1100px; max-width: 92vw; max-height: 92vh; overflow-y: auto">
        <q-toolbar class="opti-header text-white">
          <q-toolbar-title class="text-weight-bold">OptimaTech <span class="text-caption q-ml-sm">Sistema Contable · Proyectos</span></q-toolbar-title>
          <q-btn flat icon="arrow_back" label="Volver a proyectos" v-close-popup />
        </q-toolbar>
        <q-card-section class="row items-center q-px-lg">
          <div>
            <div class="text-h5">{{ proyectoActual?.nombre }}</div>
            <div class="text-caption text-grey-7">{{ proyectoActual?.codigo }} · {{ tipoLabel(proyectoActual?.tipo) }}</div>
          </div>
          <q-space />
          <q-badge :color="colorEstado(proyectoActual?.estado)" class="q-mr-md">{{ estadoLabel(proyectoActual?.estado) }}</q-badge>
          <q-btn v-close-popup flat round icon="close" />
        </q-card-section>
        <q-separator />
        <q-card-section class="q-pa-lg">
          <q-banner v-if="errorDetalle" class="bg-red-1 text-red q-mb-md" rounded>{{ errorDetalle }}</q-banner>
          <q-inner-loading :showing="cargandoDetalle"><q-spinner size="42px" color="primary" /></q-inner-loading>
          <template v-if="!cargandoDetalle && proyectoActual">
            <div v-if="rentabilidad" class="row q-col-gutter-md q-mb-lg">
              <div class="col-12 col-sm-6 col-lg-3"><q-card class="opti-card q-pa-md"><div class="text-caption text-grey-7">Ingresos asignados</div><div class="text-h5 text-positive">{{ dinero(rentabilidad.ingresos) }}</div></q-card></div>
              <div class="col-12 col-sm-6 col-lg-3"><q-card class="opti-card q-pa-md"><div class="text-caption text-grey-7">Costos directos y mano de obra</div><div class="text-h5">{{ dinero(Number(rentabilidad.costos_directos) + Number(rentabilidad.mano_obra)) }}</div></q-card></div>
              <div class="col-12 col-sm-6 col-lg-3"><q-card class="opti-card q-pa-md"><div class="text-caption text-grey-7">Costos indirectos</div><div class="text-h5">{{ dinero(rentabilidad.costos_indirectos) }}</div></q-card></div>
              <div class="col-12 col-sm-6 col-lg-3"><q-card class="opti-card q-pa-md"><div class="text-caption text-grey-7">Margen del proyecto</div><div class="text-h5" :class="Number(rentabilidad.margen) >= 0 ? 'text-positive' : 'text-negative'">{{ dinero(rentabilidad.margen) }}</div><div class="text-caption">{{ Number(rentabilidad.margen_porcentaje).toFixed(2) }}% de los ingresos</div></q-card></div>
            </div>
            <q-card v-if="rentabilidad" class="opti-card q-mb-lg">
              <q-card-section class="row items-center q-pb-sm">
                <div><div class="text-h6">Presupuesto y resultado real</div><div class="text-caption text-grey-7">La variación es real asignado menos estimado; en costos, un valor positivo indica exceso sobre el presupuesto.</div></div>
                <q-space />
                <div v-if="rentabilidad.presupuesto_completo" class="text-right"><div class="text-caption text-grey-7">Margen estimado</div><div class="text-subtitle1">{{ dinero(rentabilidad.margen_estimado) }} · {{ Number(rentabilidad.margen_estimado_porcentaje).toFixed(2) }}%</div></div>
                <q-btn v-if="auth.tienePermiso('proyectos.editar')" flat dense color="primary" icon="edit" label="Editar presupuesto" class="q-ml-md" @click="abrirEdicion(proyectoActual)" />
              </q-card-section>
              <q-table :rows="rentabilidad.comparativo" :columns="columnasComparativo" row-key="categoria" :pagination="{ rowsPerPage: 0 }" hide-bottom>
                <template #body-cell-estimado="p"><q-td :props="p" class="text-right">{{ p.value == null ? 'Sin estimar' : dinero(p.value) }}</q-td></template>
                <template #body-cell-real="p"><q-td :props="p" class="text-right">{{ dinero(p.value) }}</q-td></template>
                <template #body-cell-variacion="p"><q-td :props="p" class="text-right" :class="p.value == null ? 'text-grey-7' : p.row.categoria === 'INGRESO' ? (Number(p.value) >= 0 ? 'text-positive' : 'text-negative') : (Number(p.value) <= 0 ? 'text-positive' : 'text-negative')">{{ p.value == null ? '—' : `${Number(p.value) > 0 ? '+' : ''}${dinero(p.value)}` }}</q-td></template>
              </q-table>
              <q-card-section v-if="!rentabilidad.presupuesto_completo" class="text-caption text-grey-7 q-pt-sm">Completa las cuatro estimaciones en “Editar presupuesto” para habilitar el margen presupuestado.</q-card-section>
            </q-card>
            <q-banner v-if="!rentabilidad" class="bg-blue-1 text-blue-10 q-mb-md" rounded>
              Tu rol puede asignar solo las categorías que tiene autorizadas. El reporte consolidado de margen requiere el permiso de rentabilidad.
            </q-banner>
            <q-banner v-if="asignacionesNoVigentes.length" class="bg-amber-1 text-amber-10 q-mb-md" rounded>
              Hay {{ asignacionesNoVigentes.length }} asignación(es) cuyo documento fuente ya no está vigente. Se conservan como historial, pero se excluyen de los saldos y del margen.
            </q-banner>
            <div class="row items-center q-mb-sm">
              <div class="text-h6">Movimientos asignados</div><q-space />
              <q-btn v-if="puedeAsignarAlguna && proyectoActual.estado === 'ABIERTO'" color="primary" icon="add" label="Asignar ingreso o costo" @click="abrirAsignacion" />
            </div>
            <q-table :rows="asignacionesVisibles" :columns="columnasAsignaciones" row-key="id" :pagination="{ rowsPerPage: 10 }" no-data-label="Aún no hay ingresos o costos asignados">
              <template #body-cell-documento="p">
                <q-td :props="p">
                  <div>{{ p.row.documento || 'Documento no disponible' }}</div>
                  <q-badge v-if="p.row.fuente_vigente === false" color="warning" text-color="dark" class="q-mt-xs">Fuente no vigente</q-badge>
                  <q-badge v-if="p.row.sustituido_por_horas" color="info" class="q-mt-xs">Costo calculado con horas</q-badge>
                </q-td>
              </template>
              <template #body-cell-categoria="p"><q-td :props="p">{{ categoriaLabel(p.value) }}</q-td></template>
              <template #body-cell-dias="p"><q-td :props="p" class="text-right">{{ p.value == null ? '—' : `${p.value} días` }}</q-td></template>
              <template #body-cell-monto="p"><q-td :props="p" class="text-right">{{ dinero(p.value) }}</q-td></template>
              <template #body-cell-acciones="p">
                <q-td :props="p" class="text-right">
                  <q-btn v-if="puedeQuitar(p.row) && proyectoActual.estado === 'ABIERTO'" flat dense color="negative" icon="delete_outline" label="Quitar" @click="confirmarQuitar(p.row)" />
                </q-td>
              </template>
            </q-table>
            <div class="row items-center q-mt-lg q-mb-sm">
              <div class="text-h6">Registro de horas</div><q-space />
              <q-btn v-if="auth.tienePermiso('proyectos.asignar_planilla') && proyectoActual.estado === 'ABIERTO'" color="primary" icon="schedule" label="Registrar horas" :disable="!empleados.length" @click="abrirRegistroHoras" />
            </div>
            <q-banner v-if="errorHoras" class="bg-red-1 text-red q-mb-sm" rounded>{{ errorHoras }}</q-banner>
            <q-table :rows="horasProyecto" :columns="columnasHoras" row-key="id" :loading="cargandoHoras" :pagination="{ rowsPerPage: 10 }" no-data-label="Aún no hay horas registradas">
              <template #body-cell-fecha="p"><q-td :props="p">{{ fechaLabel(p.value) }}</q-td></template>
              <template #body-cell-horas="p"><q-td :props="p" class="text-right">{{ Number(p.value).toFixed(2) }}</q-td></template>
              <template #body-cell-costo="p"><q-td :props="p" class="text-right">{{ p.value == null ? 'Pendiente de planilla vigente' : dinero(p.value) }}</q-td></template>
              <template #body-cell-acciones-horas="p"><q-td :props="p" class="text-right"><q-btn v-if="auth.tienePermiso('proyectos.asignar_planilla') && proyectoActual.estado === 'ABIERTO'" flat dense color="negative" icon="delete_outline" label="Quitar" @click="confirmarQuitarHoras(p.row)" /></q-td></template>
            </q-table>
          </template>
        </q-card-section>
      </q-card>
    </q-dialog>

    <q-dialog v-model="dialogAsignacion">
      <q-card style="width: 820px; max-width: 96vw">
        <q-card-section class="row items-center"><div class="text-h6">Asignar ingreso o costo</div><q-space /><q-btn v-close-popup flat round icon="close" /></q-card-section>
        <q-card-section v-if="errorAsignacion" class="q-pt-none"><q-banner class="bg-red-1 text-red" rounded>{{ errorAsignacion }}</q-banner></q-card-section>
        <q-card-section class="row q-col-gutter-sm">
          <div class="col-12 col-sm-5">
            <q-select v-model="asignacion.fuente_tipo" :options="tiposFuentePermitidos" option-value="value" option-label="label" emit-value map-options label="Origen del movimiento" outlined dense @update:model-value="cargarFuentes" />
          </div>
          <div v-if="asignacion.fuente_tipo === 'COMPRA'" class="col-12 col-sm-7">
            <q-select v-model="asignacion.categoria" :options="categoriasCompra" option-value="value" option-label="label" emit-value map-options label="Clasificación del costo" outlined dense />
          </div>
          <div v-if="asignacion.fuente_tipo === 'PLANILLA'" class="col-12 col-sm-7">
            <q-select v-model="asignacion.categoria" :options="categoriasPlanilla" option-value="value" option-label="label" emit-value map-options label="Concepto de planilla" outlined dense @update:model-value="actualizarCategoriaPlanilla" />
          </div>
          <div class="col-12">
            <q-select v-model="asignacion.fuente_detalle_id" :options="fuentes" :option-value="'fuente_detalle_id'" :option-label="fuenteLabel" emit-value map-options label="Línea contabilizada *" :loading="cargandoFuentes" :disable="cargandoFuentes || !asignacion.fuente_tipo" outlined dense @update:model-value="actualizarMontoSugerido">
              <template #option="scope"><q-item v-bind="scope.itemProps"><q-item-section><q-item-label>{{ fuenteLabel(scope.opt) }}</q-item-label><q-item-label caption>{{ scope.opt.descripcion }} · {{ scope.opt.monto_disponible > 0 ? `Mano de obra: ${dinero(scope.opt.monto_disponible)}` : '' }}{{ scope.opt.monto_extra_disponible > 0 ? ` · Horas extra: ${dinero(scope.opt.monto_extra_disponible)}` : '' }}</q-item-label></q-item-section></q-item></template>
              <template #no-option><q-item><q-item-section class="text-grey-7">{{ asignacion.fuente_tipo === 'FACTURA' && !proyectoActual?.cliente_id ? 'Vincula un cliente al proyecto para ver facturas' : 'No hay líneas disponibles' }}</q-item-section></q-item></template>
            </q-select>
          </div>
          <div v-if="asignacion.fuente_tipo === 'PLANILLA' && asignacion.categoria === 'MANO_OBRA'" class="col-12 col-sm-5"><q-input v-model.number="asignacion.dias_asignados" type="number" min="0.01" :max="fuenteSeleccionada?.dias_disponibles" step="0.01" label="Días de esta planilla para el proyecto *" outlined dense @update:model-value="actualizarMontoPlanilla" /></div>
          <div v-else class="col-12 col-sm-5"><q-input v-model.number="asignacion.monto" type="number" min="0.01" :max="montoFuenteDisponible" step="0.01" :label="asignacion.fuente_tipo === 'PLANILLA' ? 'Monto de horas extra para el proyecto *' : 'Importe que se asigna *'" outlined dense /></div>
          <div v-if="asignacion.fuente_tipo === 'PLANILLA' && asignacion.categoria === 'MANO_OBRA'" class="col-12 col-sm-7 self-center text-caption text-grey-7">Días disponibles: <strong>{{ fuenteSeleccionada?.dias_disponibles || 0 }} de {{ fuenteSeleccionada?.dias_trabajados || 0 }}</strong> · Costo asignado: <strong>{{ dinero(asignacion.monto || 0) }}</strong></div>
          <div v-else class="col-12 col-sm-7 self-center text-caption text-grey-7">{{ asignacion.fuente_tipo === 'PLANILLA' ? 'Importe de horas extra disponible:' : 'Disponible en la fuente:' }} <strong>{{ dinero(montoFuenteDisponible) }}</strong></div>
        </q-card-section>
        <q-card-actions align="right"><q-btn flat label="Cancelar" v-close-popup /><q-btn color="primary" label="Guardar asignación" :loading="guardandoAsignacion" :disable="!asignacion.fuente_detalle_id || !asignacion.monto" @click="guardarAsignacion" /></q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="dialogHoras">
      <q-card style="width: 620px; max-width: 96vw">
        <q-card-section class="row items-center"><div class="text-h6">Registrar horas de trabajo</div><q-space /><q-btn flat round icon="close" v-close-popup /></q-card-section>
        <q-card-section v-if="errorHorasFormulario" class="q-pt-none"><q-banner class="bg-red-1 text-red" rounded>{{ errorHorasFormulario }}</q-banner></q-card-section>
        <q-card-section class="row q-col-gutter-sm">
          <div class="col-12"><q-select v-model="formHoras.empleado_id" :options="empleados" option-value="id" :option-label="e => `${e.codigo} · ${e.nombres} ${e.apellidos}`" emit-value map-options label="Empleado *" outlined dense /></div>
          <div class="col-12 col-sm-6"><q-input v-model="formHoras.fecha_inicio" type="date" label="Desde *" outlined dense /></div>
          <div class="col-12 col-sm-6"><q-input v-model="formHoras.fecha_fin" type="date" label="Hasta *" outlined dense /></div>
          <div class="col-12"><q-option-group v-model="formHoras.dias_semana" :options="diasSemanaOpciones" type="checkbox" inline color="primary" /></div>
          <div class="col-12 col-sm-6"><q-input v-model.number="formHoras.horas_por_dia" type="number" min="0.25" max="8" step="0.25" label="Horas por día *" outlined dense /></div>
          <div class="col-12"><q-input v-model="formHoras.actividad" type="textarea" autogrow maxlength="240" label="Actividad realizada *" outlined dense /></div>
        </q-card-section>
        <q-card-actions align="right"><q-btn flat label="Cancelar" v-close-popup /><q-btn color="primary" label="Guardar horas" :loading="guardandoHoras" :disable="!formHoras.empleado_id || !formHoras.fecha_inicio || !formHoras.fecha_fin || !formHoras.horas_por_dia || !formHoras.dias_semana.length || !formHoras.actividad" @click="guardarHoras" /></q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="dialogReporte">
      <q-card style="width: 1200px; max-width: 96vw; max-height: 90vh">
        <q-card-section class="row items-center"><div class="text-h6">Rentabilidad consolidada por proyecto</div><q-space /><q-btn flat color="primary" icon="download" label="Exportar CSV" :disable="!reporteRows.length" @click="exportarReporte" /><q-btn flat round icon="close" v-close-popup /></q-card-section>
        <q-card-section v-if="errorReporte" class="q-pt-none"><q-banner class="bg-red-1 text-red" rounded>{{ errorReporte }}</q-banner></q-card-section>
        <q-table :rows="reporteRows" :columns="columnasReporte" row-key="id" :loading="cargandoReporte" :pagination="{ rowsPerPage: 10 }" no-data-label="No hay proyectos para mostrar">
          <template #body-cell-ingresos="p"><q-td :props="p" class="text-right">{{ dinero(p.value) }}</q-td></template>
          <template #body-cell-costos_directos="p"><q-td :props="p" class="text-right">{{ dinero(p.value) }}</q-td></template>
          <template #body-cell-mano_obra="p"><q-td :props="p" class="text-right">{{ dinero(p.value) }}</q-td></template>
          <template #body-cell-costos_indirectos="p"><q-td :props="p" class="text-right">{{ dinero(p.value) }}</q-td></template>
          <template #body-cell-costos_totales="p"><q-td :props="p" class="text-right">{{ dinero(p.value) }}</q-td></template>
          <template #body-cell-margen="p"><q-td :props="p" class="text-right" :class="Number(p.value) >= 0 ? 'text-positive' : 'text-negative'">{{ dinero(p.value) }}</q-td></template>
        </q-table>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useQuasar } from 'quasar'
import { useAuthStore } from '@/stores/auth.js'
import { api } from '@/services/api.js'
import { proyectosService } from '@/services/operacionesService.js'

const $q = useQuasar()
const auth = useAuthStore()
const proyectos = ref([])
const clientes = ref([])
const filtro = ref('')
const cargando = ref(false)
const guardandoProyecto = ref(false)
const dialogProyecto = ref(false)
const dialogDetalle = ref(false)
const dialogAsignacion = ref(false)
const dialogHoras = ref(false)
const dialogReporte = ref(false)
const editando = ref(false)
const proyectoId = ref(null)
const proyectoActual = ref(null)
const rentabilidad = ref(null)
const asignaciones = ref([])
const horasProyecto = ref([])
const empleados = ref([])
const reporteRows = ref([])
const fuentes = ref([])
const cargandoDetalle = ref(false)
const cargandoFuentes = ref(false)
const guardandoAsignacion = ref(false)
const guardandoHoras = ref(false)
const cargandoHoras = ref(false)
const cargandoReporte = ref(false)
const error = ref('')
const errorDialog = ref('')
const errorDetalle = ref('')
const errorAsignacion = ref('')
const errorHoras = ref('')
const errorHorasFormulario = ref('')
const errorReporte = ref('')
const mensaje = ref('')
const formVacio = () => ({ codigo: '', nombre: '', descripcion: '', tipo: 'OTRO', cliente_id: null, fecha_inicio: '', fecha_fin: '', estado: 'ABIERTO', ingreso_estimado: null, costo_directo_estimado: null, mano_obra_estimada: null, costo_indirecto_estimado: null })
const form = ref(formVacio())
const asignacionVacia = () => ({ fuente_tipo: '', fuente_detalle_id: null, categoria: '', monto: null, dias_asignados: null })
const asignacion = ref(asignacionVacia())
const hoy = () => new Date().toLocaleDateString('sv-SE')
function diasSemanaIniciales(fecha) {
  const jsDay = new Date(`${fecha}T00:00:00Z`).getUTCDay()
  const isoDay = jsDay === 0 ? 7 : jsDay
  return [...new Set([1, 2, 3, 4, 5, ...(isoDay > 5 ? [isoDay] : [])])]
}
const formHoras = ref({ empleado_id: null, fecha_inicio: hoy(), fecha_fin: hoy(), dias_semana: diasSemanaIniciales(hoy()), actividad: '', horas_por_dia: null })
const diasSemanaOpciones = [
  { label: 'Lun', value: 1 }, { label: 'Mar', value: 2 }, { label: 'Mié', value: 3 },
  { label: 'Jue', value: 4 }, { label: 'Vie', value: 5 }, { label: 'Sáb', value: 6 }, { label: 'Dom', value: 7 }
]
const puedeVerClientes = computed(() => auth.tienePermiso('facturas.ver'))
const puedeAsignarAlguna = computed(() => ['FACTURA', 'COMPRA', 'PLANILLA'].some(type => permisoFuente(type)))
const tiposProyecto = [
  { label: 'Instalación CCTV', value: 'CCTV' }, { label: 'Desarrollo de software', value: 'DESARROLLO' },
  { label: 'Hosting', value: 'HOSTING' }, { label: 'Soporte técnico', value: 'SOPORTE' },
  { label: 'Licencias', value: 'LICENCIAS' }, { label: 'Equipo tecnológico', value: 'EQUIPO' }, { label: 'Otro', value: 'OTRO' }
]
const categoriasCompra = [{ label: 'Costo directo del proyecto', value: 'COSTO_DIRECTO' }, { label: 'Costo indirecto asignado', value: 'COSTO_INDIRECTO' }]
const categoriasPlanilla = [{ label: 'Mano de obra ordinaria', value: 'MANO_OBRA' }, { label: 'Importe pagado por horas extra', value: 'HORAS_EXTRA' }]
const estados = [{ label: 'Abierto', value: 'ABIERTO' }, { label: 'Completado', value: 'COMPLETADO' }, { label: 'Cancelado', value: 'CANCELADO' }]
const estadosPermitidos = computed(() => form.value.estado === 'ABIERTO' ? estados : estados.filter(option => option.value !== 'ABIERTO'))
const columnas = [
  { name: 'proyecto', label: 'Proyecto', field: 'nombre', align: 'left', sortable: true },
  { name: 'cliente', label: 'Cliente', field: row => row.cliente || '', align: 'left' },
  { name: 'fechas', label: 'Período', field: row => `${fechaLabel(row.fecha_inicio)} – ${fechaLabel(row.fecha_fin)}`, align: 'left' },
  { name: 'estado', label: 'Estado', field: 'estado', align: 'center' },
  { name: 'acciones', label: 'Acciones', field: 'id', align: 'right' }
]
const columnasAsignaciones = [
  { name: 'documento', label: 'Documento', field: 'documento', align: 'left' },
  { name: 'fuente_tipo', label: 'Origen', field: 'fuente_tipo' },
  { name: 'categoria', label: 'Clasificación', field: 'categoria' },
  { name: 'descripcion', label: 'Detalle', field: row => row.descripcion || '—', align: 'left' },
  { name: 'dias', label: 'Días asignados', field: 'dias_asignados', align: 'right' },
  { name: 'monto', label: 'Importe asignado', field: 'monto', align: 'right' },
  { name: 'acciones', label: 'Acciones', field: 'id', align: 'right' }
]
const columnasComparativo = [
  { name: 'concepto', label: 'Categoría', field: 'concepto', align: 'left' },
  { name: 'estimado', label: 'Estimado', field: 'estimado', align: 'right' },
  { name: 'real', label: 'Real asignado', field: 'real_asignado', align: 'right' },
  { name: 'variacion', label: 'Variación (real − estimado)', field: 'variacion', align: 'right' }
]
const columnasHorasBase = [
  { name: 'fecha', label: 'Fecha', field: 'fecha', align: 'left', sortable: true },
  { name: 'empleado', label: 'Empleado', field: 'empleado', align: 'left' },
  { name: 'actividad', label: 'Actividad', field: 'actividad', align: 'left' },
  { name: 'horas', label: 'Horas', field: 'horas', align: 'right' },
  { name: 'costo', label: 'Costo desde planilla', field: 'costo_calculado', align: 'right' },
  { name: 'acciones-horas', label: 'Acciones', field: 'id', align: 'right' }
]
const columnasHoras = computed(() => auth.tienePermiso('proyectos.rentabilidad')
  ? columnasHorasBase
  : columnasHorasBase.filter(column => column.name !== 'costo'))
const columnasReporte = [
  { name: 'codigo', label: 'Código', field: 'codigo', align: 'left' },
  { name: 'nombre', label: 'Proyecto', field: 'nombre', align: 'left' },
  { name: 'ingresos', label: 'Ingresos', field: 'ingresos', align: 'right' },
  { name: 'costos_directos', label: 'Costos directos', field: 'costos_directos', align: 'right' },
  { name: 'mano_obra', label: 'Mano de obra', field: 'mano_obra', align: 'right' },
  { name: 'costos_indirectos', label: 'Costos indirectos', field: 'costos_indirectos', align: 'right' },
  { name: 'costos_totales', label: 'Costos totales', field: 'costos_totales', align: 'right' },
  { name: 'margen', label: 'Margen', field: 'margen', align: 'right' },
  { name: 'margen_porcentaje', label: 'Margen %', field: row => `${Number(row.margen_porcentaje).toFixed(2)}%`, align: 'right' }
]
const tiposFuentePermitidos = computed(() => [
  ...(permisoFuente('FACTURA') ? [{ label: 'Factura contabilizada · Ingreso', value: 'FACTURA' }] : []),
  ...(permisoFuente('COMPRA') ? [{ label: 'Compra contabilizada · Costo', value: 'COMPRA' }] : []),
  ...(permisoFuente('PLANILLA') ? [{ label: 'Planilla contabilizada · Mano de obra', value: 'PLANILLA' }] : [])
])
const fuenteSeleccionada = computed(() => fuentes.value.find(row => row.fuente_detalle_id === asignacion.value.fuente_detalle_id) || null)
const montoFuenteDisponible = computed(() => asignacion.value.fuente_tipo === 'PLANILLA' && asignacion.value.categoria === 'HORAS_EXTRA'
  ? Number(fuenteSeleccionada.value?.monto_extra_disponible || 0)
  : Number(fuenteSeleccionada.value?.monto_disponible || 0))
const asignacionesVisibles = computed(() => rentabilidad.value?.asignaciones || asignaciones.value)
const asignacionesNoVigentes = computed(() => asignacionesVisibles.value.filter(row => row.fuente_vigente === false))

function permisoFuente(type) {
  const permission = { FACTURA: 'proyectos.asignar_ingresos', COMPRA: 'proyectos.asignar_compras', PLANILLA: 'proyectos.asignar_planilla' }[type]
  return auth.tienePermiso(permission)
}
function dinero(value) { return new Intl.NumberFormat('es-SV', { style: 'currency', currency: 'USD' }).format(Number(value) || 0) }
function fechaLabel(value) { return value ? new Intl.DateTimeFormat('es-SV', { dateStyle: 'medium', timeZone: 'UTC' }).format(new Date(`${String(value).slice(0, 10)}T00:00:00Z`)) : 'Sin fecha' }
function tipoLabel(value) { return tiposProyecto.find(item => item.value === value)?.label || 'Otro' }
function estadoLabel(value) { return ({ ABIERTO: 'Abierto', COMPLETADO: 'Completado', CANCELADO: 'Cancelado' })[value] || value || '—' }
function colorEstado(value) { return ({ ABIERTO: 'positive', COMPLETADO: 'blue-grey', CANCELADO: 'negative' })[value] || 'grey' }
function categoriaLabel(value) { return ({ INGRESO: 'Ingreso', COSTO_DIRECTO: 'Costo directo', MANO_OBRA: 'Mano de obra ordinaria', HORAS_EXTRA: 'Horas extra', COSTO_INDIRECTO: 'Costo indirecto' })[value] || value }
function fuenteLabel(row) { return `${row.documento} · ${row.tercero} · ${row.descripcion} · ${fechaLabel(row.fecha)}` }

async function cargarProyectos() {
  cargando.value = true
  error.value = ''
  try {
    const result = await proyectosService.listar()
    proyectos.value = result.proyectos || []
    if (puedeVerClientes.value) {
      try { const customers = await api.get('/api/clientes'); clientes.value = (customers.clientes || []).filter(customer => customer.estado === 'ACTIVO') }
      catch { clientes.value = [] }
    }
  } catch (err) { error.value = err.message }
  finally { cargando.value = false }
}
async function abrirReporte() {
  dialogReporte.value = true
  await cargarReporte()
}
async function cargarReporte() {
  cargandoReporte.value = true
  errorReporte.value = ''
  try {
    const result = await proyectosService.reporteRentabilidad()
    reporteRows.value = result.proyectos || []
  } catch (err) { errorReporte.value = err.message }
  finally { cargandoReporte.value = false }
}
function exportarReporte() {
  const headers = ['Código', 'Proyecto', 'Estado', 'Ingresos', 'Costos directos', 'Mano de obra', 'Costos indirectos', 'Costos totales', 'Margen', 'Margen %']
  const csvCell = value => `"${String(value ?? '').replaceAll('"', '""')}"`
  const rows = reporteRows.value.map(row => [row.codigo, row.nombre, estadoLabel(row.estado), row.ingresos, row.costos_directos, row.mano_obra, row.costos_indirectos, row.costos_totales, row.margen, row.margen_porcentaje])
  const csv = [headers, ...rows].map(row => row.map(csvCell).join(',')).join('\r\n')
  const url = URL.createObjectURL(new Blob([`\uFEFF${csv}`], { type: 'text/csv;charset=utf-8' }))
  const link = document.createElement('a')
  link.href = url
  link.download = `rentabilidad-proyectos-${hoy()}.csv`
  link.click()
  URL.revokeObjectURL(url)
}
async function cargarEmpleados() {
  if (!auth.tienePermiso('proyectos.asignar_planilla')) return
  try {
    const result = await proyectosService.empleadosActivos()
    empleados.value = result.empleados || []
  } catch (err) { error.value = err.message }
}

function abrirNuevo() {
  errorDialog.value = ''
  editando.value = false
  proyectoId.value = null
  form.value = formVacio()
  dialogProyecto.value = true
}
function abrirEdicion(row) {
  errorDialog.value = ''
  editando.value = true
  proyectoId.value = row.id
  form.value = { ...formVacio(), codigo: row.codigo || '', nombre: row.nombre, descripcion: row.descripcion || '', tipo: row.tipo || 'OTRO', cliente_id: row.cliente_id || null, fecha_inicio: row.fecha_inicio || '', fecha_fin: row.fecha_fin || '', estado: row.estado, ingreso_estimado: row.ingreso_estimado == null ? null : Number(row.ingreso_estimado), costo_directo_estimado: row.costo_directo_estimado == null ? null : Number(row.costo_directo_estimado), mano_obra_estimada: row.mano_obra_estimada == null ? null : Number(row.mano_obra_estimada), costo_indirecto_estimado: row.costo_indirecto_estimado == null ? null : Number(row.costo_indirecto_estimado) }
  dialogProyecto.value = true
}
async function guardarProyecto() {
  errorDialog.value = ''
  const nombre = String(form.value.nombre || '').trim()
  if (nombre.length < 3) { errorDialog.value = 'Escribe un nombre de proyecto de al menos 3 caracteres.'; return }
  if (form.value.fecha_inicio && form.value.fecha_fin && form.value.fecha_fin < form.value.fecha_inicio) { errorDialog.value = 'La fecha de cierre no puede ser anterior al inicio.'; return }
  const estimates = ['ingreso_estimado', 'costo_directo_estimado', 'mano_obra_estimada', 'costo_indirecto_estimado']
  for (const key of estimates) {
    const value = form.value[key]
    const amount = Number(value)
    if (value !== null && value !== '' && (!Number.isFinite(amount) || amount < 0 || Math.abs(amount * 100 - Math.round(amount * 100)) > 1e-8)) {
      errorDialog.value = 'Las estimaciones deben ser valores de cero o mayores y admitir máximo 2 decimales.'
      return
    }
  }
  const wasEditing = editando.value
  const savedProjectId = proyectoId.value
  const payload = {
    ...form.value,
    ...Object.fromEntries(estimates.map(key => [key, form.value[key] === '' || form.value[key] == null ? null : Number(form.value[key])])),
    nombre,
    codigo: form.value.codigo.trim() || null,
    descripcion: form.value.descripcion.trim() || null,
    cliente_id: form.value.cliente_id || null,
    fecha_inicio: form.value.fecha_inicio || null,
    fecha_fin: form.value.fecha_fin || null
  }
  guardandoProyecto.value = true
  try {
    const result = wasEditing ? await proyectosService.actualizar(savedProjectId, payload) : await proyectosService.crear(payload)
    dialogProyecto.value = false
    mensaje.value = wasEditing ? 'Proyecto actualizado.' : `Proyecto ${result.codigo} creado.`
    await cargarProyectos()
    if (wasEditing && dialogDetalle.value) {
      const refreshedProject = proyectos.value.find(project => project.id === savedProjectId)
      if (refreshedProject) await abrirDetalle(refreshedProject)
    }
  } catch (err) { errorDialog.value = err.message }
  finally { guardandoProyecto.value = false }
}

async function abrirDetalle(row) {
  proyectoActual.value = row
  rentabilidad.value = null
  asignaciones.value = []
  horasProyecto.value = []
  errorDetalle.value = ''
  errorHoras.value = ''
  dialogDetalle.value = true
  cargandoDetalle.value = true
  cargandoHoras.value = true
  try {
    const horasPromise = proyectosService.horas(row.id)
    if (auth.tienePermiso('proyectos.rentabilidad')) {
      const [rentabilidadResult, horasResult] = await Promise.all([proyectosService.rentabilidad(row.id), horasPromise])
      rentabilidad.value = rentabilidadResult
      horasProyecto.value = horasResult.horas || []
    } else {
      const types = ['FACTURA', 'COMPRA', 'PLANILLA'].filter(permisoFuente)
      const [parts, horasResult] = await Promise.all([Promise.all(types.map(type => proyectosService.asignaciones(row.id, type))), horasPromise])
      asignaciones.value = parts.flatMap(result => result.asignaciones || [])
      horasProyecto.value = horasResult.horas || []
    }
  } catch (err) { errorDetalle.value = err.message }
  finally { cargandoDetalle.value = false; cargandoHoras.value = false }
}

function abrirRegistroHoras() {
  errorHorasFormulario.value = ''
  const today = hoy()
  formHoras.value = { empleado_id: null, fecha_inicio: today, fecha_fin: today, dias_semana: diasSemanaIniciales(today), actividad: '', horas_por_dia: null }
  dialogHoras.value = true
}
async function guardarHoras() {
  errorHorasFormulario.value = ''
  const hours = Number(formHoras.value.horas_por_dia)
  if (!Number.isFinite(hours) || hours <= 0 || hours > 8 || Math.round(hours * 100) !== hours * 100) {
    errorHorasFormulario.value = 'Ingresa horas mayores a cero y hasta 8 por fecha, con máximo dos decimales.'
    return
  }
  if (!formHoras.value.fecha_inicio || !formHoras.value.fecha_fin || formHoras.value.fecha_fin < formHoras.value.fecha_inicio) {
    errorHorasFormulario.value = 'Revisa el rango de fechas.'
    return
  }
  if ((new Date(`${formHoras.value.fecha_fin}T00:00:00Z`) - new Date(`${formHoras.value.fecha_inicio}T00:00:00Z`)) / 86400000 > 62) {
    errorHorasFormulario.value = 'El rango máximo por operación es de 63 días.'
    return
  }
  if (!formHoras.value.dias_semana.length) { errorHorasFormulario.value = 'Selecciona al menos un día de la semana.'; return }
  const activity = String(formHoras.value.actividad || '').trim()
  if (activity.length < 3) { errorHorasFormulario.value = 'Describe la actividad con al menos 3 caracteres.'; return }
  guardandoHoras.value = true
  try {
    const result = await proyectosService.registrarHorasLote(proyectoActual.value.id, { ...formHoras.value, horas_por_dia: hours, actividad: activity })
    dialogHoras.value = false
    mensaje.value = `Se registraron ${result.registros} fecha(s), ${Number(result.horas_totales).toFixed(2)} horas en total.`
    await abrirDetalle(proyectoActual.value)
  } catch (err) { errorHorasFormulario.value = err.message }
  finally { guardandoHoras.value = false }
}
function confirmarQuitarHoras(row) {
  $q.dialog({ title: 'Quitar horas', message: `¿Quitar el registro de ${row.horas} horas de ${row.empleado}?`, cancel: true, persistent: true })
    .onOk(async () => {
      errorHoras.value = ''
      try {
        await proyectosService.quitarHoras(proyectoActual.value.id, row.id)
        await abrirDetalle(proyectoActual.value)
      } catch (err) { errorHoras.value = err.message }
    })
}

function abrirAsignacion() {
  errorAsignacion.value = ''
  asignacion.value = { ...asignacionVacia(), dias_asignados: null }
  asignacion.value.fuente_tipo = tiposFuentePermitidos.value[0]?.value || ''
  asignacion.value.categoria = asignacion.value.fuente_tipo === 'FACTURA' ? 'INGRESO' : asignacion.value.fuente_tipo === 'PLANILLA' ? 'MANO_OBRA' : 'COSTO_DIRECTO'
  fuentes.value = []
  dialogAsignacion.value = true
  if (asignacion.value.fuente_tipo) cargarFuentes()
}
async function cargarFuentes() {
  const type = asignacion.value.fuente_tipo
  asignacion.value.fuente_detalle_id = null
  asignacion.value.monto = null
  fuentes.value = []
  if (!type || !proyectoActual.value) return
  asignacion.value.categoria = type === 'FACTURA' ? 'INGRESO' : type === 'PLANILLA' ? 'MANO_OBRA' : 'COSTO_DIRECTO'
  cargandoFuentes.value = true
  errorAsignacion.value = ''
  try {
    if (type === 'FACTURA' && !proyectoActual.value.cliente_id) return
    const result = await proyectosService.fuentes(proyectoActual.value.id, type)
    fuentes.value = result.fuentes || []
  } catch (err) { errorAsignacion.value = err.message }
  finally { cargandoFuentes.value = false }
}
function actualizarMontoSugerido() {
  if (asignacion.value.fuente_tipo === 'PLANILLA' && asignacion.value.categoria === 'MANO_OBRA'
      && fuenteSeleccionada.value && Number(fuenteSeleccionada.value.monto_disponible) <= 0
      && Number(fuenteSeleccionada.value.monto_extra_disponible) > 0) {
    asignacion.value.categoria = 'HORAS_EXTRA'
  }
  asignacion.value.dias_asignados = null
  asignacion.value.monto = asignacion.value.fuente_tipo === 'PLANILLA' && asignacion.value.categoria === 'MANO_OBRA'
    ? null
    : (fuenteSeleccionada.value ? montoFuenteDisponible.value : null)
}
function actualizarCategoriaPlanilla() {
  asignacion.value.dias_asignados = null
  asignacion.value.monto = asignacion.value.categoria === 'HORAS_EXTRA' && fuenteSeleccionada.value
    ? montoFuenteDisponible.value
    : null
}
function actualizarMontoPlanilla() {
  const source = fuenteSeleccionada.value
  const days = Number(asignacion.value.dias_asignados)
  if (!source || !Number.isFinite(days) || days <= 0 || days > Number(source.dias_disponibles)) {
    asignacion.value.monto = null
    return
  }
  const isFinalDays = Math.round(days * 100) === Math.round(Number(source.dias_disponibles) * 100)
  const amount = isFinalDays ? Number(source.monto_disponible) : Number(source.monto_total) * days / Number(source.dias_trabajados)
  asignacion.value.monto = Math.round((amount + Number.EPSILON) * 100) / 100
}
async function guardarAsignacion() {
  errorAsignacion.value = ''
  const amount = Number(asignacion.value.monto)
  const available = montoFuenteDisponible.value
  if (asignacion.value.fuente_tipo === 'PLANILLA' && asignacion.value.categoria === 'MANO_OBRA') {
    const days = Number(asignacion.value.dias_asignados)
    if (!Number.isFinite(days) || days <= 0 || Math.round(days * 100) !== days * 100) { errorAsignacion.value = 'Ingresa los días trabajados que corresponden a este proyecto.'; return }
    if (days > Number(fuenteSeleccionada.value?.dias_disponibles || 0)) { errorAsignacion.value = 'Los días superan el saldo disponible de esta planilla.'; return }
  } else if (!Number.isFinite(amount) || amount <= 0 || Math.round(amount * 100) !== amount * 100) { errorAsignacion.value = 'Ingresa un importe positivo con hasta 2 decimales.'; return }
  if (amount > available) { errorAsignacion.value = `El importe supera el saldo disponible de ${dinero(available)}.`; return }
  guardandoAsignacion.value = true
  try {
    await proyectosService.asignar(proyectoActual.value.id, { ...asignacion.value, monto: amount })
    dialogAsignacion.value = false
    mensaje.value = 'Movimiento asignado al proyecto.'
    await abrirDetalle(proyectoActual.value)
  } catch (err) { errorAsignacion.value = err.message }
  finally { guardandoAsignacion.value = false }
}
function puedeQuitar(row) {
  const type = row.fuente_tipo || ({ INGRESO: 'FACTURA', COSTO_DIRECTO: 'COMPRA', COSTO_INDIRECTO: 'COMPRA', MANO_OBRA: 'PLANILLA', HORAS_EXTRA: 'PLANILLA' })[row.categoria]
  return permisoFuente(type)
}
function confirmarQuitar(row) {
  $q.dialog({ title: 'Quitar asignación', message: 'Se quitará este vínculo analítico del proyecto. El asiento contable original no cambiará.', cancel: true, persistent: true })
    .onOk(async () => {
      errorDetalle.value = ''
      try {
        await proyectosService.quitarAsignacion(proyectoActual.value.id, row.id)
        await abrirDetalle(proyectoActual.value)
      } catch (err) { errorDetalle.value = err.message }
    })
}

onMounted(() => { cargarProyectos(); cargarEmpleados() })
</script>
