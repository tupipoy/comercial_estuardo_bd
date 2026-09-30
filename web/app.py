import os
from decimal import Decimal, InvalidOperation
from functools import wraps

from flask import Flask, flash, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash

from db import get_db_connection
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey_comercial_estuardo")


def requiere_rol(*roles):
    roles_permitidos = {rol.strip().casefold() for rol in roles}

    def decorador(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("login"))

            rol_usuario = str(session.get("user_role", "")).strip().casefold()
            if rol_usuario not in roles_permitidos:
                return "Acceso no autorizado", 403

            return func(*args, **kwargs)

        return wrapper

    return decorador


@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        identificador = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        try:
            connection = get_db_connection()
            try:
                with connection.cursor() as cursor:
                    sql = """
                        SELECT
                            e.id_empleado,
                            e.nombres,
                            e.apellidos,
                            e.cargo,
                            e.password_hash,
                            s.nombre AS sucursal
                        FROM EMPLEADO e
                        INNER JOIN SUCURSAL s
                            ON e.id_sucursal = s.id_sucursal
                        WHERE
                            (e.correo = %s OR e.cui = %s)
                            AND e.estado = 1;
                    """
                    cursor.execute(sql, (identificador, identificador))
                    empleado = cursor.fetchone()
            finally:
                connection.close()

            if (
                empleado
                and empleado["password_hash"]
                and check_password_hash(empleado["password_hash"], password)
            ):
                session.clear()
                session["user_id"] = empleado["id_empleado"]
                session["user_name"] = (
                    f'{empleado["nombres"]} {empleado["apellidos"]}'
                )
                session["user_role"] = empleado["cargo"]
                session["user_branch"] = empleado["sucursal"]
                return redirect(url_for("inventario"))

            error = "Usuario o contraseña incorrectos."
        except Exception:
            app.logger.exception("Error al autenticar empleado")
            error = "No fue posible iniciar sesión. Inténtalo de nuevo."

    return render_template("login.html", error=error)

@app.route("/inventario")
@requiere_rol("Administrador", "Vendedor", "Bodega")
def inventario():
    solo_stock_bajo = request.args.get("stock_bajo", "0")
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            if solo_stock_bajo == "1":
                sql = """
                    SELECT p.id_producto, p.codigo_barra, p.nombre, p.precio_venta, 
                           p.stock_actual, p.stock_minimo, c.nombre AS categoria
                    FROM PRODUCTO p
                    INNER JOIN CATEGORIA c ON p.id_categoria = c.id_categoria
                    WHERE p.stock_actual <= p.stock_minimo AND p.estado = 1
                    ORDER BY p.stock_actual ASC;
                """
                cursor.execute(sql)
            else:
                sql = """
                    SELECT p.id_producto, p.codigo_barra, p.nombre, p.precio_venta, 
                           p.stock_actual, p.stock_minimo, c.nombre AS categoria
                    FROM PRODUCTO p
                    INNER JOIN CATEGORIA c ON p.id_categoria = c.id_categoria
                    WHERE p.estado = 1
                    ORDER BY c.nombre, p.nombre;
                """
                cursor.execute(sql)
            productos = cursor.fetchall()
    finally:
        connection.close()

    return render_template("inventario.html", productos=productos, solo_stock_bajo=solo_stock_bajo)


def cargar_categorias(cursor):
    cursor.execute("""
        SELECT id_categoria, nombre
        FROM CATEGORIA
        WHERE estado = 1
        ORDER BY nombre;
    """)
    return cursor.fetchall()


