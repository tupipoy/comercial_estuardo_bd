"""Operaciones de inventario; el llamador confirma o revierte la transacción."""
import json
from decimal import Decimal, ROUND_HALF_UP


class InventoryError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise InventoryError(message)


def actor(cursor, employee, branch=None, admin=False):
    cursor.execute("SELECT id_empleado,cargo,id_sucursal FROM EMPLEADO WHERE id_empleado=%s AND estado=1", (employee,))
    user = cursor.fetchone()
    require(user, "La cuenta ya no está activa.")
    require(user["cargo"] == "Administrador" or not admin, "Solo Administración puede autorizar esta operación.")
    if branch is not None:
        cursor.execute("SELECT id_sucursal FROM SUCURSAL WHERE id_sucursal=%s AND estado=1", (branch,))
        require(cursor.fetchone(), "La sucursal debe estar activa.")
    if branch is not None and user["cargo"] != "Administrador":
        require(user["cargo"] == "Bodega" and user["id_sucursal"] == branch,
                "Esta operación corresponde a Bodega de la sucursal indicada.")
    return user


def context(cursor, employee, kind, reference, reason=None):
    cursor.execute("SET @mov_actor=%s,@mov_tipo=%s,@mov_referencia=%s,@mov_motivo=%s",
                   (employee, kind, reference, reason))


def stock(cursor, branch, product):
    cursor.execute("INSERT INTO INVENTARIO_SUCURSAL(id_sucursal,id_producto) VALUES(%s,%s) ON DUPLICATE KEY UPDATE id_producto=VALUES(id_producto)", (branch, product))
    cursor.execute("SELECT * FROM INVENTARIO_SUCURSAL WHERE id_sucursal=%s AND id_producto=%s FOR UPDATE", (branch, product))
    return cursor.fetchone()


def product(cursor, product_id):
    cursor.execute("SELECT * FROM PRODUCTO WHERE id_producto=%s", (product_id,))
    row = cursor.fetchone()
    require(row, "El producto no existe.")
    return row


def serial_pairs(text):
    pairs = []
    for line in text.splitlines():
        if not line.strip():
            continue
        values = [part.strip().upper() for part in line.split("|")]
        require(len(values) == 2 and all(values) and max(map(len, values)) <= 50,
                "Escribe una unidad por línea con el formato VIN | MOTOR (máximo 50 caracteres por dato).")
        pairs.append({"vin": values[0], "motor": values[1]})
    require(len({p["vin"] for p in pairs}) == len(pairs) and len({p["motor"] for p in pairs}) == len(pairs),
            "No repitas VIN ni motores en la misma operación.")
    return pairs


def add_unit(cursor, product_id, branch, pair, purchase_detail=None):
    cursor.execute("""INSERT INTO UNIDAD_PRODUCTO(id_producto,id_sucursal,vin_chasis,numero_motor,id_detalle_compra)
                      VALUES(%s,%s,%s,%s,%s)""", (product_id, branch, pair["vin"], pair["motor"], purchase_detail))
    return cursor.lastrowid


def register_purchase(cursor, employee, branch, order, provider, lines):
    actor(cursor, employee, branch)
    cursor.execute("SELECT id_proveedor FROM PROVEEDOR WHERE id_proveedor=%s AND estado=1", (provider,))
    require(cursor.fetchone(), "El proveedor está inactivo.")
    total = sum(Decimal(line["costo_unitario"]) * line["cantidad"] for line in lines)
    cursor.execute("""INSERT INTO COMPRA(numero_orden,total_compra,estado_recepcion,id_proveedor,id_empleado,id_sucursal)
                      VALUES(%s,%s,'Recibido',%s,%s,%s)""", (order, total, provider, employee, branch))
    purchase_id = cursor.lastrowid
    context(cursor, employee, "Compra", f"Compra #{purchase_id}")
    for line in sorted(lines, key=lambda item: item["id_producto"]):
        p = product(cursor, line["id_producto"])
        require(p["estado"] == 1, "Uno de los productos está inactivo.")
        pairs = serial_pairs(line.get("series", ""))
        require(not p["requiere_serie"] or len(pairs) == line["cantidad"],
                f"{p['nombre']}: registra un VIN y motor por cada unidad recibida.")
        require(p["requiere_serie"] or not pairs, "Ese producto no utiliza números de serie.")
        require(Decimal(line["costo_unitario"]) <= p["precio_venta"], "El costo supera el precio de venta.")
        stock(cursor, branch, p["id_producto"])
        cursor.execute("""INSERT INTO DETALLE_COMPRA(id_compra,id_producto,cantidad,costo_unitario,subtotal)
                          VALUES(%s,%s,%s,%s,%s)""", (purchase_id, p["id_producto"], line["cantidad"], line["costo_unitario"], Decimal(line["costo_unitario"]) * line["cantidad"]))
        detail_id = cursor.lastrowid
        for pair in pairs:
            add_unit(cursor, p["id_producto"], branch, pair, detail_id)
        cursor.execute("UPDATE INVENTARIO_SUCURSAL SET stock_actual=stock_actual+%s WHERE id_sucursal=%s AND id_producto=%s", (line["cantidad"], branch, p["id_producto"]))
        cursor.execute("UPDATE PRODUCTO SET precio_costo=%s WHERE id_producto=%s", (line["costo_unitario"], p["id_producto"]))
    return purchase_id


