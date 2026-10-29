"""Pruebas transaccionales contra un esquema temporal, nunca contra producción.

Ejecutar con MYSQL_PUBLIC_URL o TEST_MYSQL_URL y el cliente mysql instalado.
"""
import os
import subprocess
import sys
import unittest
import uuid
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlparse, unquote
import pymysql

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "web"))
import inventory_control as control

SCHEMA = "ce_acceptance_" + uuid.uuid4().hex[:12]
URL = urlparse(os.environ.get("TEST_MYSQL_URL") or os.environ["MYSQL_PUBLIC_URL"])


def connect():
    return pymysql.connect(host=URL.hostname, port=URL.port or 3306, user=unquote(URL.username), password=unquote(URL.password), database=SCHEMA, cursorclass=pymysql.cursors.DictCursor)


def install():
    env = os.environ.copy()
    env["MYSQL_PWD"] = unquote(URL.password)
    for name in ("sql/ddl/01_schema.sql", "sql/migrations/08_inventory_control.sql", "sql/migrations/09_supplier_proposals.sql", "sql/triggers/01_triggers.sql", "sql/triggers/02_inventory_control.sql", "sql/procedures/01_procedures.sql", "sql/procedures/02_transfer_workflow.sql", "sql/views/01_views.sql"):
        sql = (ROOT / name).read_text().replace("comercial_estuardo_db", SCHEMA)
        result = subprocess.run(["mysql", "--default-character-set=utf8mb4", "-h", URL.hostname, "-P", str(URL.port or 3306), "-u", unquote(URL.username)], input=sql.encode(), env=env, capture_output=True)
        if result.returncode:
            raise RuntimeError(f"No se pudo instalar {name}: {result.stderr.decode()}")


