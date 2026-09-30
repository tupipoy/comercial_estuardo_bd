import os

from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash

from db import get_db_connection
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey_comercial_estuardo")

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
def inventario():
    if "user_id" not in session:
        return redirect(url_for("login"))

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


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=True)
