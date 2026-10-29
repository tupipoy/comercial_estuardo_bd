"""Matriz de permisos y aprobación de proveedores en un esquema MySQL temporal."""
import sys
import os
import json
import unittest
from concurrent.futures import ThreadPoolExecutor
import pymysql
import test_inventory_control as base
import supplier_control as suppliers
import inventory_control as control


class SupplierIntegration(unittest.TestCase):
    setUp = base.InventoryIntegration.setUp
    tearDown = base.InventoryIntegration.tearDown

    def data(self):
        return {"nit": "P" + self.token, "razon_social": "Propuesta " + self.token,
                "contacto": "Contacto", "telefono": "55555555", "correo": "proveedor@example.com", "direccion": "Dirección"}

    def http_client(self, employee, role):
        os.environ.setdefault("SECRET_KEY", "acceptance-only-secret")
        import app as application
        import control_routes
        application.get_db_connection = base.connect
        control_routes.get_db_connection = base.connect
        application.app.config.update(TESTING=True)
        client = application.app.test_client()
        with client.session_transaction() as session:
            session.update(user_id=employee, user_role=role, user_name="Prueba", csrf_token="test-token")
        return client

    def test_bodega_proposes_admin_corrects_and_approves_for_purchases(self):
        data = self.data()
        bodega = self.http_client(self.origin_user, "Bodega")
        response = bodega.post("/proveedores/nuevo", data={**data, "csrf_token": "test-token"})
        self.assertEqual(response.status_code, 302)
        self.db.rollback()
        self.c.execute("SELECT * FROM PROPUESTA_PROVEEDOR WHERE nit=%s", (data["nit"],))
        proposal = self.c.fetchone()
        self.assertEqual(proposal["estado"], "Pendiente")
        self.c.execute("SELECT COUNT(*) n FROM PROVEEDOR WHERE nit=%s", (data["nit"],))
        self.assertEqual(self.c.fetchone()["n"], 0)
        self.assertNotIn(data["razon_social"], bodega.get("/compras/nueva").get_data(as_text=True))
        admin = self.http_client(self.admin, "Administrador")
        data["razon_social"] += " corregida"
        response = admin.post(f"/proveedores/propuestas/{proposal['id_propuesta']}", data={**data, "accion": "aprobar", "observacion": "Datos comprobados", "csrf_token": "test-token"})
        self.assertEqual(response.status_code, 302)
        self.db.rollback()
        self.c.execute("SELECT * FROM PROPUESTA_PROVEEDOR WHERE id_propuesta=%s", (proposal["id_propuesta"],))
        approved = self.c.fetchone()
        self.assertEqual(approved["estado"], "Aprobada")
        self.assertEqual(approved["id_responsable"], self.admin)
        self.c.execute("SELECT * FROM PROVEEDOR WHERE id_proveedor=%s", (approved["id_proveedor"],))
        self.assertEqual(self.c.fetchone()["razon_social"], data["razon_social"])
        self.assertIn(data["razon_social"], bodega.get("/compras/nueva").get_data(as_text=True))
        for path in ("/proveedores", "/proveedores/propuestas", f"/proveedores/propuestas/{proposal['id_propuesta']}"):
            self.assertEqual(bodega.get(path).status_code, 200)
            self.assertEqual(admin.get(path).status_code, 200)
        self.c.execute("SELECT * FROM EVENTO_PROVEEDOR WHERE id_propuesta=%s ORDER BY id_evento", (proposal["id_propuesta"],))
        events = self.c.fetchall()
        self.assertEqual([e["id_empleado"] for e in events], [self.origin_user, self.admin])
        self.assertEqual(json.loads(events[1]["datos_anteriores"])["razon_social"], "Propuesta " + self.token)

    def test_permissions_are_enforced_on_direct_urls_and_posts(self):
        proposal = suppliers.propose(self.c, self.origin_user, self.data())
        self.db.commit()
        bodega = self.http_client(self.origin_user, "Bodega")
        self.assertEqual(bodega.get(f"/proveedores/editar/{self.provider}").status_code, 403)
        self.assertEqual(bodega.post(f"/proveedores/editar/{self.provider}", data={**self.data(), "csrf_token": "test-token"}).status_code, 403)
        self.assertEqual(bodega.post(f"/proveedores/desactivar/{self.provider}", data={"csrf_token": "test-token"}).status_code, 403)
        self.assertEqual(bodega.post(f"/proveedores/propuestas/{proposal}", data={**self.data(), "accion": "aprobar", "csrf_token": "test-token"}).status_code, 403)
        self.assertNotIn(f'/proveedores/editar/{self.provider}', bodega.get("/proveedores").get_data(as_text=True))
        other = self.http_client(self.dest_user, "Bodega")
        self.assertEqual(other.get(f"/proveedores/propuestas/{proposal}").status_code, 404)
        seller = self.http_client(self.seller, "Vendedor")
        for path in ("/proveedores", "/proveedores/nuevo", "/proveedores/propuestas"):
            self.assertEqual(seller.get(path).status_code, 403)
        admin = self.http_client(self.admin, "Administrador")
        self.assertEqual(admin.post(f"/proveedores/propuestas/{proposal}", data={"accion": "aprobar"}).status_code, 400)

    def test_admin_proposals_are_pending_and_rejection_is_audited(self):
        data = self.data()
        proposal = suppliers.propose(self.c, self.admin, data)
        self.c.execute("SELECT estado,id_proveedor FROM PROPUESTA_PROVEEDOR WHERE id_propuesta=%s", (proposal,))
        self.assertEqual(self.c.fetchone(), {"estado": "Pendiente", "id_proveedor": None})
        with self.assertRaises(control.InventoryError):
            suppliers.resolve(self.c, self.origin_user, proposal, True)
        with self.assertRaises(control.InventoryError):
            suppliers.resolve(self.c, self.admin, proposal, False)
        suppliers.resolve(self.c, self.admin, proposal, False, note="NIT incorrecto")
        self.c.execute("SELECT estado,observacion FROM PROPUESTA_PROVEEDOR WHERE id_propuesta=%s", (proposal,))
        self.assertEqual(self.c.fetchone(), {"estado": "Rechazada", "observacion": "NIT incorrecto"})
        with self.assertRaises(control.InventoryError):
            suppliers.resolve(self.c, self.admin, proposal, True)
        new_proposal = suppliers.propose(self.c, self.origin_user, data)
        self.assertNotEqual(new_proposal, proposal)
        self.c.execute("SELECT COUNT(*) n FROM PROVEEDOR WHERE nit=%s", (data["nit"],))
        self.assertEqual(self.c.fetchone()["n"], 0)

    def test_duplicates_and_failed_approval_are_atomic(self):
        data = self.data()
        proposal = suppliers.propose(self.c, self.origin_user, data)
        with self.assertRaises(control.InventoryError):
            suppliers.propose(self.c, self.admin, data)
        with self.assertRaises(control.InventoryError):
            suppliers.propose(self.c, self.origin_user, {**data, "nit": self.token})
        self.db.commit()
        with self.assertRaises(control.InventoryError):
            suppliers.resolve(self.c, self.admin, proposal, True, {**data, "nit": self.token})
        self.db.rollback()
        self.c.execute("SELECT estado FROM PROPUESTA_PROVEEDOR WHERE id_propuesta=%s", (proposal,))
        self.assertEqual(self.c.fetchone()["estado"], "Pendiente")
        provider = suppliers.resolve(self.c, self.admin, proposal, True)
        self.db.commit()
        with self.assertRaises(pymysql.IntegrityError):
            suppliers.update(self.c, self.admin, provider, {**data, "nit": self.token})
        self.db.rollback()
        self.c.execute("SELECT nit FROM PROVEEDOR WHERE id_proveedor=%s", (provider,))
        self.assertEqual(self.c.fetchone()["nit"], data["nit"])

    def test_only_admin_modifies_and_deactivates_preserving_purchase_history(self):
        data = {**self.data(), "nit": self.token}
        with self.assertRaises(control.InventoryError):
            suppliers.update(self.c, self.origin_user, self.provider, data)
        with self.assertRaises(control.InventoryError):
            suppliers.deactivate(self.c, self.origin_user, self.provider)
        suppliers.update(self.c, self.admin, self.provider, data)
        suppliers.deactivate(self.c, self.admin, self.provider)
        self.db.commit()
        self.c.execute("SELECT COUNT(*) n FROM COMPRA WHERE id_compra=%s AND id_proveedor=%s", (self.purchase, self.provider))
        self.assertEqual(self.c.fetchone()["n"], 1)
        self.c.execute("SELECT estado FROM PROVEEDOR WHERE id_proveedor=%s", (self.provider,))
        self.assertEqual(self.c.fetchone()["estado"], 0)
        with self.assertRaises(control.InventoryError):
            control.register_purchase(self.c, self.origin_user, self.a, "BLOCKED-" + self.token, self.provider, [{"id_producto": self.helmet, "cantidad": 1, "costo_unitario": "10", "series": ""}])
        bodega = self.http_client(self.origin_user, "Bodega")
        self.assertNotIn(data["razon_social"], bodega.get("/compras/nueva").get_data(as_text=True))
        self.assertIn(data["razon_social"], bodega.get("/proveedores?estado=inactivos").get_data(as_text=True))
        self.assertEqual(bodega.get(f"/compras/{self.purchase}").status_code, 200)
        self.c.execute("SELECT datos_nuevos FROM EVENTO_PROVEEDOR WHERE id_proveedor=%s AND accion='Desactivación'", (self.provider,))
        self.assertEqual(json.loads(self.c.fetchone()["datos_nuevos"])["estado"], 0)

    def test_concurrent_approvals_create_only_one_provider(self):
        proposal = suppliers.propose(self.c, self.origin_user, self.data())
        self.db.commit()
        def approve(_):
            db = base.connect()
            try:
                with db.cursor() as cursor:
                    suppliers.resolve(cursor, self.admin, proposal, True)
                db.commit()
                return True
            except control.InventoryError:
                db.rollback()
                return False
            finally:
                db.close()
        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(sorted(pool.map(approve, range(2))), [False, True])
        self.db.rollback()
        self.c.execute("SELECT COUNT(*) n FROM PROVEEDOR WHERE nit=%s", (self.data()["nit"],))
        self.assertEqual(self.c.fetchone()["n"], 1)
        self.c.execute("SELECT COUNT(*) n FROM EVENTO_PROVEEDOR WHERE id_propuesta=%s AND accion='Aprobación'", (proposal,))
        self.assertEqual(self.c.fetchone()["n"], 1)

    def test_stale_admin_session_cannot_modify_as_bodega(self):
        fake_admin = self.http_client(self.origin_user, "Administrador")
        response = fake_admin.post(f"/proveedores/editar/{self.provider}", data={**self.data(), "csrf_token": "test-token"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Solo Administración", response.get_data(as_text=True))
        self.db.rollback()
        self.c.execute("SELECT nit,estado FROM PROVEEDOR WHERE id_proveedor=%s", (self.provider,))
        self.assertEqual(self.c.fetchone(), {"nit": self.token, "estado": 1})


if __name__ == "__main__":
    if "--isolated" not in sys.argv:
        raise SystemExit("Requiere --isolated; únicamente usa un esquema ce_acceptance_* temporal.")
    sys.argv.remove("--isolated")
    base.install()
    try:
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SupplierIntegration))
    finally:
        db = base.connect()
        with db.cursor() as cursor:
            cursor.execute(f"DROP DATABASE `{base.SCHEMA}`")
        db.close()
    raise SystemExit(0 if result.wasSuccessful() else 1)
