import os
import json
import hmac
import secrets
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from functools import wraps

from flask import Flask, flash, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash

from db import get_db_connection
from dotenv import load_dotenv
import inventory_control as control
from control_routes import register_control_routes

load_dotenv()

app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates",
)
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024
app.secret_key = os.getenv("SECRET_KEY") or os.getenv("FLASK_SECRET_KEY")
if not app.secret_key:
    raise RuntimeError("Configura SECRET_KEY o FLASK_SECRET_KEY en el entorno.")
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=bool(os.getenv("RAILWAY_ENVIRONMENT")),
)
# Hash de relleno para mantener un coste parecido si el usuario no existe o
# está temporalmente suspendido. El valor aleatorio no se usa para autenticar.
DUMMY_PASSWORD_HASH = generate_password_hash(secrets.token_urlsafe(32), method="pbkdf2:sha256")
INTENTOS_ANTES_DE_SUSPENDER = 5


def minutos_suspension(intentos):
    """Aumenta la espera ante fallos repetidos, con un máximo de 30 minutos."""
    if intentos <= INTENTOS_ANTES_DE_SUSPENDER:
        return 1
    if intentos == 6:
        return 5
    if intentos == 7:
        return 15
    return 30


@app.context_processor
def csrf_context():
    token = session.setdefault("csrf_token", secrets.token_urlsafe(32))
    return {"csrf_token": token}


@app.before_request
def proteger_solicitudes_post():
    if request.method == "POST":
        esperado = session.get("csrf_token", "")
        recibido = request.form.get("csrf_token", "")
        if not esperado or not hmac.compare_digest(esperado, recibido):
            return "Solicitud no válida. Recarga el formulario e inténtalo de nuevo.", 400


@app.route("/health")
def health():
    return {"status": "ok"}, 200

#Login y control de acceso por cargo
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
    """Consulta el empleado activo en MySQL y valida sus credenciales."""
    if request.method == "GET" and "user_id" in session:
        return redirect(url_for("resumen"))
    error = None
    if request.method == "POST":
        identificador = request.form.get("username", "").strip()[:100]
        password = request.form.get("password", "")

        try:
            connection = get_db_connection()
            try:
                connection.begin()
                with connection.cursor() as cursor:
                    sql = """
                        SELECT
                            e.id_empleado,
                            e.nombres,
                            e.apellidos,
                            e.cargo,
                            e.password_hash,
                            e.id_sucursal,
                            e.intentos_login_fallidos,
                            (e.bloqueado_hasta IS NOT NULL
                             AND e.bloqueado_hasta > NOW()) AS suspendido,
                            s.nombre AS sucursal
                        FROM EMPLEADO e
                        INNER JOIN SUCURSAL s
                            ON e.id_sucursal = s.id_sucursal
                        WHERE (e.correo = %s OR e.cui = %s)
                          AND e.estado = 1
                        LIMIT 1
                        FOR UPDATE;
                    """
                    cursor.execute(sql, (identificador, identificador))
                    empleado = cursor.fetchone()

                    suspendido = bool(empleado and empleado["suspendido"])
                    hash_guardado = (
                        empleado["password_hash"]
                        if empleado and empleado["password_hash"]
                        else DUMMY_PASSWORD_HASH
                    )
                    password_valida = False
                    if len(password) <= 256:
                        password_valida = check_password_hash(hash_guardado, password)

                    if empleado and not suspendido and password_valida:
                        cursor.execute("""
                            UPDATE EMPLEADO
                            SET intentos_login_fallidos = 0, bloqueado_hasta = NULL
                            WHERE id_empleado = %s
                        """, (empleado["id_empleado"],))
                    elif empleado and not suspendido:
                        nuevos_intentos = min(
                            empleado["intentos_login_fallidos"] + 1, 8
                        )
                        minutos = minutos_suspension(nuevos_intentos)
                        cursor.execute("""
                            UPDATE EMPLEADO
                            SET intentos_login_fallidos = %s,
                                bloqueado_hasta = CASE
                                    WHEN %s >= %s
                                    THEN DATE_ADD(NOW(), INTERVAL %s MINUTE)
                                    ELSE NULL
                                END
                            WHERE id_empleado = %s
                        """, (
                            nuevos_intentos,
                            nuevos_intentos,
                            INTENTOS_ANTES_DE_SUSPENDER,
                            minutos,
                            empleado["id_empleado"],
                        ))
                        app.logger.warning(
                            "Falló el inicio de sesión del empleado id=%s; intentos=%s",
                            empleado["id_empleado"], nuevos_intentos,
                        )
                    connection.commit()
            finally:
                connection.close()

            if (
                empleado
                and not suspendido
                and empleado["password_hash"]
                and password_valida
            ):
                session.clear()
                session["user_id"] = empleado["id_empleado"]
                session["user_branch_id"] = empleado["id_sucursal"]
                session["user_name"] = (
                    f'{empleado["nombres"]} {empleado["apellidos"]}'
                )
                session["user_role"] = empleado["cargo"]
                session["user_branch"] = empleado["sucursal"]
                return redirect(url_for("resumen"))

            error = "Usuario o contraseña incorrectos, o acceso temporalmente suspendido."
        except Exception:
            app.logger.exception("Error al autenticar empleado")
            error = "No fue posible iniciar sesión. Inténtalo de nuevo."

    return render_template("login.html", error=error)

#empieza el inventario
def patron_busqueda(texto):
    texto = str(texto or "").strip()[:100]
    if not texto:
        return ""
    texto = texto.replace("!", "!!").replace("%", "!%").replace("_", "!_")
    return f"%{texto}%"


def fechas_filtro_transacciones():
    desde = request.args.get("desde", "").strip()
    hasta = request.args.get("hasta", "").strip()
    try:
        fecha_desde = date.fromisoformat(desde) if desde else None
        fecha_hasta = date.fromisoformat(hasta) if hasta else None
    except ValueError:
        return desde, hasta, None, None, "Ingresa fechas válidas para filtrar."
    if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
        return desde, hasta, None, None, "La fecha inicial no puede ser posterior a la fecha final."
    return desde, hasta, fecha_desde, fecha_hasta, None


def obtener_sucursal_empleado(cursor, id_empleado=None):
    """Obtiene la sucursal asignada al empleado autenticado."""
    empleado_id = id_empleado or session.get("user_id")
    cursor.execute(
        "SELECT id_sucursal FROM EMPLEADO WHERE id_empleado = %s AND estado = 1",
        (empleado_id,),
    )
    fila = cursor.fetchone()
    return fila["id_sucursal"] if fila else None


def consulta_existencias(cursor, id_empleado=None, consolidar_admin=True):
    """Devuelve el SQL de existencias globales para Administración o de sucursal."""
    if consolidar_admin and session.get("user_role") == "Administrador":
        return (
            "SELECT i.id_producto, SUM(i.stock_actual) AS stock_actual, SUM(i.stock_reservado) AS stock_reservado, SUM(COALESCE(i.stock_minimo,p.stock_minimo)) AS stock_minimo "
            "FROM INVENTARIO_SUCURSAL AS i "
            "INNER JOIN PRODUCTO p ON p.id_producto=i.id_producto "
            "INNER JOIN SUCURSAL AS s ON s.id_sucursal = i.id_sucursal "
            "WHERE s.estado = 1 GROUP BY i.id_producto",
            (),
        )
    sucursal = obtener_sucursal_empleado(cursor, id_empleado)
    return (
        "SELECT id_producto, stock_actual, stock_reservado, stock_minimo FROM INVENTARIO_SUCURSAL "
        "WHERE id_sucursal = %s",
        (sucursal,),
    )


