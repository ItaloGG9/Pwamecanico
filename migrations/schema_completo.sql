-- =============================================
-- PWAmecanico — Esquema completo de base de datos
-- Pegar en Railway → tu DB → Query
-- =============================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- TALLERES
CREATE TABLE talleres (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  nombre        VARCHAR(100) NOT NULL,
  rut           VARCHAR(12),
  direccion     TEXT,
  telefono      VARCHAR(20),
  email         VARCHAR(150),
  logo_url      TEXT,
  plan          VARCHAR(20) NOT NULL DEFAULT 'starter' CHECK (plan IN ('starter','taller','pro')),
  activo        BOOLEAN NOT NULL DEFAULT true,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- USUARIOS
CREATE TABLE usuarios (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  taller_id     UUID NOT NULL REFERENCES talleres(id) ON DELETE CASCADE,
  nombre        VARCHAR(100) NOT NULL,
  email         VARCHAR(150) NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  rol           VARCHAR(30) NOT NULL DEFAULT 'mecanico' CHECK (rol IN ('admin','mecanico','recepcion')),
  activo        BOOLEAN NOT NULL DEFAULT true,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_usuarios_taller ON usuarios(taller_id);
CREATE INDEX idx_usuarios_email  ON usuarios(email);

-- CLIENTES
CREATE TABLE clientes (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  taller_id     UUID NOT NULL REFERENCES talleres(id) ON DELETE CASCADE,
  nombre        VARCHAR(150) NOT NULL,
  rut           VARCHAR(12),
  telefono      VARCHAR(20),
  email         VARCHAR(150),
  direccion     TEXT,
  notas         TEXT,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_clientes_taller ON clientes(taller_id);

-- VEHÍCULOS
CREATE TABLE vehiculos (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  taller_id     UUID NOT NULL REFERENCES talleres(id) ON DELETE CASCADE,
  cliente_id    UUID NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
  patente       VARCHAR(10) NOT NULL,
  marca         VARCHAR(60),
  modelo        VARCHAR(60),
  anio          SMALLINT,
  color         VARCHAR(40),
  vin           VARCHAR(17),
  km_actual     INTEGER DEFAULT 0,
  notas         TEXT,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (taller_id, patente)
);
CREATE INDEX idx_vehiculos_taller  ON vehiculos(taller_id);
CREATE INDEX idx_vehiculos_cliente ON vehiculos(cliente_id);

-- PROVEEDORES
CREATE TABLE proveedores (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  taller_id     UUID NOT NULL REFERENCES talleres(id) ON DELETE CASCADE,
  nombre        VARCHAR(150) NOT NULL,
  rut           VARCHAR(12),
  contacto      VARCHAR(100),
  telefono      VARCHAR(20),
  email         VARCHAR(150),
  condiciones   TEXT,
  activo        BOOLEAN NOT NULL DEFAULT true,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_proveedores_taller ON proveedores(taller_id);

-- PRODUCTOS
CREATE TABLE productos (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  taller_id       UUID NOT NULL REFERENCES talleres(id) ON DELETE CASCADE,
  proveedor_id    UUID REFERENCES proveedores(id) ON DELETE SET NULL,
  nombre          VARCHAR(150) NOT NULL,
  sku             VARCHAR(60),
  descripcion     TEXT,
  imagen_url      TEXT,
  compatibilidad  TEXT,
  stock_actual    INTEGER NOT NULL DEFAULT 0,
  stock_minimo    INTEGER NOT NULL DEFAULT 1,
  precio_costo    NUMERIC(12,2) DEFAULT 0,
  precio_venta    NUMERIC(12,2) DEFAULT 0,
  unidad          VARCHAR(20) DEFAULT 'unidad',
  activo          BOOLEAN NOT NULL DEFAULT true,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_productos_taller ON productos(taller_id);

-- MOVIMIENTOS DE STOCK
CREATE TABLE movimientos_stock (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  taller_id       UUID NOT NULL REFERENCES talleres(id) ON DELETE CASCADE,
  producto_id     UUID NOT NULL REFERENCES productos(id) ON DELETE CASCADE,
  usuario_id      UUID REFERENCES usuarios(id) ON DELETE SET NULL,
  tipo            VARCHAR(20) NOT NULL CHECK (tipo IN ('entrada','salida','ajuste')),
  cantidad        INTEGER NOT NULL,
  stock_anterior  INTEGER NOT NULL,
  stock_nuevo     INTEGER NOT NULL,
  motivo          TEXT,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_mov_stock_producto ON movimientos_stock(producto_id);

-- CITAS
CREATE TABLE citas (
  id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  taller_id         UUID NOT NULL REFERENCES talleres(id) ON DELETE CASCADE,
  cliente_id        UUID NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
  vehiculo_id       UUID REFERENCES vehiculos(id) ON DELETE SET NULL,
  mecanico_id       UUID REFERENCES usuarios(id) ON DELETE SET NULL,
  fecha_hora        TIMESTAMPTZ NOT NULL,
  duracion_min      INTEGER DEFAULT 60,
  descripcion       TEXT,
  estado            VARCHAR(20) NOT NULL DEFAULT 'pendiente'
                    CHECK (estado IN ('pendiente','confirmada','en_curso','completada','cancelada')),
  gcal_event_id     TEXT,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_citas_taller ON citas(taller_id);
CREATE INDEX idx_citas_fecha  ON citas(fecha_hora);

-- ÓRDENES DE TRABAJO
CREATE TABLE ordenes_trabajo (
  id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  taller_id           UUID NOT NULL REFERENCES talleres(id) ON DELETE CASCADE,
  numero_ot           VARCHAR(20) NOT NULL DEFAULT '',
  cita_id             UUID REFERENCES citas(id) ON DELETE SET NULL,
  cliente_id          UUID NOT NULL REFERENCES clientes(id),
  vehiculo_id         UUID NOT NULL REFERENCES vehiculos(id),
  mecanico_id         UUID REFERENCES usuarios(id) ON DELETE SET NULL,
  estado              VARCHAR(30) NOT NULL DEFAULT 'recibido'
                      CHECK (estado IN ('recibido','diagnostico','en_reparacion','espera_repuesto','listo','entregado')),
  km_ingreso          INTEGER,
  nivel_combustible   SMALLINT CHECK (nivel_combustible BETWEEN 0 AND 8),
  diagnostico         TEXT,
  trabajo_realizado   TEXT,
  fecha_ingreso       TIMESTAMPTZ NOT NULL DEFAULT now(),
  fecha_entrega_est   TIMESTAMPTZ,
  fecha_entrega_real  TIMESTAMPTZ,
  total_neto          NUMERIC(12,2) DEFAULT 0,
  total_iva           NUMERIC(12,2) DEFAULT 0,
  total_final         NUMERIC(12,2) DEFAULT 0,
  notas_internas      TEXT,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_ot_taller  ON ordenes_trabajo(taller_id);
CREATE INDEX idx_ot_cliente ON ordenes_trabajo(cliente_id);
CREATE INDEX idx_ot_estado  ON ordenes_trabajo(estado);

-- ITEMS DE OT
CREATE TABLE ot_items (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  ot_id           UUID NOT NULL REFERENCES ordenes_trabajo(id) ON DELETE CASCADE,
  tipo            VARCHAR(15) NOT NULL CHECK (tipo IN ('producto','servicio')),
  producto_id     UUID REFERENCES productos(id) ON DELETE SET NULL,
  descripcion     TEXT NOT NULL,
  cantidad        NUMERIC(10,2) NOT NULL DEFAULT 1,
  precio_unitario NUMERIC(12,2) NOT NULL DEFAULT 0,
  subtotal        NUMERIC(12,2) GENERATED ALWAYS AS (cantidad * precio_unitario) STORED
);
CREATE INDEX idx_ot_items_ot ON ot_items(ot_id);

-- COTIZACIONES
CREATE TABLE cotizaciones (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  taller_id     UUID NOT NULL REFERENCES talleres(id) ON DELETE CASCADE,
  numero        VARCHAR(20) NOT NULL DEFAULT '',
  cliente_id    UUID NOT NULL REFERENCES clientes(id),
  vehiculo_id   UUID REFERENCES vehiculos(id) ON DELETE SET NULL,
  estado        VARCHAR(20) NOT NULL DEFAULT 'borrador'
                CHECK (estado IN ('borrador','enviada','aprobada','rechazada')),
  validez_dias  INTEGER DEFAULT 7,
  notas         TEXT,
  total_neto    NUMERIC(12,2) DEFAULT 0,
  total_iva     NUMERIC(12,2) DEFAULT 0,
  total_final   NUMERIC(12,2) DEFAULT 0,
  ot_id         UUID REFERENCES ordenes_trabajo(id) ON DELETE SET NULL,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_cotizaciones_taller  ON cotizaciones(taller_id);
CREATE INDEX idx_cotizaciones_cliente ON cotizaciones(cliente_id);

-- ITEMS DE COTIZACIÓN
CREATE TABLE cotizacion_items (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  cotizacion_id   UUID NOT NULL REFERENCES cotizaciones(id) ON DELETE CASCADE,
  tipo            VARCHAR(15) NOT NULL CHECK (tipo IN ('producto','servicio')),
  producto_id     UUID REFERENCES productos(id) ON DELETE SET NULL,
  descripcion     TEXT NOT NULL,
  cantidad        NUMERIC(10,2) NOT NULL DEFAULT 1,
  precio_unitario NUMERIC(12,2) NOT NULL DEFAULT 0,
  subtotal        NUMERIC(12,2) GENERATED ALWAYS AS (cantidad * precio_unitario) STORED
);
CREATE INDEX idx_cot_items ON cotizacion_items(cotizacion_id);

-- EMPLEADOS
CREATE TABLE empleados (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  taller_id       UUID NOT NULL REFERENCES talleres(id) ON DELETE CASCADE,
  usuario_id      UUID REFERENCES usuarios(id) ON DELETE SET NULL,
  nombre          VARCHAR(150) NOT NULL,
  rut             VARCHAR(12),
  cargo           VARCHAR(80),
  fecha_ingreso   DATE,
  sueldo_base     NUMERIC(12,2) DEFAULT 0,
  activo          BOOLEAN NOT NULL DEFAULT true,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_empleados_taller ON empleados(taller_id);

-- CATÁLOGO DE SERVICIOS
CREATE TABLE servicios_catalogo (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  taller_id       UUID NOT NULL REFERENCES talleres(id) ON DELETE CASCADE,
  nombre          VARCHAR(150) NOT NULL,
  descripcion     TEXT,
  precio          NUMERIC(12,2) NOT NULL DEFAULT 0,
  duracion_min    INTEGER DEFAULT 60,
  activo          BOOLEAN NOT NULL DEFAULT true,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_servicios_taller ON servicios_catalogo(taller_id);

-- RECEPCIONES
CREATE TABLE recepciones (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  taller_id       UUID NOT NULL REFERENCES talleres(id) ON DELETE CASCADE,
  ot_id           UUID NOT NULL REFERENCES ordenes_trabajo(id) ON DELETE CASCADE,
  km_ingreso      INTEGER,
  nivel_gasolina  SMALLINT,
  tiene_llanta    BOOLEAN DEFAULT false,
  tiene_gata      BOOLEAN DEFAULT false,
  tiene_triangulo BOOLEAN DEFAULT false,
  tiene_extintor  BOOLEAN DEFAULT false,
  danios_visibles TEXT,
  firma_cliente   TEXT,
  firmado_en      TIMESTAMPTZ,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =============================================
-- TRIGGERS: updated_at automático
-- =============================================
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = now(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_talleres_updated_at     BEFORE UPDATE ON talleres          FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_usuarios_updated_at     BEFORE UPDATE ON usuarios          FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_clientes_updated_at     BEFORE UPDATE ON clientes          FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_vehiculos_updated_at    BEFORE UPDATE ON vehiculos         FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_productos_updated_at    BEFORE UPDATE ON productos         FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_citas_updated_at        BEFORE UPDATE ON citas             FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_ot_updated_at           BEFORE UPDATE ON ordenes_trabajo   FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_cotizaciones_updated_at BEFORE UPDATE ON cotizaciones      FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_empleados_updated_at    BEFORE UPDATE ON empleados         FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- =============================================
-- TRIGGER: numeración automática OT
-- =============================================
CREATE OR REPLACE FUNCTION generar_numero_ot()
RETURNS TRIGGER AS $$
DECLARE ultimo INTEGER;
BEGIN
  SELECT COALESCE(MAX(CAST(REGEXP_REPLACE(numero_ot, '[^0-9]', '', 'g') AS INTEGER)), 0)
  INTO ultimo FROM ordenes_trabajo WHERE taller_id = NEW.taller_id;
  NEW.numero_ot = 'OT-' || LPAD((ultimo + 1)::TEXT, 5, '0');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_numero_ot
  BEFORE INSERT ON ordenes_trabajo
  FOR EACH ROW WHEN (NEW.numero_ot IS NULL OR NEW.numero_ot = '')
  EXECUTE FUNCTION generar_numero_ot();

-- =============================================
-- TRIGGER: numeración automática cotizaciones
-- =============================================
CREATE OR REPLACE FUNCTION generar_numero_cotizacion()
RETURNS TRIGGER AS $$
DECLARE ultimo INTEGER;
BEGIN
  SELECT COALESCE(MAX(CAST(REGEXP_REPLACE(numero, '[^0-9]', '', 'g') AS INTEGER)), 0)
  INTO ultimo FROM cotizaciones WHERE taller_id = NEW.taller_id;
  NEW.numero = 'COT-' || LPAD((ultimo + 1)::TEXT, 5, '0');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_numero_cotizacion
  BEFORE INSERT ON cotizaciones
  FOR EACH ROW WHEN (NEW.numero IS NULL OR NEW.numero = '')
  EXECUTE FUNCTION generar_numero_cotizacion();
