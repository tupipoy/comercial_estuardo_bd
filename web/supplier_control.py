"""Propuestas y administración de proveedores, dentro de una transacción."""
import json
from inventory_control import actor, require

FIELDS = ("nit", "razon_social", "contacto", "telefono", "correo", "direccion")


def form_data(form):
    return {field: form.get(field, "").strip() for field in FIELDS}


def validate(data):
    errors = []
    for field, label, limit in (("nit", "NIT", 15), ("razon_social", "Razón social", 150),
                                ("contacto", "Contacto", 100), ("telefono", "Teléfono", 15),
                                ("correo", "Correo", 100), ("direccion", "Dirección", 200)):
        if len(data[field]) > limit:
            errors.append(f"{label} no puede superar {limit} caracteres.")
    for field, label in (("nit", "El NIT"), ("razon_social", "La razón social"), ("telefono", "El teléfono")):
        if not data[field]:
            errors.append(f"{label} es obligatorio.")
    if data["correo"] and ("@" not in data["correo"] or " " in data["correo"]):
        errors.append("Ingresa un correo válido.")
    return errors


def snapshot(row):
    return {key: row.get(key) if row.get(key) is not None else "" for key in (*FIELDS, "estado")}


def event(cursor, employee, action, proposal=None, provider=None, old=None, new=None, note=None):
    cursor.execute("""INSERT INTO EVENTO_PROVEEDOR(id_propuesta,id_proveedor,id_empleado,accion,datos_anteriores,datos_nuevos,observacion)
                      VALUES(%s,%s,%s,%s,%s,%s,%s)""", (proposal, provider, employee, action,
                      json.dumps(snapshot(old), ensure_ascii=False) if old else None,
                      json.dumps(snapshot(new), ensure_ascii=False) if new else None, note))


def propose(cursor, employee, data):
    user = actor(cursor, employee)
    require(user["cargo"] in ("Administrador", "Bodega"), "No tienes permiso para proponer proveedores.")
    require(not validate(data), " ".join(validate(data)))
    cursor.execute("SELECT id_proveedor FROM PROVEEDOR WHERE nit=%s", (data["nit"],))
    require(not cursor.fetchone(), "Ya existe un proveedor con ese NIT, activo o inactivo. Consulta el catálogo.")
    cursor.execute("SELECT id_propuesta FROM PROPUESTA_PROVEEDOR WHERE nit=%s AND estado='Pendiente'", (data["nit"],))
    require(not cursor.fetchone(), "Ya existe una propuesta pendiente con ese NIT.")
    cursor.execute("""INSERT INTO PROPUESTA_PROVEEDOR(nit,razon_social,contacto,telefono,correo,direccion,id_solicitante)
                      VALUES(%s,%s,%s,%s,%s,%s,%s)""", (*[data[key] or None for key in FIELDS], employee))
    proposal = cursor.lastrowid
    event(cursor, employee, "Propuesta", proposal=proposal, new={**data, "estado": "Pendiente"})
    return proposal


def resolve(cursor, employee, proposal, approve, data=None, note=""):
    actor(cursor, employee, admin=True)
    cursor.execute("SELECT * FROM PROPUESTA_PROVEEDOR WHERE id_propuesta=%s FOR UPDATE", (proposal,))
    original = cursor.fetchone()
    require(original and original["estado"] == "Pendiente", "La propuesta ya fue resuelta o no existe.")
    provider = None
    if approve:
        data = data if data is not None else {key: original[key] or "" for key in FIELDS}
        require(not validate(data), " ".join(validate(data)))
        cursor.execute("SELECT id_proveedor FROM PROVEEDOR WHERE nit=%s", (data["nit"],))
        require(not cursor.fetchone(), "Ya existe un proveedor con ese NIT. Rechaza la propuesta duplicada o corrige los datos.")
        cursor.execute("INSERT INTO PROVEEDOR(nit,razon_social,contacto,telefono,correo,direccion,estado) VALUES(%s,%s,%s,%s,%s,%s,1)", tuple(data[key] or None for key in FIELDS))
        provider = cursor.lastrowid
        cursor.execute("""UPDATE PROPUESTA_PROVEEDOR SET nit=%s,razon_social=%s,contacto=%s,telefono=%s,correo=%s,direccion=%s,
                          estado='Aprobada',id_proveedor=%s,id_responsable=%s,fecha_resolucion=NOW(6),observacion=%s
                          WHERE id_propuesta=%s""", (*[data[key] or None for key in FIELDS], provider, employee, note or None, proposal))
    else:
        require(note.strip(), "Escribe el motivo del rechazo.")
        data = {key: original[key] or "" for key in FIELDS}
        cursor.execute("UPDATE PROPUESTA_PROVEEDOR SET estado='Rechazada',id_responsable=%s,fecha_resolucion=NOW(6),observacion=%s WHERE id_propuesta=%s", (employee, note, proposal))
    event(cursor, employee, "Aprobación" if approve else "Rechazo", proposal, provider, original,
          {**data, "estado": "Aprobada" if approve else "Rechazada"}, note)
    return provider


def update(cursor, employee, provider, data):
    actor(cursor, employee, admin=True)
    require(not validate(data), " ".join(validate(data)))
    cursor.execute("SELECT * FROM PROVEEDOR WHERE id_proveedor=%s FOR UPDATE", (provider,))
    original = cursor.fetchone()
    require(original, "El proveedor no existe.")
    cursor.execute("UPDATE PROVEEDOR SET nit=%s,razon_social=%s,contacto=%s,telefono=%s,correo=%s,direccion=%s WHERE id_proveedor=%s", (*[data[key] or None for key in FIELDS], provider))
    event(cursor, employee, "Edición", provider=provider, old=original, new={**data, "estado": original["estado"]})


def deactivate(cursor, employee, provider):
    actor(cursor, employee, admin=True)
    cursor.execute("SELECT * FROM PROVEEDOR WHERE id_proveedor=%s FOR UPDATE", (provider,))
    original = cursor.fetchone()
    require(original and original["estado"] == 1, "El proveedor ya está inactivo o no existe.")
    cursor.execute("UPDATE PROVEEDOR SET estado=0 WHERE id_proveedor=%s", (provider,))
    event(cursor, employee, "Desactivación", provider=provider, old=original, new={**original, "estado": 0})