@app.route("/resumen")
@requiere_rol("Administrador", "Vendedor", "Bodega")
def resumen():
    """Resume inventario y actividad a partir de registros reales de MySQL."""
    try:
        periodo = int(request.args.get("dias", "30"))
    except ValueError:
        periodo = 30
    if periodo not in {7, 30, 90}:
        periodo = 30
    fecha_inicio = date.today() - timedelta(days=periodo - 1)
    fecha_fin = date.today() + timedelta(days=1)
    fecha_inicio_anterior = fecha_inicio - timedelta(days=periodo)
    connection = None
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            stock_sql, stock_params = consulta_existencias(cursor)
            id_sucursal_scope = (
                None if session.get("user_role") == "Administrador"
                else obtener_sucursal_empleado(cursor)
            )
            cursor.execute("""
                SELECT COUNT(*) AS total_productos,
                       COALESCE(SUM(COALESCE(existencias.stock_actual, 0) > 0 AND COALESCE(existencias.stock_actual, 0) <= p.stock_minimo), 0) AS stock_bajo,
                       COALESCE(SUM(COALESCE(existencias.stock_actual, 0) = 0), 0) AS agotados,
                       COALESCE(SUM(COALESCE(existencias.stock_actual, 0) > 0 AND p.precio_costo <= 0), 0) AS costos_pendientes,
                       COALESCE(SUM(COALESCE(existencias.stock_actual, 0) * p.precio_costo), 0) AS valor_inventario
                FROM PRODUCTO AS p
                LEFT JOIN (""" + stock_sql + """) AS existencias ON existencias.id_producto = p.id_producto
                WHERE p.estado = 1
            """, stock_params)
            indicadores = cursor.fetchone()

            cursor.execute("""
                SELECT
                    (SELECT COUNT(*) FROM VENTA WHERE estado='Emitida' AND fecha_venta >= %s AND fecha_venta < %s
                     AND (%s IS NULL OR id_sucursal = %s)) AS ventas_periodo,
                    (SELECT COUNT(*) FROM COMPRA WHERE estado_recepcion='Recibido' AND fecha_compra >= %s AND fecha_compra < %s
                     AND (%s IS NULL OR id_sucursal = %s)) AS compras_periodo,
                    (SELECT COUNT(*) FROM VENTA WHERE estado='Emitida' AND fecha_venta >= %s AND fecha_venta < %s
                     AND (%s IS NULL OR id_sucursal = %s)) AS ventas_periodo_anterior,
                    (SELECT COUNT(*) FROM COMPRA WHERE estado_recepcion='Recibido' AND fecha_compra >= %s AND fecha_compra < %s
                     AND (%s IS NULL OR id_sucursal = %s)) AS compras_periodo_anterior
            """, (
                fecha_inicio, fecha_fin, id_sucursal_scope, id_sucursal_scope,
                fecha_inicio, fecha_fin, id_sucursal_scope, id_sucursal_scope,
                fecha_inicio_anterior, fecha_inicio, id_sucursal_scope, id_sucursal_scope,
                fecha_inicio_anterior, fecha_inicio, id_sucursal_scope, id_sucursal_scope,
            ))
            actividad = cursor.fetchone()

            cursor.execute("""
                SELECT c.nombre,
                       COUNT(DISTINCT CASE
                           WHEN COALESCE(existencias.stock_actual, 0) > 0
                           THEN p.id_producto
                       END) AS total
                FROM CATEGORIA c
                LEFT JOIN PRODUCTO p ON p.id_categoria = c.id_categoria AND p.estado = 1
                LEFT JOIN (""" + stock_sql + """) AS existencias
                  ON existencias.id_producto = p.id_producto
                WHERE c.estado = 1
                GROUP BY c.id_categoria, c.nombre
                ORDER BY total DESC, c.nombre
                LIMIT 6
            """, stock_params)
            categorias = cursor.fetchall()

            cursor.execute("""
                SELECT p.id_producto, p.nombre, p.codigo_barra, p.stock_actual,
                       p.stock_minimo, c.nombre AS categoria
                FROM (
                    SELECT base.*, COALESCE(existencias.stock_actual, 0) AS stock_actual
                    FROM PRODUCTO AS base
                    LEFT JOIN (""" + stock_sql + """) AS existencias
                      ON existencias.id_producto = base.id_producto
                ) AS p
                INNER JOIN CATEGORIA c ON c.id_categoria = p.id_categoria
                WHERE p.estado = 1 AND p.stock_actual <= p.stock_minimo
                ORDER BY p.stock_actual ASC, p.nombre
                LIMIT 6
            """, stock_params)
            alertas = cursor.fetchall()

            cursor.execute("""
                (SELECT 'Venta' AS tipo, v.fecha_venta AS fecha,
                        CONCAT(v.serie_factura, '-', v.numero_factura) AS referencia,
                        v.total_venta-COALESCE((SELECT SUM(r.importe) FROM REVERSO_DOCUMENTO r WHERE r.id_venta=v.id_venta),0) AS total
                 FROM VENTA v WHERE v.fecha_venta >= %s AND v.fecha_venta < %s
                   AND (%s IS NULL OR v.id_sucursal = %s)
                 ORDER BY v.fecha_venta DESC LIMIT 6)
                UNION ALL
                (SELECT 'Compra' AS tipo, c.fecha_compra AS fecha,
                        c.numero_orden AS referencia, c.total_compra-COALESCE((SELECT SUM(r.importe) FROM REVERSO_DOCUMENTO r WHERE r.id_compra=c.id_compra),0) AS total
                 FROM COMPRA c WHERE c.fecha_compra >= %s AND c.fecha_compra < %s
                   AND (%s IS NULL OR c.id_sucursal = %s)
                 ORDER BY c.fecha_compra DESC LIMIT 6)
                ORDER BY fecha DESC
                LIMIT 8
            """, (
                fecha_inicio, fecha_fin,
                id_sucursal_scope, id_sucursal_scope,
                fecha_inicio, fecha_fin,
                id_sucursal_scope, id_sucursal_scope,
            ))
            recientes = cursor.fetchall()
    except Exception:
        app.logger.exception("No se pudo cargar el resumen de inventario")
        return render_template(
            "resumen.html", error_datos=True, periodo=periodo,
            fecha_inicio=fecha_inicio,
        )
    finally:
        if connection is not None:
            connection.close()

    max_categoria = max((fila["total"] for fila in categorias), default=0)
    valor_inventario = (
        indicadores["valor_inventario"]
        if indicadores["costos_pendientes"] == 0
        else None
    )
    return render_template(
        "resumen.html", periodo=periodo, indicadores=indicadores,
        actividad=actividad, total_operaciones=actividad["ventas_periodo"] + actividad["compras_periodo"],
        operaciones_anteriores=actividad["ventas_periodo_anterior"] + actividad["compras_periodo_anterior"],
        fecha_inicio=fecha_inicio, categorias=categorias,
        max_categoria=max_categoria, alertas=alertas, recientes=recientes,
        valor_inventario=valor_inventario, error_datos=False,
    )


@app.route("/inventario")
@requiere_rol("Administrador", "Vendedor", "Bodega")
def inventario():
    """Consulta existencias con búsqueda, filtros de categoría y estado."""
    rol = session.get("user_role")
    es_bodega = rol == "Bodega"
    es_admin = rol == "Administrador"
    vista_default = "local" if es_bodega else "consolidado"
    vista = request.args.get("vista", vista_default)
    vistas_validas = {"local", "general"} if es_bodega else {"consolidado", "general"}
    if not (es_bodega or es_admin) or vista not in vistas_validas:
        vista = vista_default
    vista_general = (es_bodega or es_admin) and vista == "general"
    solo_stock_bajo = "1" if request.args.get("stock_bajo") == "1" else "0"
    busqueda = request.args.get("q", "").strip()[:100]
    condiciones = ["p.estado = 1"]
    parametros = []
    estado_stock = request.args.get("estado", "todos")
    if estado_stock not in {"todos", "disponible", "bajo", "agotado"}:
        estado_stock = "todos"
    if solo_stock_bajo == "1" or estado_stock == "bajo":
        condiciones.append("p.stock_actual > 0 AND p.stock_actual <= p.stock_minimo")
        estado_stock = "bajo"
    elif estado_stock == "agotado":
        condiciones.append("p.stock_actual = 0")
    elif estado_stock == "disponible":
        condiciones.append("p.stock_actual > p.stock_minimo")
    categoria = request.args.get("categoria", "").strip()
    if categoria.isdigit():
        condiciones.append("p.id_categoria = %s")
        parametros.append(int(categoria))
    sucursal_filtro = request.args.get("sucursal", "").strip()
    if vista_general and sucursal_filtro.isdigit():
        condiciones.append("s.id_sucursal = %s")
        parametros.append(int(sucursal_filtro))
    patron = patron_busqueda(busqueda)
    if patron:
        condiciones.append("(p.nombre LIKE %s ESCAPE '!' OR p.codigo_barra LIKE %s ESCAPE '!' OR c.nombre LIKE %s ESCAPE '!')")
        parametros.extend([patron, patron, patron])
    connection = None
    sucursal_nombre = None
    sucursales = []
    pagina = 1
    paginas = 1
    total_productos = 0
    por_pagina = 50
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            if es_bodega:
                cursor.execute("""
                    SELECT s.nombre
                    FROM EMPLEADO AS e
                    INNER JOIN SUCURSAL AS s ON s.id_sucursal = e.id_sucursal
                    WHERE e.id_empleado = %s AND e.estado = 1 AND s.estado = 1
                """, (session.get("user_id"),))
                sucursal = cursor.fetchone()
                sucursal_nombre = sucursal["nombre"] if sucursal else None

            if vista_general:
                cursor.execute("SELECT id_sucursal, nombre FROM SUCURSAL WHERE estado = 1 ORDER BY nombre")
                sucursales = cursor.fetchall()
                condiciones_general = ["p.estado = 1", "s.estado = 1"]
                # Los filtros de stock se aplican por cada sucursal, no al total combinado.
                condiciones = [c for c in condiciones if c != "p.estado = 1"]
                condiciones_general.extend(condiciones)
                where_general = " AND ".join(condiciones_general)
                parametros_general = tuple(parametros)
                from_general = """
                    FROM PRODUCTO AS p
                    INNER JOIN CATEGORIA AS c ON c.id_categoria = p.id_categoria
                    CROSS JOIN SUCURSAL AS s
                    LEFT JOIN INVENTARIO_SUCURSAL AS i
                      ON i.id_sucursal = s.id_sucursal AND i.id_producto = p.id_producto
                """
                stock_general = "COALESCE(i.stock_actual, 0)"
                condiciones_general = [x.replace("p.stock_actual", "COALESCE(i.stock_actual-i.stock_reservado,0)").replace("p.stock_minimo", "COALESCE(i.stock_minimo,p.stock_minimo)") for x in condiciones_general]
                where_general = " AND ".join(condiciones_general)
                cursor.execute(f"SELECT COUNT(*) AS total {from_general} WHERE {where_general}", parametros_general)
                total_productos = cursor.fetchone()["total"]
                paginas = max(1, (total_productos + por_pagina - 1) // por_pagina)
                try:
                    pagina = max(1, int(request.args.get("pagina", "1")))
                except ValueError:
                    pagina = 1
                pagina = min(pagina, paginas)
                offset = (pagina - 1) * por_pagina
                cursor.execute(f"""
                    SELECT p.id_producto, p.codigo_barra, p.nombre, p.precio_venta,
                           {stock_general} AS stock_actual, COALESCE(i.stock_minimo,p.stock_minimo) stock_minimo,
                           p.precio_costo, p.id_categoria, c.nombre AS categoria,
                           s.nombre AS sucursal, s.id_sucursal
                    {from_general}
                    WHERE {where_general}
                    ORDER BY c.nombre, p.nombre, s.nombre
                    LIMIT %s OFFSET %s
                """, (*parametros_general, por_pagina, offset))
                productos = cursor.fetchall()
            else:
                stock_sql, stock_params = consulta_existencias(cursor)
                parametros = [*stock_params, *parametros]
                orden = "p.stock_actual ASC, p.nombre" if estado_stock in {"bajo", "agotado"} else "c.nombre, p.nombre"
                condiciones = [x.replace("p.stock_actual", "(p.stock_actual-p.stock_reservado)") for x in condiciones]
                cursor.execute(f"""
                    SELECT p.id_producto, p.codigo_barra, p.nombre, p.precio_venta,
                           p.stock_actual, p.stock_minimo, p.precio_costo,
                           p.id_categoria, c.nombre AS categoria
                    FROM (
                        SELECT base.id_producto,base.codigo_barra,base.nombre,base.precio_venta,base.precio_costo,base.id_categoria,base.estado,
                               COALESCE(existencias.stock_actual,0) stock_actual,COALESCE(existencias.stock_reservado,0) stock_reservado,
                               COALESCE(existencias.stock_minimo,base.stock_minimo) stock_minimo
                        FROM PRODUCTO AS base
                        LEFT JOIN ({stock_sql}) AS existencias
                          ON existencias.id_producto = base.id_producto
                    ) AS p
                    INNER JOIN CATEGORIA c ON p.id_categoria = c.id_categoria
                    WHERE {' AND '.join(condiciones)}
                    ORDER BY {orden};
                """, parametros)
                productos = cursor.fetchall()
            control.enrich_inventory(cursor, productos, branch=None if es_admin else (obtener_sucursal_empleado(cursor) or -1), by_branch=vista_general)
            categorias = cargar_categorias(cursor)
    except Exception:
        app.logger.exception("No se pudo cargar el inventario")
        return render_template(
            "inventario.html", productos=[], solo_stock_bajo=solo_stock_bajo,
            busqueda=busqueda, categorias=[], categoria=categoria,
            estado_stock=estado_stock, error_datos=True, vista=vista,
            vista_general=vista_general, sucursales=sucursales,
            sucursal_filtro=sucursal_filtro, sucursal_nombre=sucursal_nombre,
            pagina=pagina, paginas=paginas, total_productos=total_productos,
        )
    finally:
        if connection is not None:
            connection.close()

    return render_template("inventario.html", productos=productos,
                           solo_stock_bajo=solo_stock_bajo, busqueda=busqueda,
                           categorias=categorias, categoria=categoria,
                           estado_stock=estado_stock, vista=vista,
                           vista_general=vista_general, sucursales=sucursales,
                           sucursal_filtro=sucursal_filtro,
                           sucursal_nombre=sucursal_nombre, pagina=pagina,
                           paginas=paginas, total_productos=total_productos)


def validar_datos_categoria(form):
    nombre = form.get("nombre", "").strip()
    descripcion = form.get("descripcion", "").strip() or None
    errores = []
    if not nombre:
        errores.append("El nombre de la categoría es obligatorio.")
    elif len(nombre) > 100:
        errores.append("El nombre no puede superar 100 caracteres.")
    if descripcion and len(descripcion) > 255:
        errores.append("La descripción no puede superar 255 caracteres.")
    return {"nombre": nombre, "descripcion": descripcion}, errores


@app.route("/categorias")
@requiere_rol("Administrador")
def categorias():
    """Consulta las categorías activas y sus relaciones con productos."""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT c.id_categoria, c.nombre, c.descripcion,
                       COUNT(p.id_producto) AS productos
                FROM CATEGORIA c
                LEFT JOIN PRODUCTO p ON p.id_categoria = c.id_categoria AND p.estado = 1
                WHERE c.estado = 1
                GROUP BY c.id_categoria, c.nombre, c.descripcion
                ORDER BY c.nombre;
            """)
            lista_categorias = cursor.fetchall()
    finally:
        connection.close()
    return render_template("categorias.html", categorias=lista_categorias)


@app.route("/categorias/nueva", methods=["GET", "POST"])
@requiere_rol("Administrador")
def nueva_categoria():
    """Valida y guarda una categoría nueva en MySQL."""
    categoria = {"nombre": "", "descripcion": ""}
    errores = []
    if request.method == "POST":
        categoria, errores = validar_datos_categoria(request.form)
        if not errores:
            connection = get_db_connection()
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO CATEGORIA (nombre, descripcion, estado)
                        VALUES (%s, %s, 1);
                    """, (categoria["nombre"], categoria["descripcion"]))
                connection.commit()
                flash("Categoría creada correctamente.", "success")
                return redirect(url_for("categorias"))
            except Exception as exc:
                connection.rollback()
                app.logger.exception("No se pudo crear la categoría")
                errores.append("Ya existe una categoría con ese nombre." if getattr(exc, "args", (None,))[0] == 1062 else "No se pudo guardar la categoría.")
            finally:
                connection.close()
    return render_template("categoria_form.html", categoria=categoria, errores=errores, titulo="Nueva categoría")


