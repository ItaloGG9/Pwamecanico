-- ============================================================
-- Migración 002: Índices optimizados para queries multi-tenant
-- Aplicar en Supabase SQL Editor
-- ============================================================

-- 1. Composite indexes para queries multi-tenant + filtros frecuentes
CREATE INDEX IF NOT EXISTS idx_ordenes_taller_estado
  ON ordenes_trabajo(taller_id, estado);

CREATE INDEX IF NOT EXISTS idx_ordenes_taller_fecha
  ON ordenes_trabajo(taller_id, fecha_ingreso DESC);

CREATE INDEX IF NOT EXISTS idx_citas_taller_fecha_estado
  ON citas(taller_id, fecha_hora, estado);

CREATE INDEX IF NOT EXISTS idx_productos_taller_activo_nombre
  ON productos(taller_id, activo, nombre);

CREATE INDEX IF NOT EXISTS idx_clientes_taller_nombre
  ON clientes(taller_id, nombre);

CREATE INDEX IF NOT EXISTS idx_cotizaciones_taller_estado_fecha
  ON cotizaciones(taller_id, estado, created_at DESC);

-- 2. Búsqueda por campos únicos frecuentes
CREATE INDEX IF NOT EXISTS idx_clientes_rut
  ON clientes(rut) WHERE rut IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_vehiculos_patente
  ON vehiculos(patente);

CREATE INDEX IF NOT EXISTS idx_vehiculos_taller_patente
  ON vehiculos(taller_id, patente);

CREATE INDEX IF NOT EXISTS idx_productos_sku
  ON productos(sku) WHERE sku IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_ordenes_numero
  ON ordenes_trabajo(numero_ot);

CREATE INDEX IF NOT EXISTS idx_cotizaciones_numero
  ON cotizaciones(numero);

-- 3. Partial index para bajo-stock (evita table scan completo)
CREATE INDEX IF NOT EXISTS idx_productos_bajo_stock
  ON productos(taller_id, nombre)
  WHERE activo = true AND stock_actual <= stock_minimo;

-- 4. Índices para email/teléfono (login, búsqueda)
CREATE INDEX IF NOT EXISTS idx_clientes_email
  ON clientes(email) WHERE email IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_clientes_telefono
  ON clientes(telefono) WHERE telefono IS NOT NULL;

-- 5. Índice para auditoría de movimientos de stock
CREATE INDEX IF NOT EXISTS idx_movimientos_taller_producto_fecha
  ON movimientos_stock(taller_id, producto_id, created_at DESC);

-- 6. Índice para filtrar citas activas (excluye canceladas)
CREATE INDEX IF NOT EXISTS idx_citas_activas
  ON citas(taller_id, fecha_hora)
  WHERE estado != 'cancelada';

-- 7. Índice para ordenes activas (excluye entregadas)
CREATE INDEX IF NOT EXISTS idx_ordenes_activas
  ON ordenes_trabajo(taller_id, estado, fecha_ingreso DESC)
  WHERE estado != 'entregado';

-- Verificar índices creados
SELECT
  indexname,
  tablename,
  indexdef
FROM pg_indexes
WHERE schemaname = 'public'
  AND tablename IN ('ordenes_trabajo', 'citas', 'productos', 'clientes', 'cotizaciones', 'vehiculos', 'movimientos_stock')
ORDER BY tablename, indexname;
