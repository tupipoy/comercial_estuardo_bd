import os
from flask import Flask, render_template, request, redirect, url_for
from db import get_db_connection
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey_comercial_estuardo")

@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        identificador = request.form.get("username")  # Correo o CUI

        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                    SELECT e.id_empleado, e.nombres, e.apellidos, e.cargo, s.nombre AS sucursal
                    FROM EMPLEADO e
                    INNER JOIN SUCURSAL s ON e.id_sucursal = s.id_sucursal
                    WHERE (e.correo = %s OR e.cui = %s) AND e.estado = 1;
                """
                cursor.execute(sql, (identificador, identificador))
                empleado = cursor.fetchone()

                if empleado:
                    return redirect(url_for("inventario"))
                else:
                    error = "Empleado no encontrado o inactivo en el sistema."
        finally:
            connection.close()

    return render_template("login.html", error=error)

@app.route("/inventario")
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

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=True)