@app.route("/categorias/editar/<int:id_categoria>", methods=["GET", "POST"])
@requiere_rol("Administrador")
def editar_categoria(id_categoria):
    """Consulta y actualiza una categoría existente en MySQL."""
    errores = []
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id_categoria, nombre, descripcion FROM CATEGORIA WHERE id_categoria = %s AND estado = 1", (id_categoria,))
            categoria = cursor.fetchone()
            if not categoria:
                return "Categoría no encontrada", 404
            if request.method == "POST":
                datos, errores = validar_datos_categoria(request.form)
                if not errores:
                    try:
                        cursor.execute("UPDATE CATEGORIA SET nombre = %s, descripcion = %s WHERE id_categoria = %s AND estado = 1", (datos["nombre"], datos["descripcion"], id_categoria))
                        connection.commit()
                        flash("Categoría actualizada correctamente.", "success")
                        return redirect(url_for("categorias"))
                    except Exception as exc:
                        connection.rollback()
                        app.logger.exception("No se pudo actualizar la categoría")
                        errores.append("Ya existe una categoría con ese nombre." if getattr(exc, "args", (None,))[0] == 1062 else "No se pudo guardar la categoría.")
                categoria = {**categoria, **datos}
    finally:
        connection.close()
    return render_template("categoria_form.html", categoria=categoria, errores=errores, titulo="Editar categoría")


@app.route("/categorias/desactivar/<int:id_categoria>", methods=["POST"])
@requiere_rol("Administrador")
def desactivar_categoria(id_categoria):
    """Desactiva lógicamente una categoría en MySQL."""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS total FROM PRODUCTO WHERE id_categoria = %s AND estado = 1", (id_categoria,))
            if cursor.fetchone()["total"]:
                flash("Desactiva primero los productos activos de esta categoría.", "warning")
                return redirect(url_for("categorias"))
            cursor.execute("UPDATE CATEGORIA SET estado = 0 WHERE id_categoria = %s AND estado = 1", (id_categoria,))
            connection.commit()
        flash("Categoría desactivada; los productos históricos se conservaron.", "success")
    finally:
        connection.close()
    return redirect(url_for("categorias"))


def validar_datos_sucursal(form):
    datos = {campo: form.get(campo, "").strip() for campo in ("nombre", "direccion", "telefono", "municipio")}
    errores = []
    limites = {"nombre": 100, "direccion": 200, "telefono": 15, "municipio": 100}
    for campo, limite in limites.items():
        if not datos[campo]:
            errores.append(f"El campo {campo.replace('_', ' ')} es obligatorio.")
        elif len(datos[campo]) > limite:
            errores.append(f"El campo {campo.replace('_', ' ')} no puede superar {limite} caracteres.")
    if datos["telefono"] and len(datos["telefono"]) < 8:
        errores.append("El teléfono debe tener al menos 8 caracteres.")
    return datos, errores


@app.route("/sucursales")
@requiere_rol("Administrador")
def sucursales():
    """Consulta las sucursales y el número de empleados relacionados."""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id_sucursal, nombre, direccion, telefono, municipio FROM SUCURSAL WHERE estado = 1 ORDER BY nombre")
            lista_sucursales = cursor.fetchall()
    finally:
        connection.close()
    return render_template("sucursales.html", sucursales=lista_sucursales)


@app.route("/sucursales/nueva", methods=["GET", "POST"])
@requiere_rol("Administrador")
def nueva_sucursal():
    """Valida y guarda una sucursal nueva en MySQL."""
    sucursal = {"nombre": "", "direccion": "", "telefono": "", "municipio": ""}
    errores = []
    if request.method == "POST":
        sucursal, errores = validar_datos_sucursal(request.form)
        if not errores:
            connection = get_db_connection()
            try:
                with connection.cursor() as cursor:
                    cursor.execute("INSERT INTO SUCURSAL (nombre, direccion, telefono, municipio, estado) VALUES (%s, %s, %s, %s, 1)", tuple(sucursal.values()))
                connection.commit()
                flash("Sucursal creada correctamente.", "success")
                return redirect(url_for("sucursales"))
            except Exception as exc:
                connection.rollback()
                app.logger.exception("No se pudo crear la sucursal")
                errores.append("Ya existe una sucursal con ese nombre." if getattr(exc, "args", (None,))[0] == 1062 else "No se pudo guardar la sucursal.")
            finally:
                connection.close()
    return render_template("sucursal_form.html", sucursal=sucursal, errores=errores, titulo="Nueva sucursal")


@app.route("/sucursales/editar/<int:id_sucursal>", methods=["GET", "POST"])
@requiere_rol("Administrador")
def editar_sucursal(id_sucursal):
    """Consulta y actualiza una sucursal existente en MySQL."""
    errores = []
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id_sucursal, nombre, direccion, telefono, municipio FROM SUCURSAL WHERE id_sucursal = %s AND estado = 1", (id_sucursal,))
            sucursal = cursor.fetchone()
            if not sucursal:
                return "Sucursal no encontrada", 404
            if request.method == "POST":
                datos, errores = validar_datos_sucursal(request.form)
                if not errores:
                    try:
                        cursor.execute("UPDATE SUCURSAL SET nombre = %s, direccion = %s, telefono = %s, municipio = %s WHERE id_sucursal = %s AND estado = 1", (*datos.values(), id_sucursal))
                        connection.commit()
                        flash("Sucursal actualizada correctamente.", "success")
                        return redirect(url_for("sucursales"))
                    except Exception as exc:
                        connection.rollback()
                        app.logger.exception("No se pudo actualizar la sucursal")
                        errores.append("Ya existe una sucursal con ese nombre." if getattr(exc, "args", (None,))[0] == 1062 else "No se pudo guardar la sucursal.")
                sucursal = {**sucursal, **datos}
    finally:
        connection.close()
    return render_template("sucursal_form.html", sucursal=sucursal, errores=errores, titulo="Editar sucursal")


@app.route("/sucursales/desactivar/<int:id_sucursal>", methods=["POST"])
@requiere_rol("Administrador")
def desactivar_sucursal(id_sucursal):
    """Desactiva lógicamente una sucursal en MySQL."""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS total FROM EMPLEADO WHERE id_sucursal = %s AND estado = 1", (id_sucursal,))
            if cursor.fetchone()["total"]:
                flash("Reasigna o desactiva primero los empleados activos de esta sucursal.", "warning")
                return redirect(url_for("sucursales"))
            cursor.execute("""
                SELECT COALESCE(SUM(stock_actual), 0) AS total
                FROM INVENTARIO_SUCURSAL WHERE id_sucursal = %s
            """, (id_sucursal,))
            if cursor.fetchone()["total"]:
                flash("Traslada primero todas las existencias fuera de esta sucursal.", "warning")
                return redirect(url_for("sucursales"))
            cursor.execute("UPDATE SUCURSAL SET estado = 0 WHERE id_sucursal = %s AND estado = 1", (id_sucursal,))
            connection.commit()
        flash("Sucursal desactivada; el historial asociado se conservó.", "success")
    finally:
        connection.close()
    return redirect(url_for("sucursales"))


def datos_formulario_empleado(form):
    return {
        "cui": form.get("cui", "").strip(),
        "nombres": form.get("nombres", "").strip(),
        "apellidos": form.get("apellidos", "").strip(),
        "cargo": form.get("cargo", "").strip(),
        "telefono": form.get("telefono", "").strip(),
        "correo": form.get("correo", "").strip() or None,
        "fecha_ingreso": form.get("fecha_ingreso", "").strip(),
        "id_sucursal": form.get("id_sucursal", "").strip(),
        "password": form.get("password", ""),
    }


def validar_datos_empleado(datos, requiere_password=False):
    errores = []
    limites = {"cui": 13, "nombres": 100, "apellidos": 100, "telefono": 15, "correo": 100}
    for campo, limite in limites.items():
        valor = datos[campo] or ""
        if len(valor) > limite:
            errores.append(f"{campo.replace('_', ' ').capitalize()} no puede superar {limite} caracteres.")
    for campo in ("cui", "nombres", "apellidos", "cargo", "telefono", "fecha_ingreso", "id_sucursal"):
        if not datos[campo]:
            errores.append(f"El campo {campo.replace('_', ' ')} es obligatorio.")
    if datos["cui"] and (len(datos["cui"]) != 13 or not datos["cui"].isdigit()):
        errores.append("El CUI debe tener exactamente 13 dígitos.")
    if datos["telefono"] and len(datos["telefono"]) < 8:
        errores.append("El teléfono debe tener al menos 8 caracteres.")
    if datos["cargo"] not in {"Administrador", "Vendedor", "Bodega"}:
        errores.append("Selecciona un cargo válido.")
    if datos["correo"] and ("@" not in datos["correo"] or " " in datos["correo"]):
        errores.append("Ingresa un correo válido.")
    try:
        datos["id_sucursal"] = int(datos["id_sucursal"])
        if datos["id_sucursal"] <= 0:
            raise ValueError
    except (TypeError, ValueError):
        errores.append("Selecciona una sucursal válida.")
    try:
        from datetime import date
        date.fromisoformat(datos["fecha_ingreso"])
    except ValueError:
        errores.append("Ingresa una fecha válida.")
    if requiere_password and len(datos["password"]) < 10:
        errores.append("La contraseña inicial debe tener al menos 10 caracteres.")
    elif datos["password"] and len(datos["password"]) < 10:
        errores.append("La nueva contraseña debe tener al menos 10 caracteres.")
    return errores