def validar_datos_producto(form):
    datos = {
        "codigo_barra": form.get("codigo_barra", "").strip() or None,
        "nombre": form.get("nombre", "").strip(),
        "descripcion": form.get("descripcion", "").strip() or None,
        "precio_costo": form.get("precio_costo", "").strip(),
        "precio_venta": form.get("precio_venta", "").strip(),
        "stock_actual": form.get("stock_actual", "").strip(),
        "stock_minimo": form.get("stock_minimo", "").strip(),
        "id_categoria": form.get("id_categoria", "").strip(),
    }
    errores = []

    if not datos["nombre"]:
        errores.append("El nombre del producto es obligatorio.")
    elif len(datos["nombre"]) > 150:
        errores.append("El nombre no puede exceder 150 caracteres.")

    if datos["codigo_barra"] and len(datos["codigo_barra"]) > 50:
        errores.append("El código de barras no puede exceder 50 caracteres.")

    for campo, etiqueta, permitir_cero in (
        ("precio_costo", "costo", True),
        ("precio_venta", "venta", False),
    ):
        try:
            precio = Decimal(datos[campo])
            if not precio.is_finite() or precio < 0 or (not permitir_cero and precio == 0):
                raise InvalidOperation
            if precio.as_tuple().exponent < -2:
                raise InvalidOperation
            datos[campo] = precio
        except (InvalidOperation, ValueError):
            limite = "igual o mayor que cero" if permitir_cero else "mayor que cero"
            errores.append(f"El precio de {etiqueta} debe ser un número {limite} con máximo dos decimales.")

    for campo, etiqueta in (("stock_actual", "stock actual"), ("stock_minimo", "stock mínimo")):
        try:
            valor = int(datos[campo])
            if valor < 0:
                raise ValueError
            datos[campo] = valor
        except (TypeError, ValueError):
            errores.append(f"El {etiqueta} debe ser un entero igual o mayor que cero.")

    try:
        datos["id_categoria"] = int(datos["id_categoria"])
    except (TypeError, ValueError):
        errores.append("Selecciona una categoría válida.")

    return datos, errores


@app.route("/productos")
@requiere_rol("Administrador", "Bodega")
def productos():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    p.id_producto,
                    p.codigo_barra,
                    p.nombre,
                    p.descripcion,
                    p.precio_costo,
                    p.precio_venta,
                    p.stock_actual,
                    p.stock_minimo,
                    p.id_categoria,
                    c.nombre AS categoria
                FROM PRODUCTO p
                INNER JOIN CATEGORIA c
                    ON p.id_categoria = c.id_categoria
                WHERE p.estado = 1
                ORDER BY p.nombre;
            """)
            lista_productos = cursor.fetchall()

    finally:
        connection.close()

    return render_template("productos.html", productos=lista_productos)


@app.route("/productos/nuevo", methods=["GET", "POST"])
@requiere_rol("Administrador", "Bodega")
def nuevo_producto():
    errores = []
    datos = None
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            categorias = cargar_categorias(cursor)
            if request.method == "POST":
                datos, errores = validar_datos_producto(request.form)
                if not categorias:
                    errores.append("Debes crear una categoría activa antes de registrar productos.")
                if datos["id_categoria"] not in {c["id_categoria"] for c in categorias}:
                    errores.append("La categoría seleccionada no está activa.")

                if not errores:
                    try:
                        cursor.execute("""
                            INSERT INTO PRODUCTO (
                                codigo_barra, nombre, descripcion, precio_costo, precio_venta,
                                stock_actual, stock_minimo, id_categoria, estado
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1);
                        """, (
                            datos["codigo_barra"], datos["nombre"], datos["descripcion"],
                            datos["precio_costo"], datos["precio_venta"], datos["stock_actual"],
                            datos["stock_minimo"], datos["id_categoria"],
                        ))
                        connection.commit()
                        return redirect(url_for("productos"))
                    except Exception as exc:
                        connection.rollback()
                        if getattr(exc, "args", [None])[0] == 1062:
                            errores.append("Ese código de barras ya está registrado.")
                        else:
                            raise
    finally:
        connection.close()

    return render_template(
        "producto_form.html", producto=datos, categorias=categorias,
        errores=errores, titulo="Nuevo producto",
    )


@app.route("/productos/editar/<int:id_producto>", methods=["GET", "POST"])
@requiere_rol("Administrador", "Bodega")
def editar_producto(id_producto):
    errores = []
    producto = None
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM PRODUCTO
                WHERE id_producto = %s AND estado = 1;
            """, (id_producto,))
            producto = cursor.fetchone()
            if not producto:
                return redirect(url_for("productos"))

            categorias = cargar_categorias(cursor)
            if request.method == "POST":
                datos, errores = validar_datos_producto(request.form)
                if datos["id_categoria"] not in {c["id_categoria"] for c in categorias}:
                    errores.append("La categoría seleccionada no está activa.")

                if not errores:
                    try:
                        cursor.execute("""
                            UPDATE PRODUCTO
                            SET codigo_barra = %s,
                                nombre = %s,
                                descripcion = %s,
                                precio_costo = %s,
                                precio_venta = %s,
                                stock_actual = %s,
                                stock_minimo = %s,
                                id_categoria = %s
                            WHERE id_producto = %s AND estado = 1;
                        """, (
                            datos["codigo_barra"], datos["nombre"], datos["descripcion"],
                            datos["precio_costo"], datos["precio_venta"], datos["stock_actual"],
                            datos["stock_minimo"], datos["id_categoria"], id_producto,
                        ))
                        connection.commit()
                        return redirect(url_for("productos"))
                    except Exception as exc:
                        connection.rollback()
                        if getattr(exc, "args", [None])[0] == 1062:
                            errores.append("Ese código de barras ya está registrado.")
                        else:
                            raise
                producto = {**producto, **datos}
    finally:
        connection.close()

    return render_template(
        "producto_form.html", producto=producto, categorias=categorias,
        errores=errores, titulo="Editar producto",
    )


