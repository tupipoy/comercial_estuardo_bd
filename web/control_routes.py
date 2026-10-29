"""Pantallas de trazabilidad y control de inventario."""
import json
from datetime import datetime, timedelta
from flask import flash, redirect, render_template, request, session, url_for
from pymysql import IntegrityError
from db import get_db_connection
import inventory_control as control


def register_control_routes(app, requiere_rol, branch_for_employee):
    def choices(cursor):
        cursor.execute("SELECT id_sucursal,nombre FROM SUCURSAL WHERE estado=1 ORDER BY nombre")
        branches = cursor.fetchall()
        cursor.execute("SELECT id_producto,nombre,requiere_serie FROM PRODUCTO WHERE estado=1 ORDER BY nombre")
        return branches, cursor.fetchall()

    def branch_scope(cursor):
        if session.get("user_role") == "Administrador":
            value = request.values.get("sucursal", "")
            return int(value) if value.isdigit() else None
        return branch_for_employee(cursor) or -1

    def handle_error(connection, exc):
        connection.rollback()
        if isinstance(exc, control.InventoryError):
            flash(str(exc), "danger")
        elif isinstance(exc, (ValueError, TypeError)):
            flash("Revisa las cantidades y los campos obligatorios.", "danger")
        elif isinstance(exc, IntegrityError):
            flash("No se pudo guardar: hay un VIN o motor repetido, o un dato ya no es válido.", "danger")
        else:
            app.logger.exception("No se pudo completar la operación de inventario")
            flash("No se pudo guardar. Recarga y verifica el estado actual de la operación.", "danger")

    @app.route("/unidades", methods=["GET", "POST"])
    @requiere_rol("Administrador", "Bodega", "Vendedor")
    def unidades():
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                if request.method == "POST":
                    try:
                        pairs = control.serial_pairs(request.form.get("series", ""))
                        control.require(len(pairs) == 1, "Registra una unidad a la vez.")
                        control.register_legacy_unit(cursor, session["user_id"], int(request.form["sucursal"]), int(request.form["producto"]), pairs[0])
                        connection.commit()
                        flash("Unidad identificada; la cantidad de inventario no cambió.", "success")
                    except Exception as exc:
                        handle_error(connection, exc)
                    return redirect(url_for("unidades"))
                branches, products = choices(cursor)
                branch = branch_scope(cursor) if session.get("user_role") != "Bodega" else (int(request.args["sucursal"]) if request.args.get("sucursal", "").isdigit() else None)
                conditions, args = ["1=1"], []
                if branch is not None:
                    conditions.append("u.id_sucursal=%s")
                    args.append(branch)
                product_id = request.args.get("producto", "")
                if product_id.isdigit():
                    conditions.append("u.id_producto=%s")
                    args.append(int(product_id))
                search = request.args.get("q", "").strip()[:100]
                if search:
                    conditions.append("(u.vin_chasis LIKE %s OR u.numero_motor LIKE %s OR p.nombre LIKE %s)")
                    args.extend([f"%{search}%"] * 3)
                cursor.execute(f"""SELECT u.*,p.nombre producto,s.nombre sucursal FROM UNIDAD_PRODUCTO u
                    JOIN PRODUCTO p USING(id_producto) JOIN SUCURSAL s USING(id_sucursal)
                    WHERE {' AND '.join(conditions)} ORDER BY u.id_unidad DESC LIMIT 300""", args)
                rows = cursor.fetchall()
            return render_template("control.html", page="unidades", rows=rows, sucursales=branches, productos=products, branch=branch, product_id=product_id, search=search)
        finally:
            connection.close()

    @app.route("/unidades/<int:unit_id>")
    @requiere_rol("Administrador", "Bodega", "Vendedor")
    def historial_unidad(unit_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT u.*,p.nombre producto,s.nombre sucursal FROM UNIDAD_PRODUCTO u JOIN PRODUCTO p USING(id_producto) JOIN SUCURSAL s USING(id_sucursal) WHERE id_unidad=%s", (unit_id,))
                unit = cursor.fetchone()
                if not unit or (session.get("user_role") == "Vendedor" and unit["id_sucursal"] != branch_for_employee(cursor)):
                    return "Unidad no encontrada", 404
                cursor.execute("""SELECT h.*,o.nombre origen,d.nombre destino,CONCAT_WS(' ',e.nombres,e.apellidos) empleado
                    FROM HISTORIAL_UNIDAD h LEFT JOIN SUCURSAL o ON o.id_sucursal=h.id_sucursal_origen
                    JOIN SUCURSAL d ON d.id_sucursal=h.id_sucursal_destino LEFT JOIN EMPLEADO e USING(id_empleado)
                    WHERE id_unidad=%s ORDER BY id_historial""", (unit_id,))
                history = cursor.fetchall()
            return render_template("control.html", page="unidad", unit=unit, rows=history)
        finally:
            connection.close()

    @app.route("/kardex")
    @requiere_rol("Administrador", "Bodega", "Vendedor")
    def kardex():
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                branches, products = choices(cursor)
                branch = branch_scope(cursor)
                product_id = request.args.get("producto", "")
                conditions, args = ["1=1"], []
                if branch is not None:
                    conditions.append("m.id_sucursal=%s")
                    args.append(branch)
                if product_id.isdigit():
                    conditions.append("m.id_producto=%s")
                    args.append(int(product_id))
                since, until = request.args.get("desde", ""), request.args.get("hasta", "")
                try:
                    if since:
                        conditions.append("m.fecha>=%s")
                        args.append(datetime.strptime(since, "%Y-%m-%d"))
                    if until:
                        conditions.append("m.fecha<%s")
                        args.append(datetime.strptime(until, "%Y-%m-%d") + timedelta(days=1))
                except ValueError:
                    flash("Indica fechas válidas.", "warning")
                    return redirect(url_for("kardex"))
                try:
                    offset = max(0, int(request.args.get("pagina", "1")) - 1) * 100
                except ValueError:
                    offset = 0
                cursor.execute(f"""SELECT m.*,p.nombre producto,s.nombre sucursal,CONCAT_WS(' ',e.nombres,e.apellidos) empleado
                    FROM MOVIMIENTO_INVENTARIO m JOIN PRODUCTO p USING(id_producto) JOIN SUCURSAL s USING(id_sucursal)
                    LEFT JOIN EMPLEADO e USING(id_empleado) WHERE {' AND '.join(conditions)}
                    ORDER BY m.id_movimiento DESC LIMIT 101 OFFSET %s""", (*args, offset))
                rows = cursor.fetchall()
            return render_template("control.html", page="kardex", rows=rows[:100], next_page=len(rows)>100, pagina=offset//100+1, sucursales=branches, productos=products, branch=branch, product_id=product_id, desde=since, hasta=until)
        finally:
            connection.close()

    @app.route("/conteos", methods=["GET", "POST"])
    @requiere_rol("Administrador", "Bodega")
    def conteos():
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                branch = branch_scope(cursor)
                if request.method == "POST":
                    try:
                        action = request.form.get("accion", "crear")
                        if action in ("aprobar", "rechazar"):
                            control.resolve_count(cursor, session["user_id"], int(request.form["conteo"]), action == "aprobar", request.form.get("observacion", "").strip()[:500])
                        elif action == "minimo":
                            control.actor(cursor, session["user_id"], admin=True)
                            s = int(request.form["sucursal"])
                            p = int(request.form["producto"])
                            minimum = int(request.form["minimo"])
                            control.require(0 <= minimum <= 1000000, "El mínimo debe ser un número no negativo.")
                            control.stock(cursor, s, p)
                            cursor.execute("UPDATE INVENTARIO_SUCURSAL SET stock_minimo=%s WHERE id_sucursal=%s AND id_producto=%s", (minimum, s, p))
                        else:
                            control.request_count(cursor, session["user_id"], int(branch), int(request.form["producto"]), int(request.form["cantidad"]), request.form.get("motivo", "").strip()[:500], [int(v) for v in request.form.getlist("presentes")], control.serial_pairs(request.form.get("nuevas", "")))
                        connection.commit()
                        flash("Operación guardada correctamente.", "success")
                    except Exception as exc:
                        handle_error(connection, exc)
                    return redirect(url_for("conteos", sucursal=request.form.get("sucursal", ""), producto=request.form.get("producto", "")))
                branches, products = choices(cursor)
                product_id = request.args.get("producto", "")
                selected, units, inventory = None, [], None
                if branch and product_id.isdigit():
                    selected = control.product(cursor, int(product_id))
                    cursor.execute("SELECT * FROM INVENTARIO_SUCURSAL WHERE id_sucursal=%s AND id_producto=%s", (branch, int(product_id)))
                    inventory = cursor.fetchone() or {"stock_actual": 0, "stock_reservado": 0, "stock_minimo": None}
                    cursor.execute("SELECT * FROM UNIDAD_PRODUCTO WHERE id_sucursal=%s AND id_producto=%s AND estado IN ('Disponible','Reservada') ORDER BY vin_chasis", (branch, int(product_id)))
                    units = cursor.fetchall()
                sql = """SELECT c.*,p.nombre producto,s.nombre sucursal,CONCAT_WS(' ',e.nombres,e.apellidos) solicitante,
                    CONCAT_WS(' ',r.nombres,r.apellidos) responsable FROM CONTEO_INVENTARIO c JOIN PRODUCTO p USING(id_producto)
                    JOIN SUCURSAL s USING(id_sucursal) JOIN EMPLEADO e ON e.id_empleado=c.id_solicitante
                    LEFT JOIN EMPLEADO r ON r.id_empleado=c.id_responsable"""
                cursor.execute(sql + (" WHERE c.id_sucursal=%s" if branch else "") + " ORDER BY c.id_conteo DESC LIMIT 200", (branch,) if branch else ())
                rows = cursor.fetchall()
            return render_template("control.html", page="conteos", rows=rows, sucursales=branches, productos=products, branch=branch, product_id=product_id, selected=selected, units=units, inventory=inventory)
        finally:
            connection.close()

    @app.route("/documentos/<kind>/<int:document_id>/reversar", methods=["GET", "POST"])
    @requiere_rol("Administrador")
    def reversar_documento(kind, document_id):
        if kind not in ("venta", "compra"):
            return "Documento no encontrado", 404
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                if request.method == "POST":
                    try:
                        quantities = {int(k.removeprefix("cantidad_")): int(v or 0) for k, v in request.form.items() if k.startswith("cantidad_")}
                        unit_ids = {int(k.removeprefix("unidades_")): [int(v) for v in request.form.getlist(k)] for k in request.form if k.startswith("unidades_")}
                        control.reverse_document(cursor, session["user_id"], kind, document_id, request.form.get("accion") == "anular", quantities, request.form.get("motivo", "").strip()[:500], unit_ids)
                        connection.commit()
                        flash("Documento conservado y movimiento de reverso registrado.", "success")
                    except Exception as exc:
                        handle_error(connection, exc)
                    return redirect(url_for("reversar_documento", kind=kind, document_id=document_id))
                table, key, detail = kind.upper(), f"id_{kind}", f"id_detalle_{kind}"
                cursor.execute(f"SELECT * FROM {table} WHERE {key}=%s", (document_id,))
                doc = cursor.fetchone()
                if not doc:
                    return "Documento no encontrado", 404
                cursor.execute(f"""SELECT d.*,p.nombre producto,p.requiere_serie,
                    d.cantidad-COALESCE((SELECT SUM(r.cantidad) FROM DETALLE_REVERSO r WHERE r.{detail}=d.{detail}),0) pendiente
                    FROM DETALLE_{table} d JOIN PRODUCTO p USING(id_producto) WHERE d.{key}=%s""", (document_id,))
                rows = cursor.fetchall()
                if kind == "compra":
                    for row in rows:
                        cursor.execute("SELECT * FROM UNIDAD_PRODUCTO WHERE id_detalle_compra=%s AND id_sucursal=%s AND estado='Disponible'", (row[detail], doc["id_sucursal"]))
                        row["units"] = cursor.fetchall()
                cursor.execute(f"SELECT r.*,CONCAT_WS(' ',e.nombres,e.apellidos) empleado FROM REVERSO_DOCUMENTO r JOIN EMPLEADO e USING(id_empleado) WHERE {key}=%s ORDER BY id_reverso DESC", (document_id,))
                history = cursor.fetchall()
            return render_template("control.html", page="reverso", rows=rows, history=history, kind=kind, doc=doc, detail_key=detail)
        finally:
            connection.close()

    @app.route("/alertas")
    @requiere_rol("Administrador", "Bodega", "Vendedor")
    def alertas():
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                branch = branch_scope(cursor)
                suffix, args = (" AND s.id_sucursal=%s", (branch,)) if branch else ("", ())
                cursor.execute("""SELECT p.id_producto,p.nombre producto,s.nombre sucursal,i.stock_actual,i.stock_reservado,
                    COALESCE(i.stock_minimo,p.stock_minimo) minimo FROM PRODUCTO p CROSS JOIN SUCURSAL s
                    LEFT JOIN INVENTARIO_SUCURSAL i ON i.id_producto=p.id_producto AND i.id_sucursal=s.id_sucursal
                    WHERE p.estado=1 AND s.estado=1 AND COALESCE(i.stock_actual-i.stock_reservado,0)<=COALESCE(i.stock_minimo,p.stock_minimo)""" + suffix + " ORDER BY s.nombre,p.nombre LIMIT 200", args)
                low = cursor.fetchall()
                transfer_where, transfer_args = (" AND (t.id_sucursal_origen=%s OR t.id_sucursal_destino=%s)", (branch, branch)) if branch else ("", ())
                cursor.execute("""SELECT t.*,o.nombre origen,d.nombre destino,TIMESTAMPDIFF(HOUR,COALESCE(t.fecha_despacho,t.fecha_traslado),NOW()) horas
                    FROM TRASLADO t JOIN SUCURSAL o ON o.id_sucursal=t.id_sucursal_origen JOIN SUCURSAL d ON d.id_sucursal=t.id_sucursal_destino
                    WHERE t.estado IN ('Pendiente de aprobación','Aprobado','En tránsito','Con diferencias')""" + transfer_where + " ORDER BY t.fecha_traslado LIMIT 200", transfer_args)
                transfers = cursor.fetchall()
                cursor.execute("""SELECT p.nombre producto,s.nombre sucursal,i.stock_actual,
                    (SELECT COUNT(*) FROM UNIDAD_PRODUCTO u WHERE u.id_sucursal=i.id_sucursal AND u.id_producto=i.id_producto AND u.estado IN ('Disponible','Reservada')) identificadas
                    FROM INVENTARIO_SUCURSAL i JOIN PRODUCTO p USING(id_producto) JOIN SUCURSAL s USING(id_sucursal)
                    WHERE p.requiere_serie=1 AND p.estado=1""" + suffix, args)
                unidentified = [row for row in cursor.fetchall() if row["stock_actual"] != row["identificadas"]]
                backup = None
                pending_suppliers = 0
                if session.get("user_role") == "Administrador":
                    cursor.execute("SELECT COUNT(*) n FROM PROPUESTA_PROVEEDOR WHERE estado='Pendiente'")
                    pending_suppliers = cursor.fetchone()['n']
                    cursor.execute("SELECT * FROM RESPALDO_EJECUCION ORDER BY id_respaldo DESC LIMIT 1")
                    backup = cursor.fetchone()
                backup_stale = not backup or backup['estado'] == 'Error' or datetime.utcnow() - backup['inicio'] > timedelta(hours=36)
            return render_template("control.html", page="alertas", low=low, transfers=transfers, unidentified=unidentified, backup=backup, backup_stale=backup_stale, pending_suppliers=pending_suppliers)
        finally:
            connection.close()

    @app.route("/respaldos")
    @requiere_rol("Administrador")
    def respaldos():
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM RESPALDO_EJECUCION ORDER BY id_respaldo DESC LIMIT 30")
                rows = cursor.fetchall()
            return render_template("control.html", page="respaldos", rows=rows)
        finally:
            connection.close()