@app.route("/empleados")
@requiere_rol("Administrador")
def empleados():
    """Consulta empleados activos y sus sucursales en MySQL."""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT e.id_empleado, e.cui, e.nombres, e.apellidos, e.cargo,
                       e.telefono, e.correo, e.fecha_ingreso, s.nombre AS sucursal
                FROM EMPLEADO e
                INNER JOIN SUCURSAL s ON s.id_sucursal = e.id_sucursal
                WHERE e.estado = 1
                ORDER BY e.apellidos, e.nombres;
            """)
            lista_empleados = cursor.fetchall()
    finally:
        connection.close()
    return render_template("empleados.html", empleados=lista_empleados)


def cargar_sucursales_activas(cursor):
    """Consulta sucursales activas para formularios administrativos."""
    cursor.execute("SELECT id_sucursal, nombre FROM SUCURSAL WHERE estado = 1 ORDER BY nombre")
    return cursor.fetchall()


@app.route("/empleados/nuevo", methods=["GET", "POST"])
@requiere_rol("Administrador")
def nuevo_empleado():
    """Valida y crea un empleado en MySQL con contraseña cifrada."""
    from datetime import date
    empleado = {"cui": "", "nombres": "", "apellidos": "", "cargo": "Vendedor", "telefono": "", "correo": "", "fecha_ingreso": date.today().isoformat(), "id_sucursal": "", "password": ""}
    errores = []
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sucursales = cargar_sucursales_activas(cursor)
            if request.method == "POST":
                empleado = datos_formulario_empleado(request.form)
                errores = validar_datos_empleado(empleado, requiere_password=True)
                sucursal_ids = {s["id_sucursal"] for s in sucursales}
                if empleado["id_sucursal"] not in sucursal_ids:
                    errores.append("La sucursal seleccionada no está activa.")
                if not errores:
                    try:
                        cursor.execute("""
                            INSERT INTO EMPLEADO (cui, nombres, apellidos, cargo, telefono, correo, password_hash, fecha_ingreso, id_sucursal, estado)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
                        """, (empleado["cui"], empleado["nombres"], empleado["apellidos"], empleado["cargo"], empleado["telefono"], empleado["correo"], generate_password_hash(empleado["password"], method="pbkdf2:sha256"), empleado["fecha_ingreso"], empleado["id_sucursal"]))
                        connection.commit()
                        flash("Empleado creado correctamente.", "success")
                        return redirect(url_for("empleados"))
                    except Exception as exc:
                        connection.rollback()
                        app.logger.exception("No se pudo crear el empleado")
                        errores.append("El CUI o correo ya está registrado." if getattr(exc, "args", (None,))[0] == 1062 else "No se pudo guardar el empleado.")
    finally:
        connection.close()
    empleado.pop("password", None)
    return render_template("empleado_form.html", empleado=empleado, sucursales=sucursales, errores=errores, titulo="Nuevo empleado", nuevo=True)


@app.route("/empleados/editar/<int:id_empleado>", methods=["GET", "POST"])
@requiere_rol("Administrador")
def editar_empleado(id_empleado):
    """Consulta y actualiza los datos de un empleado en MySQL."""
    errores = []
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id_empleado, cui, nombres, apellidos, cargo, telefono, correo, fecha_ingreso, id_sucursal FROM EMPLEADO WHERE id_empleado = %s AND estado = 1", (id_empleado,))
            empleado = cursor.fetchone()
            if not empleado:
                return "Empleado no encontrado", 404
            sucursales = cargar_sucursales_activas(cursor)
            if request.method == "POST":
                datos = datos_formulario_empleado(request.form)
                errores = validar_datos_empleado(datos)
                if id_empleado == session.get("user_id") and datos["cargo"] != "Administrador":
                    errores.append("No puedes quitarte tu propio cargo de Administrador.")
                if datos["id_sucursal"] not in {s["id_sucursal"] for s in sucursales}:
                    errores.append("La sucursal seleccionada no está activa.")
                if not errores:
                    try:
                        if datos["password"]:
                            cursor.execute("""
                                UPDATE EMPLEADO SET cui=%s, nombres=%s, apellidos=%s, cargo=%s,
                                    telefono=%s, correo=%s, fecha_ingreso=%s, id_sucursal=%s,
                                    password_hash=%s WHERE id_empleado=%s AND estado=1
                            """, (datos["cui"], datos["nombres"], datos["apellidos"], datos["cargo"], datos["telefono"], datos["correo"], datos["fecha_ingreso"], datos["id_sucursal"], generate_password_hash(datos["password"], method="pbkdf2:sha256"), id_empleado))
                        else:
                            cursor.execute("""
                                UPDATE EMPLEADO SET cui=%s, nombres=%s, apellidos=%s, cargo=%s,
                                    telefono=%s, correo=%s, fecha_ingreso=%s, id_sucursal=%s
                                WHERE id_empleado=%s AND estado=1
                            """, (datos["cui"], datos["nombres"], datos["apellidos"], datos["cargo"], datos["telefono"], datos["correo"], datos["fecha_ingreso"], datos["id_sucursal"], id_empleado))
                        connection.commit()
                        flash("Empleado actualizado correctamente.", "success")
                        return redirect(url_for("empleados"))
                    except Exception as exc:
                        connection.rollback()
                        app.logger.exception("No se pudo actualizar el empleado")
                        errores.append("El CUI o correo ya está registrado." if getattr(exc, "args", (None,))[0] == 1062 else "No se pudo guardar el empleado.")
                empleado = {**empleado, **{k: v for k, v in datos.items() if k != "password"}}
            if hasattr(empleado.get("fecha_ingreso"), "isoformat"):
                empleado["fecha_ingreso"] = empleado["fecha_ingreso"].isoformat()
    finally:
        connection.close()
    return render_template("empleado_form.html", empleado=empleado, sucursales=sucursales, errores=errores, titulo="Editar empleado", nuevo=False)


@app.route("/empleados/desactivar/<int:id_empleado>", methods=["POST"])
@requiere_rol("Administrador")
def desactivar_empleado(id_empleado):
    """Desactiva un empleado y protege el último administrador activo."""
    if id_empleado == session.get("user_id"):
        flash("No puedes desactivar tu propia cuenta.", "warning")
        return redirect(url_for("empleados"))
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT cargo FROM EMPLEADO WHERE id_empleado = %s AND estado = 1", (id_empleado,))
            empleado = cursor.fetchone()
            if empleado and empleado["cargo"] == "Administrador":
                cursor.execute("SELECT COUNT(*) AS total FROM EMPLEADO WHERE cargo = 'Administrador' AND estado = 1")
                if cursor.fetchone()["total"] <= 1:
                    flash("No se puede desactivar el último Administrador activo.", "warning")
                    return redirect(url_for("empleados"))
            cursor.execute("UPDATE EMPLEADO SET estado = 0 WHERE id_empleado = %s AND estado = 1", (id_empleado,))
            connection.commit()
        flash("Empleado desactivado; sus registros históricos se conservaron.", "success")
    finally:
        connection.close()
    return redirect(url_for("empleados"))


def cargar_categorias(cursor):
    """Consulta categorías activas para formularios de productos."""
    cursor.execute("""
        SELECT id_categoria, nombre
        FROM CATEGORIA
        WHERE estado = 1
        ORDER BY nombre;
    """)
    return cursor.fetchall()


def validar_datos_producto(form):
    datos = {
        "requiere_serie": 1 if form.get("requiere_serie") == "1" else 0,
        "codigo_barra": form.get("codigo_barra", "").strip() or None,
        "nombre": form.get("nombre", "").strip(),
        "descripcion": form.get("descripcion", "").strip() or None,
        "precio_costo": form.get("precio_costo", "").strip(),
        "precio_venta": form.get("precio_venta", "").strip(),
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
            if (not precio.is_finite() or precio < 0 or precio > Decimal("99999999.99")
                    or (not permitir_cero and precio == 0)):
                raise InvalidOperation
            if precio.as_tuple().exponent < -2:
                raise InvalidOperation
            datos[campo] = precio
        except (InvalidOperation, ValueError):
            limite = "igual o mayor que cero" if permitir_cero else "mayor que cero"
            errores.append(f"El precio de {etiqueta} debe ser un número {limite} con máximo dos decimales.")

    if isinstance(datos["precio_costo"], Decimal) and isinstance(datos["precio_venta"], Decimal):
        if datos["precio_venta"] < datos["precio_costo"]:
            errores.append("El precio de venta no puede ser menor que el precio de costo.")

    for campo, etiqueta in (("stock_minimo", "stock mínimo"),):
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
    """Lista productos activos con filtros, orden y paginación."""
    busqueda = request.args.get("q", "").strip()[:100]
    patron = patron_busqueda(busqueda)
    categoria = request.args.get("categoria", "").strip()
    estado_stock = request.args.get("estado", "todos")
    if estado_stock not in {"todos", "disponible", "bajo", "agotado"}:
        estado_stock = "todos"
    ordenes = {
        "nombre": "p.nombre ASC",
        "stock": "p.stock_actual ASC, p.nombre ASC",
        "precio": "p.precio_venta ASC, p.nombre ASC",
    }
    orden = request.args.get("orden", "nombre")
    if orden not in ordenes:
        orden = "nombre"
    try:
        pagina = max(1, int(request.args.get("pagina", "1")))
    except ValueError:
        pagina = 1
    por_pagina = 24
    condiciones = ["p.estado = 1"]
    parametros = []
    if patron:
        condiciones.append("(p.nombre LIKE %s ESCAPE '!' OR p.codigo_barra LIKE %s ESCAPE '!' OR c.nombre LIKE %s ESCAPE '!')")
        parametros.extend([patron] * 3)
    if categoria.isdigit():
        condiciones.append("p.id_categoria = %s")
        parametros.append(int(categoria))
    if estado_stock == "disponible":
        condiciones.append("p.stock_actual > p.stock_minimo")
    elif estado_stock == "bajo":
        condiciones.append("p.stock_actual > 0 AND p.stock_actual <= p.stock_minimo")
    elif estado_stock == "agotado":
        condiciones.append("p.stock_actual = 0")
    where = " AND ".join(condiciones)
    connection = None
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            stock_sql, stock_params = consulta_existencias(cursor)
            parametros = [*stock_params, *parametros]
            categorias = cargar_categorias(cursor)
            cursor.execute(f"""
                SELECT COUNT(*) AS total
                FROM (
                    SELECT base.*, COALESCE(existencias.stock_actual, 0) AS stock_actual
                    FROM PRODUCTO AS base
                    LEFT JOIN ({stock_sql}) AS existencias
                      ON existencias.id_producto = base.id_producto
                ) AS p
                INNER JOIN CATEGORIA c ON p.id_categoria = c.id_categoria
                WHERE {where}
            """, parametros)
            total_productos = cursor.fetchone()["total"]
            paginas = max(1, (total_productos + por_pagina - 1) // por_pagina)
            pagina = min(pagina, paginas)
            offset = (pagina - 1) * por_pagina
            cursor.execute(f"""
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
                FROM (
                    SELECT base.*, COALESCE(existencias.stock_actual, 0) AS stock_actual
                    FROM PRODUCTO AS base
                    LEFT JOIN ({stock_sql}) AS existencias
                      ON existencias.id_producto = base.id_producto
                ) AS p
                INNER JOIN CATEGORIA c
                    ON p.id_categoria = c.id_categoria
                WHERE """ + where + f" ORDER BY {ordenes[orden]} LIMIT %s OFFSET %s",
                (
                    *stock_params,
                    *parametros[len(stock_params):],
                    por_pagina,
                    offset,
                ),
            )
            lista_productos = cursor.fetchall()
    except Exception:
        app.logger.exception("No se pudo cargar el catálogo de productos")
        return render_template(
            "productos.html", productos=[], busqueda=busqueda,
            categorias=[], categoria=categoria, estado_stock=estado_stock,
            orden=orden, pagina=1, paginas=1, total_productos=0,
            error_datos=True,
        )
    finally:
        if connection is not None:
            connection.close()

    return render_template(
        "productos.html", productos=lista_productos, busqueda=busqueda,
        categorias=categorias, categoria=categoria, estado_stock=estado_stock,
        orden=orden, pagina=pagina, paginas=paginas,
        total_productos=total_productos,
    )


@app.route("/productos/nuevo", methods=["GET", "POST"])
@requiere_rol("Administrador", "Bodega")
def nuevo_producto():
    """Valida y crea un producto asociado a una categoría activa."""
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
                                stock_minimo, id_categoria, requiere_serie, estado
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1);
                        """, (
                            datos["codigo_barra"], datos["nombre"], datos["descripcion"],
                            datos["precio_costo"], datos["precio_venta"],
                            datos["stock_minimo"], datos["id_categoria"], datos["requiere_serie"],
                        ))
                        id_producto = cursor.lastrowid
                        cursor.execute("""
                            INSERT INTO INVENTARIO_SUCURSAL (id_sucursal, id_producto, stock_actual)
                            SELECT id_sucursal, %s, 0 FROM SUCURSAL WHERE estado = 1
                        """, (id_producto,))
                        connection.commit()
                        flash("Producto creado correctamente.", "success")
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
    """Consulta y actualiza un producto existente en MySQL."""
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
                                stock_minimo = %s,
                                id_categoria = %s,
                                requiere_serie = %s
                            WHERE id_producto = %s AND estado = 1;
                        """, (
                            datos["codigo_barra"], datos["nombre"], datos["descripcion"],
                            datos["precio_costo"], datos["precio_venta"],
                            datos["stock_minimo"], datos["id_categoria"], datos["requiere_serie"], id_producto,
                        ))
                        connection.commit()
                        flash("Producto actualizado correctamente.", "success")
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
    """Desactiva lógicamente un producto en MySQL."""
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
    """Consulta clientes activos y aplica el filtro de búsqueda."""
    busqueda = request.args.get("q", "").strip()[:100]
    patron = patron_busqueda(busqueda)
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    id_cliente, nit, cui, nombres, apellidos,
                    telefono, correo, direccion, estado
                FROM CLIENTE
                WHERE estado = 1
                  AND (%s = '' OR nit LIKE %s ESCAPE '!'
                       OR cui LIKE %s ESCAPE '!'
                       OR nombres LIKE %s ESCAPE '!'
                       OR apellidos LIKE %s ESCAPE '!'
                       OR correo LIKE %s ESCAPE '!')
                ORDER BY nombres, apellidos;
            """, (patron, patron, patron, patron, patron, patron))
            lista_clientes = cursor.fetchall()
    finally:
        connection.close()

    return render_template("clientes.html", clientes=lista_clientes, busqueda=busqueda)