@app.route("/productos/desactivar/<int:id_producto>", methods=["POST"])
@requiere_rol("Administrador", "Bodega")
def desactivar_producto(id_producto):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE PRODUCTO
                SET estado = 0
                WHERE id_producto = %s AND estado = 1;
            """, (id_producto,))
            connection.commit()
    finally:
        connection.close()

    return redirect(url_for("productos"))


def validar_datos_cliente(form):
    datos = {
        "nit": form.get("nit", "").strip(),
        "cui": form.get("cui", "").strip() or None,
        "nombres": form.get("nombres", "").strip(),
        "apellidos": form.get("apellidos", "").strip() or None,
        "telefono": form.get("telefono", "").strip(),
        "correo": form.get("correo", "").strip() or None,
        "direccion": form.get("direccion", "").strip(),
    }
    errores = []

    limites = {
        "nit": (15, "El NIT"),
        "cui": (13, "El CUI"),
        "nombres": (100, "Los nombres"),
        "apellidos": (100, "Los apellidos"),
        "telefono": (15, "El teléfono"),
        "correo": (100, "El correo"),
        "direccion": (200, "La dirección"),
    }
    for campo, (limite, etiqueta) in limites.items():
        valor = datos[campo]
        if valor and len(valor) > limite:
            errores.append(f"{etiqueta} no puede exceder {limite} caracteres.")

    for campo, etiqueta in (("nit", "El NIT"), ("nombres", "Los nombres"),
                            ("telefono", "El teléfono"), ("direccion", "La dirección")):
        if not datos[campo]:
            errores.append(f"{etiqueta} es obligatorio.")

    if datos["cui"] and len(datos["cui"]) != 13:
        errores.append("El CUI debe tener exactamente 13 caracteres.")
    if datos["telefono"] and len(datos["telefono"]) < 8:
        errores.append("El teléfono debe tener al menos 8 caracteres.")
    if datos["correo"] and ("@" not in datos["correo"] or datos["correo"].startswith("@") or datos["correo"].endswith("@")):
        errores.append("Ingresa un correo válido.")

    return datos, errores


@app.route("/clientes")
@requiere_rol("Administrador", "Vendedor")
def clientes():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    id_cliente, nit, cui, nombres, apellidos,
                    telefono, correo, direccion, estado
                FROM CLIENTE
                WHERE estado = 1
                ORDER BY nombres, apellidos;
            """)
            lista_clientes = cursor.fetchall()
    finally:
        connection.close()

    return render_template("clientes.html", clientes=lista_clientes)


