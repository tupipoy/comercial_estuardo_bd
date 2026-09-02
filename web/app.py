import os
from flask import Flask, render_template, request
from db import get_db_connection
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route("/")
def index():
    solo_stock_bajo = request.args.get("stock_bajo", "0")
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            if solo_stock_bajo == "1":
                # RF-07: Consulta parametrizada de stock minimo
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
                # RF-05: Catalogo general
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
    port = int(os.getenv("PORT", 3000))
    app.run(host="0.0.0.0", port=port, debug=True)