@app.route("/clientes/nuevo", methods=["GET", "POST"])
@requiere_rol("Administrador", "Vendedor")
def nuevo_cliente():
    """Valida y registra un cliente en MySQL."""
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
    """Consulta y actualiza un cliente existente en MySQL."""
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
    """Desactiva lógicamente un cliente en MySQL."""
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


def cargar_opciones_venta(cursor, id_sucursal):
    """Consulta clientes y productos elegibles para una venta."""
    cursor.execute("""
        SELECT id_cliente, nit, nombres, apellidos
        FROM CLIENTE
        WHERE estado = 1
        ORDER BY nombres, apellidos;
    """)
    clientes_activos = cursor.fetchall()

    cursor.execute("""
        SELECT p.id_producto, p.codigo_barra, p.nombre, p.precio_costo, p.precio_venta,
               i.stock_actual-i.stock_reservado AS stock_actual, c.nombre AS categoria,
               p.requiere_serie
        FROM PRODUCTO p
        INNER JOIN CATEGORIA c ON c.id_categoria = p.id_categoria
        INNER JOIN INVENTARIO_SUCURSAL i ON i.id_producto = p.id_producto
        WHERE p.estado = 1 AND i.id_sucursal = %s AND i.stock_actual-i.stock_reservado > 0 AND c.estado = 1
        ORDER BY p.nombre;
    """, (id_sucursal,))
    productos_disponibles = cursor.fetchall()
    return clientes_activos, productos_disponibles


def faltan_triggers_venta(cursor):
    """Consulta information_schema para comprobar los triggers requeridos."""
    cursor.execute("""
        SELECT COUNT(*) AS cantidad
        FROM information_schema.TRIGGERS
        WHERE TRIGGER_SCHEMA = DATABASE()
          AND TRIGGER_NAME IN (
              'trg_validar_stock_venta',
              'trg_descontar_stock_venta',
              'trg_validar_margen_venta'
          );
    """)
    return cursor.fetchone()["cantidad"] != 3

#ventas
@app.route("/ventas")
@requiere_rol("Administrador", "Vendedor")
def ventas():
    """Consulta el historial de ventas con filtros parametrizados."""
    busqueda = request.args.get("q", "").strip()[:100]
    patron = patron_busqueda(busqueda)
    desde, hasta, fecha_desde, fecha_hasta, error_fechas = fechas_filtro_transacciones()
    condiciones = []
    parametros = []
    if patron:
        condiciones.append("(v.serie_factura LIKE %s ESCAPE '!' OR CAST(v.numero_factura AS CHAR) LIKE %s ESCAPE '!' OR c.nombres LIKE %s ESCAPE '!' OR c.apellidos LIKE %s ESCAPE '!' OR e.nombres LIKE %s ESCAPE '!' OR e.apellidos LIKE %s ESCAPE '!')")
        parametros.extend([patron] * 6)
    if error_fechas:
        condiciones.append("1 = 0")
    else:
        if fecha_desde:
            condiciones.append("v.fecha_venta >= %s")
            parametros.append(fecha_desde.isoformat())
        if fecha_hasta:
            condiciones.append("v.fecha_venta < %s")
            parametros.append((fecha_hasta + timedelta(days=1)).isoformat())
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            if session.get("user_role") != "Administrador":
                condiciones.append("v.id_sucursal = %s")
                parametros.append(obtener_sucursal_empleado(cursor))
            where = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""
            cursor.execute(f"""
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
                {where}
                ORDER BY v.fecha_venta DESC, v.id_venta DESC
                LIMIT 200;
            """, parametros)
            lista_ventas = cursor.fetchall()
    finally:
        connection.close()

    return render_template("ventas.html", ventas=lista_ventas, busqueda=busqueda,
                           desde=desde, hasta=hasta, error_fechas=error_fechas)