def event(cursor, transfer_id, employee, action, note=None):
    cursor.execute("INSERT INTO EVENTO_TRASLADO(id_traslado,id_empleado,accion,observacion) VALUES(%s,%s,%s,%s)", (transfer_id, employee, action, note))


def request_transfer(cursor, employee, origin, destination, number, lines):
    actor(cursor, employee, origin)
    require(origin != destination, "El origen y el destino deben ser diferentes.")
    cursor.execute("SELECT COUNT(*) n FROM SUCURSAL WHERE id_sucursal IN (%s,%s) AND estado=1", (origin, destination))
    require(cursor.fetchone()["n"] == 2, "Las sucursales deben estar activas.")
    cursor.execute("""INSERT INTO TRASLADO(numero_traslado,id_sucursal_origen,id_sucursal_destino,id_empleado)
                      VALUES(%s,%s,%s,%s)""", (number, origin, destination, employee))
    transfer_id = cursor.lastrowid
    for line in sorted(lines, key=lambda item: item["id_producto"]):
        p = product(cursor, line["id_producto"])
        s = stock(cursor, origin, p["id_producto"])
        require(s["stock_actual"] - s["stock_reservado"] >= line["cantidad"], "No hay suficientes unidades disponibles.")
        cursor.execute("INSERT INTO DETALLE_TRASLADO(id_traslado,id_producto,cantidad) VALUES(%s,%s,%s)", (transfer_id, p["id_producto"], line["cantidad"]))
        units = line.get("unidades", [])
        if p["requiere_serie"]:
            require(len(units) == line["cantidad"] and len(set(units)) == len(units), f"Selecciona las unidades exactas de {p['nombre']}.")
            for unit_id in sorted(units):
                cursor.execute("SELECT * FROM UNIDAD_PRODUCTO WHERE id_unidad=%s FOR UPDATE", (unit_id,))
                unit = cursor.fetchone()
                require(unit and unit["id_producto"] == p["id_producto"] and unit["id_sucursal"] == origin and unit["estado"] == "Disponible", "Una unidad elegida ya no está disponible en origen.")
                cursor.execute("INSERT INTO TRASLADO_UNIDAD(id_traslado,id_unidad) VALUES(%s,%s)", (transfer_id, unit_id))
        else:
            require(not units, "El producto no utiliza unidades identificadas.")
    event(cursor, transfer_id, employee, "Solicitud")
    return transfer_id