@app.route("/clientes/nuevo", methods=["GET", "POST"])
@requiere_rol("Administrador", "Vendedor")
def nuevo_cliente():
    cliente = None
    errores = []
    if request.method == "POST":
        cliente, errores = validar_datos_cliente(request.form)
        if not errores:
            connection = get_db_connection()
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO CLIENTE (
                            nit, cui, nombres, apellidos, telefono,
                            correo, direccion, estado
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, 1);
                    """, (
                        cliente["nit"], cliente["cui"], cliente["nombres"],
                        cliente["apellidos"], cliente["telefono"],
                        cliente["correo"], cliente["direccion"],
                    ))
                    connection.commit()
                return redirect(url_for("clientes"))
            except Exception as exc:
                connection.rollback()
                if getattr(exc, "args", [None])[0] == 1062:
                    errores.append("El NIT o CUI ya está registrado.")
                else:
                    raise
            finally:
                connection.close()

    return render_template("cliente_form.html", cliente=cliente, errores=errores, titulo="Nuevo cliente")


@app.route("/clientes/editar/<int:id_cliente>", methods=["GET", "POST"])
@requiere_rol("Administrador", "Vendedor")
def editar_cliente(id_cliente):
    errores = []
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM CLIENTE
                WHERE id_cliente = %s AND estado = 1;
            """, (id_cliente,))
            cliente = cursor.fetchone()
            if not cliente:
                return redirect(url_for("clientes"))

            if request.method == "POST":
                datos, errores = validar_datos_cliente(request.form)
                if not errores:
                    try:
                        cursor.execute("""
                            UPDATE CLIENTE
                            SET nit = %s, cui = %s, nombres = %s,
                                apellidos = %s, telefono = %s,
                                correo = %s, direccion = %s
                            WHERE id_cliente = %s AND estado = 1;
                        """, (
                            datos["nit"], datos["cui"], datos["nombres"],
                            datos["apellidos"], datos["telefono"],
                            datos["correo"], datos["direccion"], id_cliente,
                        ))
                        connection.commit()
                        return redirect(url_for("clientes"))
                    except Exception as exc:
                        connection.rollback()
                        if getattr(exc, "args", [None])[0] == 1062:
                            errores.append("El NIT o CUI ya está registrado.")
                        else:
                            raise
                cliente = {**cliente, **datos}
    finally:
        connection.close()

    return render_template(
        "cliente_form.html", cliente=cliente, errores=errores, titulo="Editar cliente"
    )


@app.route("/clientes/desactivar/<int:id_cliente>", methods=["POST"])
@requiere_rol("Administrador", "Vendedor")
def desactivar_cliente(id_cliente):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE CLIENTE
                SET estado = 0
                WHERE id_cliente = %s AND estado = 1;
            """, (id_cliente,))
            connection.commit()
    finally:
        connection.close()

    return redirect(url_for("clientes"))


def cargar_opciones_venta(cursor):
    cursor.execute("""
        SELECT id_cliente, nit, nombres, apellidos
        FROM CLIENTE
        WHERE estado = 1
        ORDER BY nombres, apellidos;
    """)
    clientes_activos = cursor.fetchall()

    cursor.execute("""
        SELECT id_producto, codigo_barra, nombre, precio_venta, stock_actual
        FROM PRODUCTO
        WHERE estado = 1 AND stock_actual > 0
        ORDER BY nombre;
    """)
    productos_disponibles = cursor.fetchall()
    return clientes_activos, productos_disponibles


def faltan_triggers_venta(cursor):
    cursor.execute("""
        SELECT COUNT(*) AS cantidad
        FROM information_schema.TRIGGERS
        WHERE TRIGGER_SCHEMA = DATABASE()
          AND TRIGGER_NAME IN (
              'trg_validar_stock_venta',
              'trg_descontar_stock_venta'
          );
    """)
    return cursor.fetchone()["cantidad"] != 2


@app.route("/ventas")
@requiere_rol("Administrador", "Vendedor")
def ventas():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    v.id_venta,
                    v.serie_factura,
                    v.numero_factura,
                    v.fecha_venta,
                    v.total_venta,
                    v.tipo_pago,
                    v.estado,
                    CONCAT_WS(' ', c.nombres, c.apellidos) AS cliente,
                    CONCAT(e.nombres, ' ', e.apellidos) AS empleado,
                    s.nombre AS sucursal
                FROM VENTA AS v
                INNER JOIN CLIENTE AS c ON c.id_cliente = v.id_cliente
                INNER JOIN EMPLEADO AS e ON e.id_empleado = v.id_empleado
                INNER JOIN SUCURSAL AS s ON s.id_sucursal = v.id_sucursal
                ORDER BY v.fecha_venta DESC, v.id_venta DESC
                LIMIT 200;
            """)
            lista_ventas = cursor.fetchall()
    finally:
        connection.close()

    return render_template("ventas.html", ventas=lista_ventas)