@app.route("/ventas/<int:id_venta>")
@requiere_rol("Administrador", "Vendedor")
def detalle_venta(id_venta):
    """Consulta la cabecera y las líneas de una factura en MySQL."""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT v.id_venta, v.serie_factura, v.numero_factura, v.fecha_venta,
                       v.total_venta, v.tipo_pago, v.estado,
                       CONCAT_WS(' ', c.nombres, c.apellidos) AS cliente,
                       e.nombres AS empleado_nombres, e.apellidos AS empleado_apellidos,
                       s.id_sucursal, s.nombre AS sucursal
                FROM VENTA v
                INNER JOIN CLIENTE c ON c.id_cliente = v.id_cliente
                INNER JOIN EMPLEADO e ON e.id_empleado = v.id_empleado
                INNER JOIN SUCURSAL s ON s.id_sucursal = v.id_sucursal
                WHERE v.id_venta = %s
            """, (id_venta,))
            venta = cursor.fetchone()
            if not venta:
                return "Venta no encontrada", 404
            if (session.get("user_role") != "Administrador"
                    and venta["id_sucursal"] != obtener_sucursal_empleado(cursor)):
                return "Venta no encontrada", 404
            cursor.execute("""
                SELECT d.id_detalle_venta, p.codigo_barra, p.nombre AS producto,
                       d.vin_chasis, d.numero_motor, d.cantidad, d.precio_unitario,
                       d.descuento, d.subtotal
                FROM DETALLE_VENTA d
                INNER JOIN PRODUCTO p ON p.id_producto = d.id_producto
                WHERE d.id_venta = %s
                ORDER BY d.id_detalle_venta
            """, (id_venta,))
            detalles = cursor.fetchall()
            cursor.execute("SELECT COALESCE(SUM(importe),0) total FROM REVERSO_DOCUMENTO WHERE id_venta=%s", (id_venta,))
            reversado = cursor.fetchone()["total"]

    finally:
        connection.close()
    return render_template("venta_detalle.html", venta=venta, detalles=detalles, reversado=reversado)


@app.route("/ventas/<int:id_venta>/eliminar", methods=["POST"])
@requiere_rol("Administrador")
def eliminar_venta(id_venta):
    """Conserva el recibo y abre el formulario de anulación con motivo."""
    return redirect(url_for("reversar_documento", kind="venta", document_id=id_venta))

#ventas
@app.route("/ventas/nueva", methods=["GET", "POST"])
@requiere_rol("Administrador", "Vendedor")
def nueva_venta():
    """Valida y registra una venta mediante el procedimiento almacenado."""
    errores = []
    datos = {"id_cliente": "", "tipo_pago": "Efectivo"}
    lineas_formulario = [{"id_producto": "", "cantidad": "1", "descuento": "0.00", "vin_chasis": "", "numero_motor": ""}]
    lineas_validas = []
    lock_name = "comercial_estuardo_web_venta_numero"
    lock_acquired = False
    connection = None
    clientes_activos = []
    productos_disponibles = []
    unidades_disponibles = []
    triggers_disponibles = False

    if request.method == "POST":
        datos.update({"id_cliente": request.form.get("id_cliente", "").strip(), "tipo_pago": request.form.get("tipo_pago", "").strip()})
        try:
            datos["id_cliente"] = int(datos["id_cliente"])
        except (TypeError, ValueError):
            errores.append("Selecciona un cliente válido.")
        posted = zip(request.form.getlist("id_producto"), request.form.getlist("cantidad"), request.form.getlist("descuento"), request.form.getlist("vin_chasis"), request.form.getlist("numero_motor"))
        line_lists = [request.form.getlist(name) for name in ("id_producto", "cantidad", "descuento", "vin_chasis", "numero_motor")]
        if len({len(values) for values in line_lists}) != 1:
            errores.append("El formulario de líneas no está completo. Recarga e inténtalo de nuevo.")
        if len(line_lists[0]) > 50:
            errores.append("Una venta no puede superar 50 líneas de producto.")
        lineas_formulario = []
        for id_producto, cantidad, descuento, vin, motor in posted:
            linea = {"id_producto": id_producto.strip(), "cantidad": cantidad.strip(), "descuento": descuento.strip(), "vin_chasis": vin.strip() or None, "numero_motor": motor.strip() or None}
            if not linea["id_producto"] and not linea["cantidad"]:
                continue
            lineas_formulario.append(linea)
            try:
                id_producto_num = int(linea["id_producto"])
                cantidad_num = int(linea["cantidad"])
                descuento_num = Decimal(linea["descuento"] or "0")
                if id_producto_num <= 0 or cantidad_num <= 0 or not descuento_num.is_finite() or descuento_num < 0 or descuento_num.as_tuple().exponent < -2:
                    raise ValueError
                lineas_validas.append({"id_producto": id_producto_num, "cantidad": cantidad_num, "descuento": descuento_num, "vin_chasis": linea["vin_chasis"], "numero_motor": linea["numero_motor"]})
            except (TypeError, ValueError, InvalidOperation):
                errores.append("Revisa el producto, cantidad y descuento de cada línea de venta.")
        if not lineas_validas:
            errores.append("Agrega al menos un producto a la venta.")
        if len([l["vin_chasis"] for l in lineas_validas if l["vin_chasis"]]) != len({l["vin_chasis"] for l in lineas_validas if l["vin_chasis"]}):
            errores.append("No repitas una motocicleta en la misma venta.")
        for linea in lineas_validas:
            if bool(linea["vin_chasis"]) != bool(linea["numero_motor"]):
                errores.append("Para una motocicleta debes ingresar tanto VIN/chasis como número de motor.")
                break
            if linea["vin_chasis"] and (len(linea["vin_chasis"]) > 50 or len(linea["numero_motor"]) > 50):
                errores.append("VIN y número de motor no pueden superar 50 caracteres.")
                break

        tipos_pago = {"Efectivo", "Transferencia", "Depósito Bancario"}
        if datos["tipo_pago"] not in tipos_pago:
            errores.append("Selecciona un tipo de pago válido.")

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            id_sucursal_venta = obtener_sucursal_empleado(cursor)
            clientes_activos, productos_disponibles = cargar_opciones_venta(cursor, id_sucursal_venta)
            cursor.execute("SELECT id_unidad,id_producto,vin_chasis,numero_motor FROM UNIDAD_PRODUCTO WHERE id_sucursal=%s AND estado='Disponible' ORDER BY vin_chasis", (id_sucursal_venta,))
            unidades_disponibles = cursor.fetchall()
            triggers_disponibles = not faltan_triggers_venta(cursor)

            if request.method == "POST" and not errores:
                if not triggers_disponibles:
                    errores.append(
                        "No se puede registrar la venta: instala primero los triggers "
                        "de inventario y margen desde sql/triggers/01_triggers.sql "
                        "o aplica sql/migrations/04_enforce_product_margin.sql en una base existente."
                    )

                cliente_ids = {c["id_cliente"] for c in clientes_activos}
                producto_por_id = {p["id_producto"]: p for p in productos_disponibles}
                if datos["id_cliente"] not in cliente_ids:
                    errores.append("El cliente seleccionado no existe o está inactivo.")
                for linea in lineas_validas:
                    producto = producto_por_id.get(linea["id_producto"])
                    if not producto:
                        errores.append("Uno de los productos no existe, está inactivo o no tiene stock.")
                        break
                    linea["precio_unitario"] = str(producto["precio_venta"])
                    ingreso_linea = Decimal(producto["precio_venta"]) * linea["cantidad"] - linea["descuento"]
                    costo_linea = Decimal(producto["precio_costo"]) * linea["cantidad"]
                    if ingreso_linea < costo_linea:
                        errores.append("El precio de venta y el descuento no pueden dejar la línea por debajo de su costo.")
                        break
                    if linea["descuento"] > Decimal(producto["precio_venta"]) * linea["cantidad"]:
                        errores.append("El descuento de una línea supera el importe de esa línea.")
                        break
                    es_motocicleta = producto["requiere_serie"]
                    if es_motocicleta and (linea["cantidad"] != 1 or not linea["vin_chasis"] or not linea["numero_motor"]):
                        errores.append("Cada motocicleta requiere cantidad 1, VIN/chasis y número de motor.")
                        break
                    linea["descuento"] = str(linea["descuento"])

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
                            CALL sp_registrar_venta_detallada(%s, %s, %s, %s, %s, %s, %s);
                        """, (
                            serie_factura,
                            numero_factura,
                            datos["tipo_pago"],
                            datos["id_cliente"],
                            session["user_id"],
                            empleado["id_sucursal"],
                            json.dumps(lineas_validas),
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
        if isinstance(exc, control.InventoryError):
            errores.append(str(exc))
        elif "Stock insuficiente" in mensaje_db:
            errores.append("Stock insuficiente para realizar la venta.")
        elif getattr(exc, "args", (None,))[0] == 1644:
            errores.append(mensaje_db)
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
        lineas=lineas_formulario,
        errores=errores,
        triggers_disponibles=triggers_disponibles,
        unidades=unidades_disponibles,
    )


def cargar_opciones_compra(cursor, id_sucursal):
    """Consulta proveedores y productos activos para una compra."""
    cursor.execute("""
        SELECT id_proveedor, razon_social
        FROM PROVEEDOR
        WHERE estado = 1
        ORDER BY razon_social;
    """)
    proveedores_activos = cursor.fetchall()

    cursor.execute("""
        SELECT p.id_producto, p.codigo_barra, p.nombre, p.precio_costo, p.precio_venta,
               COALESCE(i.stock_actual, 0) AS stock_actual, p.requiere_serie
        FROM PRODUCTO p
        INNER JOIN CATEGORIA c ON c.id_categoria = p.id_categoria
        LEFT JOIN INVENTARIO_SUCURSAL i
          ON i.id_producto = p.id_producto AND i.id_sucursal = %s
        WHERE p.estado = 1 AND c.estado = 1
        ORDER BY p.nombre;
    """, (id_sucursal,))
    productos_activos = cursor.fetchall()
    return proveedores_activos, productos_activos

#compra
@app.route("/compras")
@requiere_rol("Administrador", "Bodega")
def compras():
    """Consulta el historial de compras con filtros parametrizados."""
    busqueda = request.args.get("q", "").strip()[:100]
    patron = patron_busqueda(busqueda)
    desde, hasta, fecha_desde, fecha_hasta, error_fechas = fechas_filtro_transacciones()
    condiciones = []
    parametros = []
    if patron:
        condiciones.append("(c.numero_orden LIKE %s ESCAPE '!' OR p.razon_social LIKE %s ESCAPE '!' OR p.nit LIKE %s ESCAPE '!' OR e.nombres LIKE %s ESCAPE '!' OR e.apellidos LIKE %s ESCAPE '!')")
        parametros.extend([patron] * 5)
    if error_fechas:
        condiciones.append("1 = 0")
    else:
        if fecha_desde:
            condiciones.append("c.fecha_compra >= %s")
            parametros.append(fecha_desde.isoformat())
        if fecha_hasta:
            condiciones.append("c.fecha_compra < %s")
            parametros.append((fecha_hasta + timedelta(days=1)).isoformat())
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            if session.get("user_role") != "Administrador":
                condiciones.append("c.id_sucursal = %s")
                parametros.append(obtener_sucursal_empleado(cursor))
            where = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""
            cursor.execute(f"""
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
                {where}
                ORDER BY c.fecha_compra DESC, c.id_compra DESC
                LIMIT 200;
            """, parametros)
            lista_compras = cursor.fetchall()
    finally:
        connection.close()

    return render_template("compras.html", compras=lista_compras, busqueda=busqueda,
                           desde=desde, hasta=hasta, error_fechas=error_fechas)


