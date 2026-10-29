# Guía de defensa — Entrega 4

Cada integrante debe practicar estas respuestas usando el código y una base de demostración; no memorizar afirmaciones que no pueda comprobar.

1. Identificar las ocho entidades principales y las dos N:M. Mostrar los detalles y sus FK en el relacional.
2. Explicar 1FN, 2FN y 3FN con VENTA–CLIENTE–DETALLE_VENTA–PRODUCTO–CATEGORIA. Justificar importes históricos almacenados como decisión controlada.
3. Mostrar PK, UNIQUE de VIN/motor, FK, CHECK y NOT NULL. Explicar RESTRICT frente a CASCADE y por qué los documentos emitidos no se borran.
4. Ejecutar una compra y una venta en la base de demostración; explicar cantidad, costo/precio, descuento y commit/rollback.
5. Demostrar dos procedimientos y dos triggers. Distinguir la venta web por SP de la compra identificada por servicio Python.
6. Probar un rechazo por falta de stock y mostrar que no quedó una cabecera parcial.
7. Diferenciar existencia física, reservada, disponible y en tránsito. Explicar qué cambia en cada estado del traslado.
8. Mostrar por qué una unidad devuelta puede venderse otra vez sin duplicar su VIN en UNIDAD_PRODUCTO.
9. Mostrar qué puede hacer Bodega con proveedores y por qué no basta con ocultar un botón: rutas, validación del cargo y permisos SQL.
10. Actualizar una cabecera como Administración y enseñar la auditoría; anular y comprobar el Kardex.
11. Explicar un conteo desactualizado y el campo de revisión de inventario.
12. Abrir el resultado de un respaldo y explicar cifrado, clave de recuperación, retención y prueba de restauración.
13. Explicar consultas parametrizadas, CSRF, hash de contraseñas, suspensión progresiva y separación de conexión/interfaz.
14. Mostrar INSTALL.md, la instalación completa, 50 datos por entidad, casos de prueba y el tag entrega-4.
15. Reconocer el apoyo de IA, mostrar la bitácora y explicar qué comprobó el equipo personalmente.

## Demostración sugerida

Login → compra identificada → inventario local → venta → Kardex → propuesta de proveedor desde Bodega → aprobación desde Administración → traslado aprobado/reservado/despachado/recibido → devolución o corrección de cabecera → respaldo verificado.

La información sensible, tokens y claves de recuperación no se muestran durante la presentación. La defensa oral y las firmas pertenecen al equipo; este documento solo sirve para prepararlas.