@app.route("/ventas/nueva", methods=["GET", "POST"])
@requiere_rol("Administrador", "Vendedor")
def nueva_venta():
    errores = []
    datos = {
        "id_cliente": "",
        "id_producto": "",
        "cantidad": "1",
        "tipo_pago": "Efectivo",
    }
    lock_name = "comercial_estuardo_web_venta_numero"
    lock_acquired = False
    connection = None
    clientes_activos = []
    productos_disponibles = []
    triggers_disponibles = False

    if request.method == "POST":
        datos.update({
            "id_cliente": request.form.get("id_cliente", "").strip(),
            "id_producto": request.form.get("id_producto", "").strip(),
            "cantidad": request.form.get("cantidad", "").strip(),
            "tipo_pago": request.form.get("tipo_pago", "").strip(),
        })
        try:
            datos["id_cliente"] = int(datos["id_cliente"])
        except (TypeError, ValueError):
            errores.append("Selecciona un cliente válido.")
        try:
            datos["id_producto"] = int(datos["id_producto"])
        except (TypeError, ValueError):
            errores.append("Selecciona un producto válido.")
        try:
            datos["cantidad"] = int(datos["cantidad"])
            if datos["cantidad"] <= 0:
                raise ValueError
        except (TypeError, ValueError):
            errores.append("La cantidad debe ser un entero mayor que cero.")

        tipos_pago = {"Efectivo", "Transferencia", "Depósito Bancario"}
        if datos["tipo_pago"] not in tipos_pago:
            errores.append("Selecciona un tipo de pago válido.")

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            clientes_activos, productos_disponibles = cargar_opciones_venta(cursor)
            triggers_disponibles = not faltan_triggers_venta(cursor)

            if request.method == "POST" and not errores:
                if not triggers_disponibles:
                    errores.append(
                        "No se puede registrar la venta: instala primero los triggers "
                        "de control de inventario desde sql/triggers/01_triggers.sql."
                    )

                cliente_ids = {c["id_cliente"] for c in clientes_activos}
                producto_por_id = {p["id_producto"]: p for p in productos_disponibles}
                if datos["id_cliente"] not in cliente_ids:
                    errores.append("El cliente seleccionado no existe o está inactivo.")
                producto = producto_por_id.get(datos["id_producto"])
                if not producto:
                    errores.append("El producto seleccionado no existe, está inactivo o no tiene stock.")

                cursor.execute("""
                    SELECT id_sucursal
                    FROM EMPLEADO
                    WHERE id_empleado = %s AND estado = 1;
                """, (session["user_id"],))
                empleado = cursor.fetchone()
                if not empleado:
                    errores.append("El empleado de la sesión ya no está activo.")

                if not errores:
                    cursor.execute("SELECT GET_LOCK(%s, 10) AS adquirido", (lock_name,))
                    lock_acquired = cursor.fetchone()["adquirido"] == 1
                    if not lock_acquired:
                        errores.append("No se pudo reservar un número de factura. Inténtalo de nuevo.")
                    else:
                        serie_factura = "WEB"
                        cursor.execute("""
                            SELECT COALESCE(MAX(numero_factura), 0) + 1 AS siguiente
                            FROM VENTA
                            WHERE serie_factura = %s;
                        """, (serie_factura,))
                        numero_factura = cursor.fetchone()["siguiente"]

                        cursor.execute("""
                            CALL sp_registrar_venta(
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                            );
                        """, (
                            serie_factura,
                            numero_factura,
                            datos["tipo_pago"],
                            datos["id_cliente"],
                            session["user_id"],
                            empleado["id_sucursal"],
                            datos["id_producto"],
                            datos["cantidad"],
                            producto["precio_venta"],
                            Decimal("0.00"),
                        ))
                        while cursor.nextset():
                            pass
                        flash(
                            f"Venta WEB-{numero_factura} registrada correctamente.",
                            "success",
                        )
                        return redirect(url_for("ventas"))
    except Exception as exc:
        if connection:
            connection.rollback()
        app.logger.exception("No se pudo registrar la venta")
        mensaje_db = str(exc.args[1]) if len(getattr(exc, "args", ())) > 1 else ""
        if "Stock insuficiente" in mensaje_db:
            errores.append("Stock insuficiente para realizar la venta.")
        else:
            errores.append("No se pudo registrar la venta. Revisa los datos y la configuración de MySQL.")
    finally:
        if connection:
            try:
                if lock_acquired:
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT RELEASE_LOCK(%s)", (lock_name,))
            finally:
                connection.close()

    return render_template(
        "venta_form.html",
        clientes=clientes_activos,
        productos=productos_disponibles,
        datos=datos,
        errores=errores,
        triggers_disponibles=triggers_disponibles,
    )


def cargar_opciones_compra(cursor):
    cursor.execute("""
        SELECT id_proveedor, razon_social
        FROM PROVEEDOR
        WHERE estado = 1
        ORDER BY razon_social;
    """)
    proveedores_activos = cursor.fetchall()

    cursor.execute("""
        SELECT id_producto, codigo_barra, nombre, precio_costo, stock_actual
        FROM PRODUCTO
        WHERE estado = 1
        ORDER BY nombre;
    """)
    productos_activos = cursor.fetchall()
    return proveedores_activos, productos_activos


