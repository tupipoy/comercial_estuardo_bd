-- Archivo: sql/migrations/07_transfer_workflow.sql
-- Autor: Equipo Comercial Estuardo
-- Descripción: actualiza de forma incremental el esquema existente.
-- Dependencias: Esquema y objetos previos según INSTALL.md; no ejecutar sobre producción sin respaldo.
-- Agrega aprobacion, despacho y recepcion al flujo de traslados.
-- Ejecutar una sola vez sobre una base que ya tenga sql/migrations/06.
USE comercial_estuardo_db;

ALTER TABLE TRASLADO
    MODIFY estado VARCHAR(30) NOT NULL DEFAULT 'Pendiente de aprobación',
    ADD COLUMN id_empleado_aprobacion INT NULL AFTER id_empleado,
    ADD COLUMN fecha_aprobacion DATETIME NULL AFTER id_empleado_aprobacion,
    ADD COLUMN observacion_resolucion VARCHAR(500) NULL AFTER fecha_aprobacion,
    ADD COLUMN id_empleado_despacho INT NULL AFTER observacion_resolucion,
    ADD COLUMN fecha_despacho DATETIME NULL AFTER id_empleado_despacho,
    ADD COLUMN id_empleado_recepcion INT NULL AFTER fecha_despacho,
    ADD COLUMN fecha_recepcion DATETIME NULL AFTER id_empleado_recepcion,
    ADD COLUMN observacion_recepcion VARCHAR(500) NULL AFTER fecha_recepcion,
    DROP CHECK chk_traslado_estado,
    ADD CONSTRAINT chk_traslado_estado CHECK (estado IN (
        'Pendiente de aprobación', 'Rechazado', 'Aprobado',
        'En tránsito', 'Completado', 'Anulado'
    )),
    ADD CONSTRAINT fk_traslado_aprobador FOREIGN KEY (id_empleado_aprobacion)
        REFERENCES EMPLEADO(id_empleado) ON UPDATE CASCADE ON DELETE RESTRICT,
    ADD CONSTRAINT fk_traslado_despachador FOREIGN KEY (id_empleado_despacho)
        REFERENCES EMPLEADO(id_empleado) ON UPDATE CASCADE ON DELETE RESTRICT,
    ADD CONSTRAINT fk_traslado_receptor FOREIGN KEY (id_empleado_recepcion)
        REFERENCES EMPLEADO(id_empleado) ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE DETALLE_TRASLADO
    ADD COLUMN cantidad_recibida INT NULL AFTER cantidad,
    ADD CONSTRAINT chk_dettraslado_recibida CHECK (
        cantidad_recibida IS NULL OR (cantidad_recibida >= 0 AND cantidad_recibida <= cantidad)
    );

-- Los traslados previos ya descontaron y acreditaron el total en un paso.
UPDATE DETALLE_TRASLADO d
INNER JOIN TRASLADO t ON t.id_traslado=d.id_traslado
SET d.cantidad_recibida=d.cantidad
WHERE t.estado='Completado';