@app.route("/compras/<int:id_compra>")
@requiere_rol("Administrador", "Bodega")
def detalle_compra(id_compra):
    """Consulta la cabecera y las líneas de una orden en MySQL."""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT c.id_compra, c.id_sucursal, c.numero_orden, c.fecha_compra, c.total_compra,
                       c.estado_recepcion, p.razon_social AS proveedor,
                       e.nombres AS empleado_nombres, e.apellidos AS empleado_apellidos
                FROM COMPRA c
                INNER JOIN PROVEEDOR p ON p.id_proveedor = c.id_proveedor
                INNER JOIN EMPLEADO e ON e.id_empleado = c.id_empleado
                WHERE c.id_compra = %s
            """, (id_compra,))
            compra = cursor.fetchone()
            if not compra:
                return "Compra no encontrada", 404
            if (session.get("user_role") != "Administrador"
                    and compra["id_sucursal"] != obtener_sucursal_empleado(cursor)):
                return "Compra no encontrada", 404
            cursor.execute("""
                SELECT d.id_detalle_compra, p.codigo_barra, p.nombre AS producto,
                       d.cantidad, d.costo_unitario, d.subtotal
                FROM DETALLE_COMPRA d
                INNER JOIN PRODUCTO p ON p.id_producto = d.id_producto
                WHERE d.id_compra = %s
                ORDER BY d.id_detalle_compra
            """, (id_compra,))
            detalles = cursor.fetchall()
            cursor.execute("SELECT COALESCE(SUM(importe),0) total FROM REVERSO_DOCUMENTO WHERE id_compra=%s", (id_compra,))
            reversado = cursor.fetchone()["total"]
    finally:
        connection.close()
    return render_template("compra_detalle.html", compra=compra, detalles=detalles, reversado=reversado)

#compra
@app.route("/compras/nueva", methods=["GET", "POST"])
@requiere_rol("Administrador", "Bodega")
def nueva_compra():
    """Valida y registra una compra mediante el procedimiento almacenado."""
    errores = []
    datos = {
        "numero_orden": "",
        "id_proveedor": "",
    }
    lineas_formulario = [{"id_producto": "", "cantidad": "1", "costo_unitario": "", "series": ""}]
    lineas_validas = []
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

        for campo, etiqueta in (("id_proveedor", "proveedor"),):
            try:
                datos[campo] = int(datos[campo])
                if datos[campo] <= 0:
                    raise ValueError
            except (TypeError, ValueError):
                errores.append(f"Selecciona un {etiqueta} válido.")

        posted = zip(request.form.getlist("id_producto"), request.form.getlist("cantidad"), request.form.getlist("costo_unitario"), request.form.getlist("series"))
        line_lists = [request.form.getlist(name) for name in ("id_producto", "cantidad", "costo_unitario", "series")]
        if len({len(values) for values in line_lists}) != 1:
            errores.append("El formulario de líneas no está completo. Recarga e inténtalo de nuevo.")
        if len(line_lists[0]) > 50:
            errores.append("Una compra no puede superar 50 líneas de producto.")
        lineas_formulario = []
        for id_producto, cantidad, costo, series in posted:
            linea = {"id_producto": id_producto.strip(), "cantidad": cantidad.strip(), "costo_unitario": costo.strip(), "series": series}
            if not linea["id_producto"] and not linea["cantidad"] and not linea["costo_unitario"]:
                continue
            lineas_formulario.append(linea)
            try:
                id_producto_num = int(linea["id_producto"])
                cantidad_num = int(linea["cantidad"])
                costo_num = Decimal(linea["costo_unitario"])
                if id_producto_num <= 0 or cantidad_num <= 0 or not costo_num.is_finite() or costo_num <= 0 or costo_num.as_tuple().exponent < -2:
                    raise ValueError
                lineas_validas.append({"id_producto": id_producto_num, "cantidad": cantidad_num, "costo_unitario": str(costo_num), "series": series})
            except (InvalidOperation, TypeError, ValueError):
                errores.append("Revisa el producto, cantidad y costo unitario de cada línea de compra.")
        if not lineas_validas:
            errores.append("Agrega al menos un producto a la compra.")
        if len(lineas_validas) != len({linea["id_producto"] for linea in lineas_validas}):
            errores.append("Cada producto debe aparecer una sola vez; ajusta la cantidad en su línea.")

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            id_sucursal_compra = obtener_sucursal_empleado(cursor)
            proveedores, productos = cargar_opciones_compra(cursor, id_sucursal_compra)

            if request.method == "POST" and not errores:
                proveedor_ids = {p["id_proveedor"] for p in proveedores}
                producto_por_id = {p["id_producto"]: p for p in productos}
                if datos["id_proveedor"] not in proveedor_ids:
                    errores.append("El proveedor seleccionado no existe o está inactivo.")
                if any(linea["id_producto"] not in producto_por_id for linea in lineas_validas):
                    errores.append("Uno de los productos no existe o está inactivo.")
                for linea in lineas_validas:
                    producto = producto_por_id.get(linea["id_producto"])
                    if producto and Decimal(linea["costo_unitario"]) > Decimal(producto["precio_venta"]):
                        errores.append(
                            f"El costo de compra de {producto['nombre']} supera su precio de venta. "
                            "Actualiza el precio de venta antes de registrar esta compra."
                        )
                        break

                cursor.execute("""
                    SELECT id_empleado
                    FROM EMPLEADO
                    WHERE id_empleado = %s AND estado = 1;
                """, (session["user_id"],))
                empleado = cursor.fetchone()
                if not empleado:
                    errores.append("El empleado de la sesión ya no está activo.")

                if not errores:
                    control.register_purchase(cursor, session["user_id"], id_sucursal_compra,
                                              datos["numero_orden"], datos["id_proveedor"], lineas_validas)
                    connection.commit()
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
        if isinstance(exc, control.InventoryError):
            errores.append(str(exc))
        elif "Duplicate entry" in mensaje_db:
            errores.append("Ese número de orden, VIN o motor ya está registrado.")
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
        lineas=lineas_formulario,
        errores=errores,
    )


@app.route("/traslados")
@requiere_rol("Administrador", "Bodega")
def traslados():
    """Lista movimientos entre sucursales, limitados a las sucursales del empleado."""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT t.id_traslado, t.numero_traslado, t.fecha_traslado, t.estado,
                       origen.nombre AS sucursal_origen,
                       destino.nombre AS sucursal_destino,
                       CONCAT(e.nombres, ' ', e.apellidos) AS empleado
                FROM TRASLADO AS t
                INNER JOIN SUCURSAL AS origen ON origen.id_sucursal = t.id_sucursal_origen
                INNER JOIN SUCURSAL AS destino ON destino.id_sucursal = t.id_sucursal_destino
                INNER JOIN EMPLEADO AS e ON e.id_empleado = t.id_empleado
            """
            parametros = ()
            if session.get("user_role") != "Administrador":
                id_sucursal = obtener_sucursal_empleado(cursor)
                sql += " WHERE t.id_sucursal_origen = %s OR t.id_sucursal_destino = %s"
                parametros = (id_sucursal, id_sucursal)
            sql += " ORDER BY t.fecha_traslado DESC, t.id_traslado DESC LIMIT 200"
            cursor.execute(sql, parametros)
            lista = cursor.fetchall()
            detalles_por_traslado = {traslado["id_traslado"]: [] for traslado in lista}
            if detalles_por_traslado:
                ids_traslados = tuple(detalles_por_traslado)
                placeholders = ", ".join(["%s"] * len(ids_traslados))
                cursor.execute(f"""
                    SELECT d.id_traslado, p.nombre AS producto, d.cantidad
                    FROM DETALLE_TRASLADO AS d
                    INNER JOIN PRODUCTO AS p ON p.id_producto = d.id_producto
                    WHERE d.id_traslado IN ({placeholders})
                    ORDER BY d.id_traslado, p.nombre
                """, ids_traslados)
                for detalle in cursor.fetchall():
                    detalles_por_traslado[detalle["id_traslado"]].append(detalle)
            for traslado in lista:
                traslado["detalles"] = detalles_por_traslado[traslado["id_traslado"]]
    finally:
        connection.close()
    return render_template("traslados.html", traslados=lista)