@app.route("/compras")
@requiere_rol("Administrador", "Bodega")
def compras():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    c.id_compra,
                    c.numero_orden,
                    c.fecha_compra,
                    c.total_compra,
                    c.estado_recepcion,
                    p.razon_social AS proveedor,
                    CONCAT(e.nombres, ' ', e.apellidos) AS empleado
                FROM COMPRA AS c
                INNER JOIN PROVEEDOR AS p ON p.id_proveedor = c.id_proveedor
                INNER JOIN EMPLEADO AS e ON e.id_empleado = c.id_empleado
                ORDER BY c.fecha_compra DESC, c.id_compra DESC
                LIMIT 200;
            """)
            lista_compras = cursor.fetchall()
    finally:
        connection.close()

    return render_template("compras.html", compras=lista_compras)


@app.route("/compras/nueva", methods=["GET", "POST"])
@requiere_rol("Administrador", "Bodega")
def nueva_compra():
    errores = []
    datos = {
        "numero_orden": "",
        "id_proveedor": "",
        "id_producto": "",
        "cantidad": "1",
        "costo_unitario": "",
    }
    proveedores = []
    productos = []
    connection = None

    if request.method == "POST":
        datos.update({
            campo: request.form.get(campo, "").strip()
            for campo in datos
        })
        if not datos["numero_orden"]:
            errores.append("El número de orden es obligatorio.")
        elif len(datos["numero_orden"]) > 30:
            errores.append("El número de orden no puede superar 30 caracteres.")

        for campo, etiqueta in (("id_proveedor", "proveedor"), ("id_producto", "producto")):
            try:
                datos[campo] = int(datos[campo])
                if datos[campo] <= 0:
                    raise ValueError
            except (TypeError, ValueError):
                errores.append(f"Selecciona un {etiqueta} válido.")

        try:
            datos["cantidad"] = int(datos["cantidad"])
            if datos["cantidad"] <= 0:
                raise ValueError
        except (TypeError, ValueError):
            errores.append("La cantidad debe ser un entero mayor que cero.")

        try:
            datos["costo_unitario"] = Decimal(datos["costo_unitario"])
            if not datos["costo_unitario"].is_finite() or datos["costo_unitario"] <= 0:
                raise InvalidOperation
        except (InvalidOperation, TypeError, ValueError):
            errores.append("El costo unitario debe ser un importe mayor que cero.")

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            proveedores, productos = cargar_opciones_compra(cursor)

            if request.method == "POST" and not errores:
                proveedor_ids = {p["id_proveedor"] for p in proveedores}
                producto_por_id = {p["id_producto"]: p for p in productos}
                if datos["id_proveedor"] not in proveedor_ids:
                    errores.append("El proveedor seleccionado no existe o está inactivo.")
                if datos["id_producto"] not in producto_por_id:
                    errores.append("El producto seleccionado no existe o está inactivo.")

                cursor.execute("""
                    SELECT id_empleado
                    FROM EMPLEADO
                    WHERE id_empleado = %s AND estado = 1;
                """, (session["user_id"],))
                empleado = cursor.fetchone()
                if not empleado:
                    errores.append("El empleado de la sesión ya no está activo.")

                if not errores:
                    cursor.callproc("sp_registrar_compra", (
                        datos["numero_orden"],
                        datos["id_proveedor"],
                        session["user_id"],
                        datos["id_producto"],
                        datos["cantidad"],
                        datos["costo_unitario"],
                    ))
                    while cursor.nextset():
                        pass
                    flash(
                        f"Compra {datos['numero_orden']} registrada correctamente; "
                        "stock y costo fueron actualizados.",
                        "success",
                    )
                    return redirect(url_for("compras"))
    except Exception as exc:
        if connection:
            connection.rollback()
        app.logger.exception("No se pudo registrar la compra")
        mensaje_db = str(exc.args[1]) if len(getattr(exc, "args", ())) > 1 else ""
        if "Duplicate entry" in mensaje_db:
            errores.append("Ese número de orden ya está registrado.")
        else:
            errores.append("No se pudo registrar la compra. Revisa los datos y la configuración de MySQL.")
    finally:
        if connection:
            connection.close()

    return render_template(
        "compra_form.html",
        proveedores=proveedores,
        productos=productos,
        datos=datos,
        errores=errores,
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=True)