def transfer_action(cursor, employee, transfer_id, action, note="", received=None):
    cursor.execute("SELECT * FROM TRASLADO WHERE id_traslado=%s FOR UPDATE", (transfer_id,))
    t = cursor.fetchone()
    require(t, "El traslado no existe.")
    cursor.execute("SELECT d.*,p.requiere_serie FROM DETALLE_TRASLADO d JOIN PRODUCTO p USING(id_producto) WHERE id_traslado=%s ORDER BY id_producto", (transfer_id,))
    details = cursor.fetchall()
    origin, destination = t["id_sucursal_origen"], t["id_sucursal_destino"]
    if action in ("aprobar", "rechazar", "anular"):
        actor(cursor, employee, admin=True)
        require(t["estado"] in (("Pendiente de aprobación", "Aprobado") if action == "anular" else ("Pendiente de aprobación",)), "El estado del traslado ya cambió.")
        require(action == "aprobar" or note.strip(), "Escribe el motivo de la decisión.")
        context(cursor, employee, "Reserva" if action == "aprobar" else "Liberación de reserva", f"Traslado #{transfer_id}", note)
        for d in details:
            s = stock(cursor, origin, d["id_producto"])
            if action == "aprobar":
                require(s["stock_actual"] - s["stock_reservado"] >= d["cantidad"], "No hay stock disponible para aprobar; otras unidades están reservadas.")
                if d["requiere_serie"]:
                    cursor.execute("SELECT u.* FROM TRASLADO_UNIDAD tu JOIN UNIDAD_PRODUCTO u USING(id_unidad) WHERE tu.id_traslado=%s AND u.id_producto=%s ORDER BY u.id_unidad FOR UPDATE", (transfer_id, d["id_producto"]))
                    units = cursor.fetchall()
                    require(len(units) == d["cantidad"] and all(u["estado"] == "Disponible" and u["id_sucursal"] == origin for u in units), "Las motocicletas de la solicitud ya no están disponibles; crea una nueva solicitud.")
                    cursor.execute("UPDATE UNIDAD_PRODUCTO u JOIN TRASLADO_UNIDAD tu USING(id_unidad) SET u.estado='Reservada',u.id_traslado=%s WHERE tu.id_traslado=%s AND u.id_producto=%s", (transfer_id, transfer_id, d["id_producto"]))
                cursor.execute("UPDATE INVENTARIO_SUCURSAL SET stock_reservado=stock_reservado+%s WHERE id_sucursal=%s AND id_producto=%s", (d["cantidad"], origin, d["id_producto"]))
            elif action == "anular" and t["estado"] == "Aprobado":
                require(s["stock_reservado"] >= d["cantidad"], "La reserva no coincide; revisa el inventario.")
                cursor.execute("UPDATE INVENTARIO_SUCURSAL SET stock_reservado=stock_reservado-%s WHERE id_sucursal=%s AND id_producto=%s", (d["cantidad"], origin, d["id_producto"]))
                cursor.execute("UPDATE UNIDAD_PRODUCTO SET estado='Disponible',id_traslado=NULL WHERE id_traslado=%s AND id_producto=%s AND estado='Reservada'", (transfer_id, d["id_producto"]))
        state = {"aprobar": "Aprobado", "rechazar": "Rechazado", "anular": "Anulado"}[action]
        cursor.execute("UPDATE TRASLADO SET estado=%s,id_empleado_aprobacion=%s,fecha_aprobacion=NOW(),observacion_resolucion=%s WHERE id_traslado=%s", (state, employee, note, transfer_id))
    elif action == "despachar":
        actor(cursor, employee, origin)
        require(t["estado"] == "Aprobado", "El traslado debe estar aprobado para despacharlo.")
        context(cursor, employee, "Despacho de traslado", f"Traslado #{transfer_id}")
        for d in details:
            s = stock(cursor, origin, d["id_producto"])
            require(s["stock_reservado"] >= d["cantidad"] and s["stock_actual"] >= d["cantidad"], "La reserva no tiene existencias suficientes.")
            cursor.execute("UPDATE INVENTARIO_SUCURSAL SET stock_actual=stock_actual-%s,stock_reservado=stock_reservado-%s WHERE id_sucursal=%s AND id_producto=%s", (d["cantidad"], d["cantidad"], origin, d["id_producto"]))
        cursor.execute("UPDATE UNIDAD_PRODUCTO SET estado='En tránsito' WHERE id_traslado=%s AND estado='Reservada'", (transfer_id,))
        cursor.execute("UPDATE TRASLADO SET estado='En tránsito',id_empleado_despacho=%s,fecha_despacho=NOW() WHERE id_traslado=%s", (employee, transfer_id))
    elif action == "recibir":
        actor(cursor, employee, destination)
        require(t["estado"] in ("En tránsito", "Con diferencias"), "El traslado no está pendiente de recepción.")
        received = received or []
        require(len(received) == len(details) and len({r["id_producto"] for r in received}) == len(details), "Completa todas las líneas de recepción.")
        by_product = {r["id_producto"]: r for r in received}
        context(cursor, employee, "Recepción de traslado", f"Traslado #{transfer_id}", note)
        complete = True
        for d in details:
            r = by_product.get(d["id_producto"])
            require(r and (d["cantidad_recibida"] or 0) <= r["cantidad"] <= d["cantidad"], "La recepción acumulada no puede disminuir ni exceder lo enviado.")
            if d["requiere_serie"]:
                cursor.execute("SELECT tu.*,u.id_producto,u.estado,u.id_traslado actual_traslado FROM TRASLADO_UNIDAD tu JOIN UNIDAD_PRODUCTO u USING(id_unidad) WHERE tu.id_traslado=%s AND u.id_producto=%s ORDER BY u.id_unidad FOR UPDATE", (transfer_id, d["id_producto"]))
                units = cursor.fetchall()
                selected = set(r.get("unidades", []))
                require(len(selected) == r["cantidad"] and selected <= {u["id_unidad"] for u in units}, "Marca las motocicletas que llegaron físicamente.")
                require({u["id_unidad"] for u in units if u["recibida"]} <= selected, "Conserva las unidades ya recibidas.")
                for u in units:
                    if u["id_unidad"] in selected and not u["recibida"]:
                        require(u["estado"] == "En tránsito" and u["actual_traslado"] == transfer_id, "La unidad ya no está en este traslado.")
                        cursor.execute("UPDATE UNIDAD_PRODUCTO SET estado='Disponible',id_sucursal=%s,id_traslado=NULL WHERE id_unidad=%s", (destination, u["id_unidad"]))
                        cursor.execute("UPDATE TRASLADO_UNIDAD SET recibida=1 WHERE id_traslado=%s AND id_unidad=%s", (transfer_id, u["id_unidad"]))
            delta = r["cantidad"] - (d["cantidad_recibida"] or 0)
            stock(cursor, destination, d["id_producto"])
            if delta:
                cursor.execute("UPDATE INVENTARIO_SUCURSAL SET stock_actual=stock_actual+%s WHERE id_sucursal=%s AND id_producto=%s", (delta, destination, d["id_producto"]))
            cursor.execute("UPDATE DETALLE_TRASLADO SET cantidad_recibida=%s WHERE id_detalle_traslado=%s", (r["cantidad"], d["id_detalle_traslado"]))
            complete = complete and r["cantidad"] == d["cantidad"]
        require(complete or note.strip(), "Describe los faltantes en la observación de recepción.")
        cursor.execute("UPDATE TRASLADO SET estado=%s,id_empleado_recepcion=%s,fecha_recepcion=NOW(),observacion_recepcion=%s WHERE id_traslado=%s", ("Completado" if complete else "Con diferencias", employee, note, transfer_id))
    else:
        raise InventoryError("Acción no válida.")
    event(cursor, transfer_id, employee, action, note)