class InventoryIntegration(unittest.TestCase):
    def setUp(self):
        self.db = connect()
        self.c = self.db.cursor()
        self.token = uuid.uuid4().hex[:10]
        self.branches = []
        for suffix in ("A", "B"):
            self.c.execute("INSERT INTO SUCURSAL(nombre,direccion,telefono,municipio) VALUES(%s,'Prueba','55555555','Prueba')", (self.token + suffix,))
            self.branches.append(self.c.lastrowid)
        self.employees = []
        for index, role in enumerate(("Administrador", "Bodega", "Bodega", "Vendedor")):
            self.c.execute("INSERT INTO EMPLEADO(cui,nombres,apellidos,cargo,telefono,fecha_ingreso,id_sucursal) VALUES(%s,'Prueba','Prueba',%s,'55555555',CURRENT_DATE,%s)", (str(uuid.uuid4().int)[:13], role, self.branches[1] if index == 2 else self.branches[0]))
            self.employees.append(self.c.lastrowid)
        self.admin, self.origin_user, self.dest_user, self.seller = self.employees
        self.a, self.b = self.branches
        self.c.execute("INSERT INTO CLIENTE(nit,nombres,telefono,direccion) VALUES(%s,'Prueba','55555555','Prueba')", (self.token,))
        self.client = self.c.lastrowid
        self.c.execute("INSERT INTO PROVEEDOR(nit,razon_social,telefono) VALUES(%s,'Prueba','55555555')", (self.token,))
        self.provider = self.c.lastrowid
        self.products = []
        for category in ("Motos ", "Accesorios "):
            self.c.execute("INSERT INTO CATEGORIA(nombre) VALUES(%s)", (category + self.token,))
            self.c.execute("INSERT INTO PRODUCTO(nombre,precio_costo,precio_venta,id_categoria) VALUES(%s,10,20,%s)", (category + self.token, self.c.lastrowid))
            self.products.append(self.c.lastrowid)
        self.moto, self.helmet = self.products
        self.purchase = control.register_purchase(self.c, self.origin_user, self.a, "TEST-" + self.token, self.provider, [
            {"id_producto": self.moto, "cantidad": 2, "costo_unitario": "10", "series": f"{self.token}VIN1 | {self.token}MOTOR1\n{self.token}VIN2 | {self.token}MOTOR2"},
            {"id_producto": self.helmet, "cantidad": 10, "costo_unitario": "10", "series": ""},
        ])
        self.db.commit()
        self.c.execute("SELECT * FROM UNIDAD_PRODUCTO WHERE id_producto=%s ORDER BY id_unidad", (self.moto,))
        self.units = self.c.fetchall()

    def tearDown(self):
        self.db.rollback()
        self.c.close()
        self.db.close()

    def balance(self, branch, pid):
        self.c.execute("SELECT stock_actual,stock_reservado FROM INVENTARIO_SUCURSAL WHERE id_sucursal=%s AND id_producto=%s", (branch, pid))
        row = self.c.fetchone()
        return (row["stock_actual"], row["stock_reservado"]) if row else (0, 0)

    def transfer(self, pid, qty, ids=()):
        return control.request_transfer(self.c, self.origin_user, self.a, self.b, uuid.uuid4().hex[:25], [{"id_producto": pid, "cantidad": qty, "unidades": list(ids)}])

    def sale(self, pid, qty=1, unit=None, branch=None, employee=None):
        self.c.execute("INSERT INTO VENTA(serie_factura,numero_factura,total_venta,tipo_pago,id_cliente,id_empleado,id_sucursal) VALUES(%s,1,%s,'Efectivo',%s,%s,%s)", (uuid.uuid4().hex[:10], 20 * qty, self.client, employee or self.seller, branch or self.a))
        vid = self.c.lastrowid
        self.c.execute("INSERT INTO DETALLE_VENTA(id_venta,id_producto,cantidad,precio_unitario,subtotal,vin_chasis,numero_motor) VALUES(%s,%s,%s,20,%s,%s,%s)", (vid, pid, qty, 20 * qty, unit["vin_chasis"] if unit else None, unit["numero_motor"] if unit else None))
        return vid, self.c.lastrowid

    def test_reservation_dispatch_partial_receipt_and_ledger(self):
        tid = self.transfer(self.helmet, 8)
        control.transfer_action(self.c, self.admin, tid, "aprobar")
        self.assertEqual(self.balance(self.a, self.helmet), (10, 8))
        with self.assertRaises(pymysql.MySQLError):
            self.sale(self.helmet, 3)
        control.transfer_action(self.c, self.origin_user, tid, "despachar")
        self.assertEqual(self.balance(self.a, self.helmet), (2, 0))
        control.transfer_action(self.c, self.dest_user, tid, "recibir", "Faltan tres unidades", [{"id_producto": self.helmet, "cantidad": 5}])
        self.assertEqual(self.balance(self.b, self.helmet), (5, 0))
        control.transfer_action(self.c, self.dest_user, tid, "recibir", "Llegaron las tres pendientes", [{"id_producto": self.helmet, "cantidad": 8}])
        self.assertEqual(self.balance(self.b, self.helmet), (8, 0))
        with self.assertRaises(control.InventoryError):
            control.transfer_action(self.c, self.dest_user, tid, "recibir", received=[{"id_producto": self.helmet, "cantidad": 8}])
        self.c.execute("SELECT SUM(cantidad) total FROM MOVIMIENTO_INVENTARIO WHERE id_producto=%s", (self.helmet,))
        self.assertEqual(self.c.fetchone()["total"], 10)

    def test_serial_transfer_and_sale(self):
        tid = self.transfer(self.moto, 1, [self.units[0]["id_unidad"]])
        control.transfer_action(self.c, self.admin, tid, "aprobar")
        with self.assertRaises(pymysql.MySQLError):
            self.sale(self.moto, unit=self.units[0])
        control.transfer_action(self.c, self.origin_user, tid, "despachar")
        control.transfer_action(self.c, self.dest_user, tid, "recibir", received=[{"id_producto": self.moto, "cantidad": 1, "unidades": [self.units[0]["id_unidad"]]}])
        self.sale(self.moto, unit=self.units[0], branch=self.b, employee=self.dest_user)
        self.assertEqual(self.balance(self.b, self.moto), (0, 0))
        self.c.execute("SELECT COUNT(*) n FROM HISTORIAL_UNIDAD WHERE id_unidad=%s", (self.units[0]["id_unidad"],))
        self.assertGreaterEqual(self.c.fetchone()["n"], 5)

    def test_sale_return_and_resale_keeps_original(self):
        vid, did = self.sale(self.moto, unit=self.units[0])
        control.reverse_document(self.c, self.admin, "venta", vid, False, {did: 1}, "Devolución física", {})
        self.sale(self.moto, unit=self.units[0])
        self.c.execute("SELECT COUNT(*) n FROM DETALLE_VENTA WHERE vin_chasis=%s", (self.units[0]["vin_chasis"],))
        self.assertEqual(self.c.fetchone()["n"], 2)
        with self.assertRaises(control.InventoryError):
            control.reverse_document(self.c, self.admin, "venta", vid, False, {did: 1}, "Otra devolución", {})

    def test_cancel_sale_preserves_history_and_avoids_duplicate_stock(self):
        vid, _ = self.sale(self.helmet, 2)
        control.reverse_document(self.c, self.admin, "venta", vid, True, {}, "Error de facturación", {})
        self.assertEqual(self.balance(self.a, self.helmet), (10, 0))
        with self.assertRaises(control.InventoryError):
            control.reverse_document(self.c, self.admin, "venta", vid, True, {}, "Reintento", {})
        self.c.execute("SELECT estado FROM VENTA WHERE id_venta=%s", (vid,))
        self.assertEqual(self.c.fetchone()["estado"], "Anulada")
        with self.assertRaises(pymysql.MySQLError):
            self.c.execute("DELETE FROM VENTA WHERE id_venta=%s", (vid,))

    def test_stale_count_and_approved_adjustment(self):
        cid = control.request_count(self.c, self.origin_user, self.a, self.helmet, 9, "Conteo físico", [], [])
        self.sale(self.helmet)
        with self.assertRaises(control.InventoryError):
            control.resolve_count(self.c, self.admin, cid, True, "")
        cid = control.request_count(self.c, self.origin_user, self.a, self.helmet, 8, "Conteo nuevo", [], [])
        control.resolve_count(self.c, self.admin, cid, True, "Verificado")
        self.assertEqual(self.balance(self.a, self.helmet), (8, 0))

    def test_serial_count_identifies_missing_and_new_units(self):
        cid = control.request_count(self.c, self.origin_user, self.a, self.moto, 2, "Una unidad cambió", [self.units[0]["id_unidad"]], [{"vin": self.token + "NEW", "motor": self.token + "NEW"}])
        control.resolve_count(self.c, self.admin, cid, True, "Verificado")
        self.c.execute("SELECT estado FROM UNIDAD_PRODUCTO WHERE id_unidad=%s", (self.units[1]["id_unidad"],))
        self.assertEqual(self.c.fetchone()["estado"], "Baja")
        self.assertEqual(self.balance(self.a, self.moto), (2, 0))

    def test_purchase_return_exact_units(self):
        did = self.units[0]["id_detalle_compra"]
        control.reverse_document(self.c, self.admin, "compra", self.purchase, False, {did: 1}, "Defecto de fábrica", {did: [self.units[0]["id_unidad"]]})
        self.assertEqual(self.balance(self.a, self.moto), (1, 0))
        self.c.execute("SELECT estado FROM UNIDAD_PRODUCTO WHERE id_unidad=%s", (self.units[0]["id_unidad"],))
        self.assertEqual(self.c.fetchone()["estado"], "Devuelta a proveedor")

    def test_cancel_releases_reservation_and_scope(self):
        tid = self.transfer(self.moto, 1, [self.units[0]["id_unidad"]])
        with self.assertRaises(control.InventoryError):
            control.transfer_action(self.c, self.origin_user, tid, "aprobar")
        control.transfer_action(self.c, self.admin, tid, "aprobar")
        control.transfer_action(self.c, self.admin, tid, "anular", "Cambio de destino")
        self.assertEqual(self.balance(self.a, self.moto), (2, 0))
        with self.assertRaises(control.InventoryError):
            control.request_count(self.c, self.dest_user, self.a, self.helmet, 0, "Inválido", [], [])

    def test_concurrent_approvals_do_not_overreserve(self):
        one = self.transfer(self.helmet, 8)
        two = self.transfer(self.helmet, 8)
        self.db.commit()
        def approve(tid):
            db = connect()
            try:
                with db.cursor() as c:
                    control.transfer_action(c, self.admin, tid, "aprobar")
                db.commit()
                return True
            except control.InventoryError:
                db.rollback()
                return False
            finally:
                db.close()
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(approve, [one, two]))
        self.db.rollback()
        self.assertEqual(sorted(results), [False, True])
        self.assertEqual(self.balance(self.a, self.helmet), (10, 8))

    def test_pages_render_and_roles_are_scoped(self):
        os.environ.setdefault("SECRET_KEY", "acceptance-only-secret")
        import app as app_module
        import control_routes
        app_module.get_db_connection = connect
        control_routes.get_db_connection = connect
        app_module.app.config.update(TESTING=True)
        client = app_module.app.test_client()
        for user, role in ((self.admin, "Administrador"), (self.origin_user, "Bodega"), (self.seller, "Vendedor")):
            with client.session_transaction() as session:
                session.update(user_id=user, user_role=role, user_name="Prueba", csrf_token="test-token")
            for path in ("/resumen", "/inventario", "/unidades", "/kardex", "/alertas", "/unidades/" + str(self.units[0]["id_unidad"])):
                self.assertEqual(client.get(path).status_code, 200, (role, path))
            self.assertEqual(client.get("/respaldos").status_code, 200 if role == "Administrador" else 403)
            self.assertEqual(client.get("/conteos").status_code, 403 if role == "Vendedor" else 200)
        with client.session_transaction() as session:
            session.update(user_id=self.admin, user_role="Administrador")
        tid = self.transfer(self.helmet, 1)
        self.db.commit()
        vid, _ = self.sale(self.helmet)
        self.db.commit()
        for path in (f"/traslados/{tid}", "/traslados/nuevo", "/ventas/nueva", "/compras/nueva", f"/documentos/compra/{self.purchase}/reversar", f"/conteos?sucursal={self.a}&producto={self.moto}", "/inventario?vista=general", "/inventario?estado=disponible", "/productos/nuevo", "/productos", "/ventas", "/compras", f"/ventas/{vid}", f"/compras/{self.purchase}"):
            self.assertEqual(client.get(path).status_code, 200, path)

    def test_failed_purchase_rolls_back_header_stock_and_units(self):
        with self.assertRaises(pymysql.IntegrityError):
            control.register_purchase(self.c, self.origin_user, self.a, "DUP-" + self.token, self.provider,
                [{"id_producto": self.moto, "cantidad": 1, "costo_unitario": "10", "series": f"{self.units[0]['vin_chasis']} | NEW{self.token}"}])
        self.db.rollback()
        self.c.execute("SELECT COUNT(*) n FROM COMPRA WHERE numero_orden=%s", ("DUP-" + self.token,))
        self.assertEqual(self.c.fetchone()["n"], 0)
        self.assertEqual(self.balance(self.a, self.moto), (2, 0))

    def test_partial_refund_rounding_never_exceeds_original(self):
        self.c.execute("UPDATE PRODUCTO SET precio_costo=0 WHERE id_producto=%s", (self.helmet,))
        self.c.execute("INSERT INTO VENTA(serie_factura,numero_factura,total_venta,tipo_pago,id_cliente,id_empleado,id_sucursal) VALUES(%s,1,0.03,'Efectivo',%s,%s,%s)", (self.token, self.client, self.seller, self.a))
        vid = self.c.lastrowid
        self.c.execute("INSERT INTO DETALLE_VENTA(id_venta,id_producto,cantidad,precio_unitario,descuento,subtotal) VALUES(%s,%s,6,20,119.97,0.03)", (vid, self.helmet))
        did = self.c.lastrowid
        for quantity in (1, 1, 1, 1, 2):
            control.reverse_document(self.c, self.admin, "venta", vid, False, {did: quantity}, "Devolución parcial", {})
            self.c.execute("SELECT SUM(importe) total FROM REVERSO_DOCUMENTO WHERE id_venta=%s", (vid,))
            self.assertLessEqual(self.c.fetchone()["total"], Decimal("0.03"))
        self.c.execute("SELECT SUM(importe) total FROM REVERSO_DOCUMENTO WHERE id_venta=%s", (vid,))
        self.assertEqual(self.c.fetchone()["total"], Decimal("0.03"))


if __name__ == "__main__":
    if "--isolated" not in sys.argv:
        raise SystemExit("Requiere --isolated; crea y elimina únicamente un esquema ce_acceptance_*.")
    sys.argv.remove("--isolated")
    install()
    try:
        suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(name, InventoryIntegration) for name in sys.argv[1:]) if len(sys.argv)>1 else unittest.defaultTestLoader.loadTestsFromTestCase(InventoryIntegration)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
    finally:
        db = connect()
        with db.cursor() as cursor:
            cursor.execute(f"DROP DATABASE `{SCHEMA}`")
        db.close()
    raise SystemExit(0 if result.wasSuccessful() else 1)