@app.route("/traslados/<int:id_traslado>", methods=["GET", "POST"])
@requiere_rol("Administrador", "Bodega")
def detalle_traslado(id_traslado):
    """Muestra el traslado y procesa su aprobacion, despacho o recepcion."""
    if request.method == "POST":
        accion = request.form.get("accion", "")
        connection = None
        try:
            connection = get_db_connection()
            with connection.cursor() as cursor:
                recibidas = None
                if accion == "recibir":
                    ids = request.form.getlist("id_producto")
                    cantidades = request.form.getlist("cantidad_recibida")
                    control.require(ids and len(ids) == len(cantidades) and len(ids) <= 50,
                                    "Completa todas las cantidades recibidas.")
                    recibidas = [{"id_producto": int(pid), "cantidad": int(qty),
                                  "unidades": [int(v) for v in request.form.getlist(f"unidades_{pid}")]}
                                 for pid, qty in zip(ids, cantidades)]
                control.transfer_action(cursor, session["user_id"], id_traslado, accion,
                                        request.form.get("observacion_recepcion" if accion == "recibir" else "observacion", "").strip()[:500], recibidas)
            connection.commit()
            flash("El traslado se actualizó correctamente.", "success")
        except Exception as exc:
            if connection:
                connection.rollback()
            app.logger.exception("No se pudo actualizar el traslado")
            flash(str(exc) if isinstance(exc, (control.InventoryError, ValueError)) else "No se pudo actualizar el traslado. Recarga y verifica su estado.", "danger")
        finally:
            if connection:
                connection.close()
        return redirect(url_for("detalle_traslado", id_traslado=id_traslado))

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT t.id_traslado, t.numero_traslado, t.fecha_traslado, t.estado,
                       t.id_sucursal_origen, t.id_sucursal_destino,
                       origen.nombre AS sucursal_origen, destino.nombre AS sucursal_destino,
                       CONCAT(e.nombres, ' ', e.apellidos) AS empleado,
                       t.fecha_aprobacion, t.observacion_resolucion, t.fecha_despacho,
                       t.fecha_recepcion, t.observacion_recepcion,
                       CONCAT(ap.nombres, ' ', ap.apellidos) AS aprobador,
                       CONCAT(de.nombres, ' ', de.apellidos) AS despachador,
                       CONCAT(re.nombres, ' ', re.apellidos) AS receptor
                FROM TRASLADO AS t
                INNER JOIN SUCURSAL AS origen ON origen.id_sucursal = t.id_sucursal_origen
                INNER JOIN SUCURSAL AS destino ON destino.id_sucursal = t.id_sucursal_destino
                INNER JOIN EMPLEADO AS e ON e.id_empleado = t.id_empleado
                LEFT JOIN EMPLEADO AS ap ON ap.id_empleado = t.id_empleado_aprobacion
                LEFT JOIN EMPLEADO AS de ON de.id_empleado = t.id_empleado_despacho
                LEFT JOIN EMPLEADO AS re ON re.id_empleado = t.id_empleado_recepcion
                WHERE t.id_traslado = %s
            """, (id_traslado,))
            traslado = cursor.fetchone()
            if not traslado:
                return "Traslado no encontrado", 404
            if session.get("user_role") != "Administrador":
                id_sucursal = obtener_sucursal_empleado(cursor)
                if id_sucursal not in (traslado["id_sucursal_origen"], traslado["id_sucursal_destino"]):
                    return "Traslado no encontrado", 404
            cursor.execute("""
                SELECT p.id_producto, p.nombre AS producto, p.codigo_barra, d.cantidad,
                       d.cantidad_recibida
                FROM DETALLE_TRASLADO AS d
                INNER JOIN PRODUCTO AS p ON p.id_producto = d.id_producto
                WHERE d.id_traslado = %s ORDER BY p.nombre
            """, (id_traslado,))
            detalles = cursor.fetchall()
            for d in detalles:
                cursor.execute("SELECT u.*,tu.recibida FROM TRASLADO_UNIDAD tu JOIN UNIDAD_PRODUCTO u USING(id_unidad) WHERE tu.id_traslado=%s AND u.id_producto=%s ORDER BY u.vin_chasis", (id_traslado, d["id_producto"]))
                d["unidades"] = cursor.fetchall()
            cursor.execute("SELECT ev.*,CONCAT_WS(' ',e.nombres,e.apellidos) empleado FROM EVENTO_TRASLADO ev JOIN EMPLEADO e USING(id_empleado) WHERE id_traslado=%s ORDER BY id_evento", (id_traslado,))
            eventos = cursor.fetchall()
    finally:
        connection.close()
    id_sucursal_usuario = None
    if session.get("user_role") != "Administrador":
        id_sucursal_usuario = traslado["id_sucursal_origen"] if id_sucursal == traslado["id_sucursal_origen"] else traslado["id_sucursal_destino"]
    return render_template("traslado_detalle.html", traslado=traslado, detalles=detalles,
                           id_sucursal_usuario=id_sucursal_usuario, eventos=eventos)


@app.route("/traslados/nuevo", methods=["GET", "POST"])
@requiere_rol("Administrador", "Bodega")
def nuevo_traslado():
    """Transfiere existencias desde la sucursal asignada a la elegida."""
    errores = []
    datos = {"id_sucursal_origen": "", "id_sucursal_destino": ""}
    lineas = [{"id_producto": "", "cantidad": "1"}]
    sucursales = []
    productos = []
    unidades = []
    connection = None

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            id_sucursal_empleado = obtener_sucursal_empleado(cursor)
            cursor.execute("SELECT id_sucursal, nombre FROM SUCURSAL WHERE estado = 1 ORDER BY nombre")
            sucursales = cursor.fetchall()
            if session.get("user_role") == "Administrador":
                datos["id_sucursal_origen"] = request.form.get(
                    "id_sucursal_origen",
                    request.args.get(
                        "origen",
                        str(sucursales[0]["id_sucursal"]) if sucursales else "",
                    ),
                ).strip()
            else:
                datos["id_sucursal_origen"] = str(id_sucursal_empleado)
            datos["id_sucursal_destino"] = request.form.get(
                "id_sucursal_destino", ""
            ).strip()

            try:
                origen = int(datos["id_sucursal_origen"])
            except (TypeError, ValueError):
                origen = id_sucursal_empleado
                errores.append("Selecciona una sucursal de origen válida.")
            try:
                destino = int(datos["id_sucursal_destino"])
            except (TypeError, ValueError):
                destino = None
                if request.method == "POST":
                    errores.append("Selecciona una sucursal de destino válida.")

            sucursal_ids = {s["id_sucursal"] for s in sucursales}
            if origen not in sucursal_ids:
                errores.append("La sucursal de origen no está activa.")
            if destino is not None and destino not in sucursal_ids:
                errores.append("La sucursal de destino no está activa.")
            if session.get("user_role") != "Administrador" and origen != id_sucursal_empleado:
                errores.append("Solo puedes trasladar productos desde tu sucursal asignada.")
            if destino == origen:
                errores.append("El origen y destino deben ser sucursales distintas.")

            cursor.execute("""
                SELECT p.id_producto, p.nombre, p.codigo_barra, i.stock_actual-i.stock_reservado AS stock_actual
                FROM PRODUCTO AS p
                INNER JOIN INVENTARIO_SUCURSAL AS i ON i.id_producto = p.id_producto
                WHERE p.estado = 1 AND i.id_sucursal = %s AND i.stock_actual-i.stock_reservado > 0
                ORDER BY p.nombre
            """, (origen,))
            productos = cursor.fetchall()

            cursor.execute("SELECT id_unidad,id_producto,vin_chasis,numero_motor FROM UNIDAD_PRODUCTO WHERE id_sucursal=%s AND estado='Disponible' ORDER BY vin_chasis", (origen,))
            unidades = cursor.fetchall()

            if request.method == "POST":
                producto_ids = request.form.getlist("id_producto")
                cantidades = request.form.getlist("cantidad")
                if len(producto_ids) != len(cantidades) or len(producto_ids) > 50:
                    errores.append("Las líneas del traslado no son válidas.")
                lineas = []
                lineas_validas = []
                inventario = {p["id_producto"]: p for p in productos}
                for id_producto, cantidad in zip(producto_ids, cantidades):
                    lineas.append({"id_producto": id_producto, "cantidad": cantidad})
                    try:
                        id_num = int(id_producto)
                        cantidad_num = int(cantidad)
                        producto = inventario.get(id_num)
                        if (not producto or cantidad_num <= 0
                                or cantidad_num > producto["stock_actual"]):
                            raise ValueError
                        lineas_validas.append({"id_producto": id_num, "cantidad": cantidad_num,
                                              "unidades": [int(v) for v in request.form.getlist(f"unidades_{id_num}")]})
                    except (TypeError, ValueError):
                        errores.append("Revisa que cada producto tenga existencias suficientes y cantidad válida.")
                        break
                if not lineas_validas:
                    errores.append("Agrega al menos un producto al traslado.")
                if len(lineas_validas) != len({l["id_producto"] for l in lineas_validas}):
                    errores.append("Cada producto debe aparecer una sola vez en el traslado.")

                if not errores:
                    numero = f"TR-{date.today():%Y%m%d}-{secrets.token_hex(3).upper()}"
                    control.request_transfer(cursor, session["user_id"], origen, destino, numero, lineas_validas)
                    connection.commit()
                    flash(f"Solicitud de traslado {numero} enviada al administrador para aprobación.", "success")
                    return redirect(url_for("traslados"))
    except Exception as exc:
        if connection:
            connection.rollback()
        app.logger.exception("No se pudo registrar el traslado")
        errores.append(str(exc) if isinstance(exc, control.InventoryError) else "No se pudo registrar el traslado. Verifica las existencias e inténtalo de nuevo.")
    finally:
        if connection:
            connection.close()

    destinos = [s for s in sucursales if str(s["id_sucursal"]) != str(datos["id_sucursal_origen"])]
    return render_template(
        "traslado_form.html", datos=datos, lineas=lineas,
        sucursales=sucursales, destinos=destinos, productos=productos,
        errores=errores, unidades=unidades,
    )


def datos_formulario_proveedor(formulario):
    return {
        "nit": formulario.get("nit", "").strip(),
        "razon_social": formulario.get("razon_social", "").strip(),
        "contacto": formulario.get("contacto", "").strip(),
        "telefono": formulario.get("telefono", "").strip(),
        "correo": formulario.get("correo", "").strip(),
        "direccion": formulario.get("direccion", "").strip(),
    }


def validar_datos_proveedor(datos):
    errores = []
    for campo, etiqueta, maximo in (
        ("nit", "NIT", 15),
        ("razon_social", "La razón social", 150),
        ("contacto", "El contacto", 100),
        ("telefono", "El teléfono", 15),
        ("correo", "El correo", 100),
        ("direccion", "La dirección", 200),
    ):
        if len(datos[campo]) > maximo:
            errores.append(f"{etiqueta} no puede superar {maximo} caracteres.")

    for campo, etiqueta in (("nit", "El NIT"), ("razon_social", "La razón social"), ("telefono", "El teléfono")):
        if not datos[campo]:
            errores.append(f"{etiqueta} es obligatorio.")

    if datos["correo"] and ("@" not in datos["correo"] or " " in datos["correo"]):
        errores.append("Ingresa un correo válido.")
    return errores


@app.route("/proveedores")
@requiere_rol("Administrador", "Bodega")
def proveedores():
    """Consulta proveedores activos y aplica el filtro de búsqueda."""
    busqueda = request.args.get("q", "").strip()[:100]
    patron = patron_busqueda(busqueda)
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    id_proveedor,
                    nit,
                    razon_social,
                    contacto,
                    telefono,
                    correo,
                    direccion
                FROM PROVEEDOR
                WHERE estado = 1
                  AND (%s = '' OR nit LIKE %s ESCAPE '!'
                       OR razon_social LIKE %s ESCAPE '!'
                       OR contacto LIKE %s ESCAPE '!'
                       OR telefono LIKE %s ESCAPE '!'
                       OR correo LIKE %s ESCAPE '!')
                ORDER BY razon_social;
            """, (patron, patron, patron, patron, patron, patron))
            lista_proveedores = cursor.fetchall()
    finally:
        connection.close()

    return render_template("proveedores.html", proveedores=lista_proveedores, busqueda=busqueda)


@app.route("/proveedores/nuevo", methods=["GET", "POST"])
@requiere_rol("Administrador", "Bodega")
def nuevo_proveedor():
    """Valida y registra un proveedor en MySQL."""
    proveedor = {"nit": "", "razon_social": "", "contacto": "", "telefono": "", "correo": "", "direccion": ""}
    errores = []

    if request.method == "POST":
        proveedor = datos_formulario_proveedor(request.form)
        errores = validar_datos_proveedor(proveedor)
        if not errores:
            connection = get_db_connection()
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO PROVEEDOR (
                            nit, razon_social, contacto, telefono, correo, direccion, estado
                        ) VALUES (%s, %s, %s, %s, %s, %s, 1);
                    """, (
                        proveedor["nit"],
                        proveedor["razon_social"],
                        proveedor["contacto"] or None,
                        proveedor["telefono"],
                        proveedor["correo"] or None,
                        proveedor["direccion"] or None,
                    ))
                connection.commit()
                flash("Proveedor creado correctamente.", "success")
                return redirect(url_for("proveedores"))
            except Exception as exc:
                connection.rollback()
                app.logger.exception("No se pudo crear el proveedor")
                if getattr(exc, "args", (None,))[0] == 1062:
                    errores.append("Ya existe un proveedor con ese NIT.")
                else:
                    errores.append("No se pudo guardar el proveedor. Revisa los datos.")
            finally:
                connection.close()

    return render_template("proveedor_form.html", proveedor=proveedor, errores=errores)


@app.route("/proveedores/editar/<int:id_proveedor>", methods=["GET", "POST"])
@requiere_rol("Administrador", "Bodega")
def editar_proveedor(id_proveedor):
    """Consulta y actualiza un proveedor existente en MySQL."""
    errores = []
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id_proveedor, nit, razon_social, contacto, telefono, correo, direccion
                FROM PROVEEDOR
                WHERE id_proveedor = %s AND estado = 1;
            """, (id_proveedor,))
            proveedor = cursor.fetchone()
            if not proveedor:
                return "Proveedor no encontrado", 404

            if request.method == "POST":
                datos = datos_formulario_proveedor(request.form)
                errores = validar_datos_proveedor(datos)
                if not errores:
                    try:
                        cursor.execute("""
                            UPDATE PROVEEDOR
                            SET nit = %s,
                                razon_social = %s,
                                contacto = %s,
                                telefono = %s,
                                correo = %s,
                                direccion = %s
                            WHERE id_proveedor = %s AND estado = 1;
                        """, (
                            datos["nit"],
                            datos["razon_social"],
                            datos["contacto"] or None,
                            datos["telefono"],
                            datos["correo"] or None,
                            datos["direccion"] or None,
                            id_proveedor,
                        ))
                        connection.commit()
                        flash("Proveedor actualizado correctamente.", "success")
                        return redirect(url_for("proveedores"))
                    except Exception as exc:
                        connection.rollback()
                        app.logger.exception("No se pudo actualizar el proveedor")
                        if getattr(exc, "args", (None,))[0] == 1062:
                            errores.append("Ya existe un proveedor con ese NIT.")
                        else:
                            errores.append("No se pudo guardar el proveedor. Revisa los datos.")
                proveedor = {**proveedor, **datos}
    finally:
        connection.close()

    return render_template("proveedor_form.html", proveedor=proveedor, errores=errores)


@app.route("/proveedores/desactivar/<int:id_proveedor>", methods=["POST"])
@requiere_rol("Administrador", "Bodega")
def desactivar_proveedor(id_proveedor):
    """Desactiva lógicamente un proveedor en MySQL."""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE PROVEEDOR
                SET estado = 0
                WHERE id_proveedor = %s AND estado = 1;
            """, (id_proveedor,))
        connection.commit()
        flash("Proveedor desactivado.", "success")
    finally:
        connection.close()

    return redirect(url_for("proveedores"))


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))

register_control_routes(app, requiere_rol, obtener_sucursal_empleado)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG") == "1")