def current_units(cursor, branch, product_id):
    cursor.execute("SELECT * FROM UNIDAD_PRODUCTO WHERE id_sucursal=%s AND id_producto=%s AND estado IN ('Disponible','Reservada') ORDER BY id_unidad FOR UPDATE", (branch, product_id))
    return cursor.fetchall()


def register_legacy_unit(cursor, employee, branch, product_id, pair):
    actor(cursor, employee, admin=True)
    p = product(cursor, product_id)
    require(p["requiere_serie"], "Este producto no se controla por unidad.")
    s = stock(cursor, branch, product_id)
    units = current_units(cursor, branch, product_id)
    require(len(units) < s["stock_actual"], "Todas las existencias ya tienen identificación. Registra las entradas mediante compra o conteo.")
    context(cursor, employee, "Identificación", "Existencia previa", "Identificación de stock sin modificar su cantidad")
    return add_unit(cursor, product_id, branch, pair)


def request_count(cursor, employee, branch, product_id, quantity, reason, present, new_pairs):
    actor(cursor, employee, branch)
    require(reason.strip() and 0 <= quantity <= 1000000, "Indica una cantidad válida y el motivo del conteo.")
    p = product(cursor, product_id)
    s = stock(cursor, branch, product_id)
    units = current_units(cursor, branch, product_id)
    if p["requiere_serie"]:
        require(len(units) == s["stock_actual"], "Completa primero la identificación del stock existente en Unidades.")
        require(set(present) <= {u["id_unidad"] for u in units} and len(set(present)) == len(present), "Las unidades contadas no corresponden a esta sucursal.")
        require(quantity == len(present) + len(new_pairs), "La cantidad contada debe coincidir con las unidades presentes y nuevas.")
    else:
        require(not present and not new_pairs, "Este producto se cuenta por cantidad.")
    cursor.execute("""INSERT INTO CONTEO_INVENTARIO(id_sucursal,id_producto,stock_sistema,reservado_sistema,revision_sistema,cantidad_contada,unidades_snapshot,unidades_presentes,unidades_nuevas,motivo,id_solicitante)
                      VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", (branch, product_id, s["stock_actual"], s["stock_reservado"], s["revision"], quantity, json.dumps([(u["id_unidad"], u["estado"]) for u in units]), json.dumps(present), json.dumps(new_pairs), reason, employee))
    return cursor.lastrowid


def resolve_count(cursor, employee, count_id, approve, note):
    actor(cursor, employee, admin=True)
    cursor.execute("SELECT * FROM CONTEO_INVENTARIO WHERE id_conteo=%s FOR UPDATE", (count_id,))
    c = cursor.fetchone()
    require(c and c["estado"] == "Pendiente", "El conteo ya fue resuelto.")
    if approve:
        s = stock(cursor, c["id_sucursal"], c["id_producto"])
        require(s["revision"] == c["revision_sistema"], "El inventario cambió desde el conteo. Recházalo y realiza otro conteo físico.")
        require(c["cantidad_contada"] >= s["stock_reservado"], "El ajuste afectaría unidades reservadas; resuelve las reservas primero.")
        context(cursor, employee, "Ajuste por conteo", f"Conteo #{count_id}", c["motivo"])
        p = product(cursor, c["id_producto"])
        if p["requiere_serie"]:
            units = current_units(cursor, c["id_sucursal"], c["id_producto"])
            require(json.dumps([(u["id_unidad"], u["estado"]) for u in units]) == json.dumps(json.loads(c["unidades_snapshot"])), "La identificación de las unidades cambió; realiza otro conteo.")
            present = set(json.loads(c["unidades_presentes"]))
            for u in units:
                if u["id_unidad"] not in present:
                    require(u["estado"] == "Disponible", "Una unidad faltante está reservada; resuelve su traslado primero.")
                    cursor.execute("UPDATE UNIDAD_PRODUCTO SET estado='Baja' WHERE id_unidad=%s", (u["id_unidad"],))
            for pair in json.loads(c["unidades_nuevas"]):
                add_unit(cursor, c["id_producto"], c["id_sucursal"], pair)
        cursor.execute("UPDATE INVENTARIO_SUCURSAL SET stock_actual=%s WHERE id_sucursal=%s AND id_producto=%s", (c["cantidad_contada"], c["id_sucursal"], c["id_producto"]))
    else:
        require(note.strip(), "Escribe el motivo del rechazo.")
    cursor.execute("UPDATE CONTEO_INVENTARIO SET estado=%s,id_responsable=%s,fecha_resolucion=NOW(),observacion=%s WHERE id_conteo=%s", ("Aprobado" if approve else "Rechazado", employee, note, count_id))


def reverse_document(cursor, employee, kind, document_id, cancel, quantities, reason, selected_units):
    actor(cursor, employee, admin=True)
    require(kind in ("venta", "compra") and reason.strip(), "Escribe el motivo de la devolución o anulación.")
    table, detail_table = ("VENTA", "DETALLE_VENTA") if kind == "venta" else ("COMPRA", "DETALLE_COMPRA")
    key, detail_key = f"id_{kind}", f"id_detalle_{kind}"
    cursor.execute(f"SELECT * FROM {table} WHERE {key}=%s FOR UPDATE", (document_id,))
    doc = cursor.fetchone()
    require(doc and doc.get("estado", doc.get("estado_recepcion")) not in ("Anulada", "Cancelado"), "El documento no existe o ya fue anulado.")
    cursor.execute(f"SELECT d.*,p.requiere_serie FROM {detail_table} d JOIN PRODUCTO p USING(id_producto) WHERE {key}=%s ORDER BY d.id_producto,d.{detail_key} FOR UPDATE", (document_id,))
    details = cursor.fetchall()
    operation = ("Anulación " if cancel else "Devolución ") + kind
    cursor.execute(f"INSERT INTO REVERSO_DOCUMENTO(tipo,{key},id_empleado,motivo) VALUES(%s,%s,%s,%s)", (operation, document_id, employee, reason))
    reversal_id = cursor.lastrowid
    context(cursor, employee, operation, f"Reverso #{reversal_id}; {kind} #{document_id}", reason)
    total, changed = Decimal("0.00"), False
    for d in details:
        did = d[detail_key]
        cursor.execute(f"SELECT COALESCE(SUM(cantidad),0) n,COALESCE(SUM(importe),0) importe FROM DETALLE_REVERSO WHERE {detail_key}=%s", (did,))
        previous = cursor.fetchone()
        remaining = d["cantidad"] - previous["n"]
        quantity = int(remaining) if cancel else quantities.get(did, 0)
        require(0 <= quantity <= remaining, "La cantidad a devolver supera lo pendiente del documento.")
        if not quantity:
            continue
        changed = True
        s = stock(cursor, doc["id_sucursal"], d["id_producto"])
        if kind == "venta":
            if d["id_unidad"]:
                cursor.execute("SELECT * FROM UNIDAD_PRODUCTO WHERE id_unidad=%s FOR UPDATE", (d["id_unidad"],))
                unit = cursor.fetchone()
                require(unit["estado"] == "Vendida" and unit["id_detalle_venta"] == did, "La motocicleta ya no pertenece a esta venta.")
                cursor.execute("UPDATE UNIDAD_PRODUCTO SET estado='Disponible',id_sucursal=%s,id_detalle_venta=NULL WHERE id_unidad=%s", (doc["id_sucursal"], d["id_unidad"]))
            cursor.execute("UPDATE INVENTARIO_SUCURSAL SET stock_actual=stock_actual+%s WHERE id_sucursal=%s AND id_producto=%s", (quantity, doc["id_sucursal"], d["id_producto"]))
        else:
            require(s["stock_actual"] - s["stock_reservado"] >= quantity, "No hay stock libre suficiente para devolver al proveedor.")
            if d["requiere_serie"]:
                ids = selected_units.get(did, [])
                require(len(ids) == quantity and len(set(ids)) == len(ids), "Selecciona las unidades exactas que se devolverán al proveedor.")
                for uid in sorted(ids):
                    cursor.execute("SELECT * FROM UNIDAD_PRODUCTO WHERE id_unidad=%s FOR UPDATE", (uid,))
                    u = cursor.fetchone()
                    require(u and u["id_detalle_compra"] == did and u["id_sucursal"] == doc["id_sucursal"] and u["estado"] == "Disponible", "Solo puedes devolver unidades disponibles de esta compra y sucursal.")
                    cursor.execute("UPDATE UNIDAD_PRODUCTO SET estado='Devuelta a proveedor' WHERE id_unidad=%s", (uid,))
            cursor.execute("UPDATE INVENTARIO_SUCURSAL SET stock_actual=stock_actual-%s WHERE id_sucursal=%s AND id_producto=%s", (quantity, doc["id_sucursal"], d["id_producto"]))
        cumulative = (d["subtotal"] * (previous["n"] + quantity) / d["cantidad"]).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        amount = cumulative - previous["importe"]
        cursor.execute(f"INSERT INTO DETALLE_REVERSO(id_reverso,id_producto,{detail_key},cantidad,importe) VALUES(%s,%s,%s,%s,%s)", (reversal_id, d["id_producto"], did, quantity, amount))
        total += amount
    require(changed or cancel, "Selecciona al menos una cantidad para devolver.")
    cursor.execute("UPDATE REVERSO_DOCUMENTO SET importe=%s WHERE id_reverso=%s", (total, reversal_id))
    if cancel:
        column, state = ("estado", "Anulada") if kind == "venta" else ("estado_recepcion", "Cancelado")
        cursor.execute(f"UPDATE {table} SET {column}=%s WHERE {key}=%s", (state, document_id))
    return reversal_id


def enrich_inventory(cursor, rows, branch=None, by_branch=False):
    cursor.execute("""SELECT i.id_sucursal,i.id_producto,i.stock_actual,i.stock_reservado,
                         COALESCE(i.stock_minimo,p.stock_minimo) minimo
                      FROM INVENTARIO_SUCURSAL i JOIN PRODUCTO p USING(id_producto) JOIN SUCURSAL s USING(id_sucursal)
                      WHERE s.estado=1""")
    inventory = cursor.fetchall()
    cursor.execute("""SELECT t.id_sucursal_destino id_sucursal,d.id_producto,SUM(d.cantidad-COALESCE(d.cantidad_recibida,0)) cantidad
                      FROM TRASLADO t JOIN DETALLE_TRASLADO d USING(id_traslado)
                      WHERE t.estado IN ('En tránsito','Con diferencias') GROUP BY t.id_sucursal_destino,d.id_producto""")
    transit = cursor.fetchall()
    for row in rows:
        target = row.get("id_sucursal") if by_branch else branch
        stocks = [s for s in inventory if s["id_producto"] == row["id_producto"] and (target is None or s["id_sucursal"] == target)]
        row["reservado"] = sum(s["stock_reservado"] for s in stocks)
        row["disponible"] = row["stock_actual"] - row["reservado"]
        row["en_transito"] = sum(t["cantidad"] for t in transit if t["id_producto"] == row["id_producto"] and (target is None or t["id_sucursal"] == target))
        if target is not None and stocks:
            row["stock_minimo"] = stocks[0]["minimo"]
