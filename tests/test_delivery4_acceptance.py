"""Instalación completa y flujos de entrega en una base y roles temporales."""
import hashlib
import json
import os
import secrets
import sys
import platform
import importlib.metadata
import unittest
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote
import pymysql
from werkzeug.security import generate_password_hash
import test_inventory_control as base
import inventory_control as control

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/entrega-4/evidencias/VERIFICACION_ENTREGA4.json"
MAIN_TABLES = ("SUCURSAL","EMPLEADO","CLIENTE","CATEGORIA","PRODUCTO","PROVEEDOR","COMPRA","VENTA")


def metadata(files):
    """Captura solo estructura y conteos sintéticos; nunca contraseñas ni filas de personas."""
    db = base.connect()
    result = {"fecha_utc": datetime.now(timezone.utc).isoformat(), "entorno": "MySQL temporal aislado, no producción", "esquema_temporal": base.SCHEMA,
              "scripts": [{"ruta":f,"sha256":hashlib.sha256((ROOT/f).read_bytes()).hexdigest()} for f in files]}
    result['python']=platform.python_version()
    result['dependencias']={name:importlib.metadata.version(name) for name in ('Flask','PyMySQL','cryptography','gunicorn','python-dotenv')}
    with db.cursor() as c:
        c.execute("SELECT VERSION() version")
        result["mysql"] = c.fetchone()["version"]
        queries = {
            "tablas": "SELECT TABLE_NAME,TABLE_TYPE,ENGINE FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA=DATABASE() ORDER BY TABLE_NAME",
            "columnas": "SELECT TABLE_NAME,COLUMN_NAME,COLUMN_TYPE,IS_NULLABLE,COLUMN_KEY,COLUMN_DEFAULT,EXTRA,GENERATION_EXPRESSION FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=DATABASE() ORDER BY TABLE_NAME,ORDINAL_POSITION",
            "restricciones": "SELECT TABLE_NAME,CONSTRAINT_NAME,CONSTRAINT_TYPE FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS WHERE CONSTRAINT_SCHEMA=DATABASE() ORDER BY TABLE_NAME,CONSTRAINT_NAME",
            "fks": "SELECT k.TABLE_NAME,k.COLUMN_NAME,k.REFERENCED_TABLE_NAME,k.REFERENCED_COLUMN_NAME,r.UPDATE_RULE,r.DELETE_RULE FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE k JOIN INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS r ON r.CONSTRAINT_SCHEMA=k.CONSTRAINT_SCHEMA AND r.CONSTRAINT_NAME=k.CONSTRAINT_NAME AND r.TABLE_NAME=k.TABLE_NAME WHERE k.CONSTRAINT_SCHEMA=DATABASE() AND k.REFERENCED_TABLE_NAME IS NOT NULL ORDER BY k.TABLE_NAME,k.COLUMN_NAME",
            "checks": "SELECT CONSTRAINT_NAME,CHECK_CLAUSE FROM INFORMATION_SCHEMA.CHECK_CONSTRAINTS WHERE CONSTRAINT_SCHEMA=DATABASE() ORDER BY CONSTRAINT_NAME",
            "triggers": "SELECT TRIGGER_NAME,EVENT_MANIPULATION,EVENT_OBJECT_TABLE,ACTION_TIMING FROM INFORMATION_SCHEMA.TRIGGERS WHERE TRIGGER_SCHEMA=DATABASE() ORDER BY TRIGGER_NAME",
            "procedimientos": "SELECT ROUTINE_NAME,ROUTINE_TYPE FROM INFORMATION_SCHEMA.ROUTINES WHERE ROUTINE_SCHEMA=DATABASE() ORDER BY ROUTINE_NAME",
        }
        for name,query in queries.items():
            c.execute(query)
            result[name] = c.fetchall()
        result["filas_principales"] = {}
        for name in MAIN_TABLES:
            c.execute(f"SELECT COUNT(*) n FROM {name}")
            count = c.fetchone()["n"]
            if count < 50:
                raise AssertionError(f"{name}: solo {count} registros de demostración")
            result["filas_principales"][name] = count
        result["roles_temporales"] = list(base.ROLE_NAMES.values())
    db.close()
    return result


class DeliveryAcceptance(unittest.TestCase):
    setUp = base.InventoryIntegration.setUp
    tearDown = base.InventoryIntegration.tearDown

    def app(self):
        os.environ.setdefault("SECRET_KEY", secrets.token_urlsafe(32))
        import app as application
        import control_routes
        application.get_db_connection = base.connect
        control_routes.get_db_connection = base.connect
        application.app.config.update(TESTING=True, SESSION_COOKIE_SECURE=False)
        return application

    def login(self, user):
        password = secrets.token_urlsafe(18)
        self.c.execute("UPDATE EMPLEADO SET password_hash=%s WHERE id_empleado=%s", (generate_password_hash(password,method="pbkdf2:sha256"),user))
        self.c.execute("SELECT cui FROM EMPLEADO WHERE id_empleado=%s", (user,))
        cui = self.c.fetchone()["cui"]
        self.db.commit()
        client = self.app().app.test_client()
        self.assertEqual(client.get("/").status_code, 200)
        with client.session_transaction() as session:
            token = session["csrf_token"]
        self.assertEqual(client.post("/",data={"username":cui,"password":password}).status_code,400)
        response=client.post("/",data={"username":cui,"password":password,"csrf_token":token})
        self.assertEqual(response.status_code,302)
        self.assertEqual(client.get("/resumen").status_code,200)
        with client.session_transaction() as session:
            token=session["csrf_token"]
        return client,token

    def test_real_login_csrf_logout_and_permissions(self):
        client,token=self.login(self.seller)
        for path in ("/categorias","/sucursales","/empleados","/proveedores","/conteos","/respaldos"):
            self.assertEqual(client.get(path).status_code,403,path)
        self.assertEqual(client.get("/ventas").status_code,200)
        self.assertEqual(client.post("/logout").status_code,400)
        self.assertEqual(client.post("/logout",data={"csrf_token":token}).status_code,302)
        self.assertEqual(client.get("/ventas").status_code,302)

    def test_catalog_crud_from_forms_persists(self):
        client,token=self.login(self.admin)
        cases=[
            ("categorias","CATEGORIA","id_categoria",{"nombre":"Nueva "+self.token,"descripcion":"Prueba"},"nombre"),
            ("sucursales","SUCURSAL","id_sucursal",{"nombre":"Nueva "+self.token,"direccion":"Prueba","telefono":"55555555","municipio":"Prueba"},"nombre"),
            ("clientes","CLIENTE","id_cliente",{"nit":"C"+self.token,"cui":"","nombres":"Nuevo "+self.token,"apellidos":"Prueba","telefono":"55555555","correo":"prueba@example.com","direccion":"Prueba"},"nombres"),
            ("productos","PRODUCTO","id_producto",{"codigo_barra":"SKU"+self.token,"nombre":"Nuevo "+self.token,"descripcion":"Prueba","precio_costo":"10","precio_venta":"20","stock_minimo":"1","id_categoria":str(self.category())},"nombre"),
        ]
        for route,table,key,data,label in cases:
            response=client.post(f"/{route}/nuevo" if route in ("clientes","productos") else f"/{route}/nueva",data={**data,"csrf_token":token})
            self.assertEqual(response.status_code,302,(route,response.status_code))
            self.db.rollback()
            self.c.execute(f"SELECT {key} FROM {table} WHERE {label}=%s",(data[label],))
            identifier=self.c.fetchone()[key]
            data[label]+=" editado"
            self.assertEqual(client.post(f"/{route}/editar/{identifier}",data={**data,"csrf_token":token}).status_code,302)
            self.db.rollback()
            self.c.execute(f"SELECT {label} FROM {table} WHERE {key}=%s",(identifier,))
            self.assertEqual(self.c.fetchone()[label],data[label])
            self.assertEqual(client.post(f"/{route}/desactivar/{identifier}",data={"csrf_token":token}).status_code,302)
            self.db.rollback()
            self.c.execute(f"SELECT estado FROM {table} WHERE {key}=%s",(identifier,))
            self.assertEqual(self.c.fetchone()["estado"],0)

    def category(self):
        self.c.execute("SELECT id_categoria FROM PRODUCTO WHERE id_producto=%s",(self.helmet,))
        return self.c.fetchone()["id_categoria"]

    def test_employee_crud_password_and_self_protection(self):
        client,token=self.login(self.admin)
        data={"cui":str(secrets.randbelow(10**13)).zfill(13),"nombres":"Alta "+self.token,"apellidos":"Prueba","cargo":"Bodega","telefono":"55555555","correo":self.token+"@example.com","fecha_ingreso":"2026-10-29","id_sucursal":str(self.a),"password":secrets.token_urlsafe(15)}
        self.assertEqual(client.post("/empleados/nuevo",data={**data,"csrf_token":token}).status_code,302)
        self.db.rollback()
        self.c.execute("SELECT * FROM EMPLEADO WHERE cui=%s",(data["cui"],))
        employee=self.c.fetchone()
        self.assertNotEqual(employee["password_hash"],data["password"])
        data.update(nombres="Cambio "+self.token,password="")
        self.assertEqual(client.post(f"/empleados/editar/{employee['id_empleado']}",data={**data,"csrf_token":token}).status_code,302)
        self.assertEqual(client.post(f"/empleados/desactivar/{employee['id_empleado']}",data={"csrf_token":token}).status_code,302)
        self.assertEqual(client.post(f"/empleados/desactivar/{self.admin}",data={"csrf_token":token}).status_code,302)
        self.db.rollback()
        self.c.execute("SELECT estado FROM EMPLEADO WHERE id_empleado=%s",(self.admin,))
        self.assertEqual(self.c.fetchone()["estado"],1)

    def test_multiline_purchase_and_sale_from_forms(self):
        client,token=self.login(self.origin_user)
        order="ACCEPT-"+self.token
        response=client.post("/compras/nueva",data={"csrf_token":token,"numero_orden":order,"id_proveedor":str(self.provider),"id_producto":[str(self.moto),str(self.helmet)],"cantidad":["1","2"],"costo_unitario":["10","10"],"series":[self.token+"NEWVIN | "+self.token+"NEWMOTOR",""]})
        self.assertEqual(response.status_code,302)
        self.db.rollback()
        self.c.execute("SELECT id_compra,total_compra FROM COMPRA WHERE numero_orden=%s",(order,))
        purchase=self.c.fetchone();self.assertEqual(purchase["total_compra"],30)
        self.c.execute("SELECT COUNT(*) n FROM DETALLE_COMPRA WHERE id_compra=%s",(purchase["id_compra"],))
        self.assertEqual(self.c.fetchone()["n"],2)
        seller,token=self.login(self.seller)
        response=seller.post("/ventas/nueva",data={"csrf_token":token,"id_cliente":str(self.client),"tipo_pago":"Efectivo","id_producto":[str(self.moto),str(self.helmet)],"cantidad":["1","2"],"descuento":["0","0"],"vin_chasis":[self.units[0]["vin_chasis"],""],"numero_motor":[self.units[0]["numero_motor"],""]})
        self.assertEqual(response.status_code,302)
        self.db.rollback()
        self.c.execute("SELECT id_venta,total_venta FROM VENTA WHERE id_cliente=%s ORDER BY id_venta DESC LIMIT 1",(self.client,))
        sale=self.c.fetchone();self.assertEqual(sale["total_venta"],60)
        self.c.execute("SELECT COUNT(*) n FROM DETALLE_VENTA WHERE id_venta=%s",(sale["id_venta"],))
        self.assertEqual(self.c.fetchone()["n"],2)

    def test_document_update_is_audited_without_stock_or_amount_change(self):
        vid,_=base.InventoryIntegration.sale(self,self.helmet)
        self.db.commit()
        client,token=self.login(self.admin)
        self.c.execute("SELECT stock_actual FROM INVENTARIO_SUCURSAL WHERE id_sucursal=%s AND id_producto=%s",(self.a,self.helmet))
        original=self.c.fetchone()["stock_actual"]
        for kind,did,data in (("venta",vid,{"id_cliente":str(self.client),"tipo_pago":"Transferencia"}),("compra",self.purchase,{"id_proveedor":str(self.provider),"numero_orden":"FIX-"+self.token})):
            self.assertEqual(client.get(f"/documentos/{kind}/{did}/corregir").status_code,200)
            self.assertEqual(client.post(f"/documentos/{kind}/{did}/corregir",data={**data,"motivo":"Corrección de digitación","csrf_token":token}).status_code,302)
        self.db.rollback()
        self.c.execute("SELECT COUNT(*) n FROM CORRECCION_DOCUMENTO WHERE id_empleado=%s",(self.admin,))
        self.assertEqual(self.c.fetchone()["n"],2)
        self.c.execute("SELECT stock_actual FROM INVENTARIO_SUCURSAL WHERE id_sucursal=%s AND id_producto=%s",(self.a,self.helmet))
        self.assertEqual(self.c.fetchone()["stock_actual"],original)
        self.c.execute("SELECT total_venta,tipo_pago FROM VENTA WHERE id_venta=%s",(vid,))
        self.assertEqual(self.c.fetchone(),{"total_venta":20,"tipo_pago":"Transferencia"})
        bodega,bt=self.login(self.origin_user)
        self.assertEqual(bodega.post(f"/documentos/compra/{self.purchase}/corregir",data={"csrf_token":bt}).status_code,403)
        with self.assertRaises(control.InventoryError):
            control.correct_document(self.c,self.admin,"venta",vid,{"id_cliente":self.client,"tipo_pago":"Efectivo"},"")

    def test_database_roles_have_different_effective_permissions(self):
        users=[]
        try:
            for original,role in base.ROLE_NAMES.items():
                user="ce_user_"+secrets.token_hex(7)
                password=secrets.token_urlsafe(25)
                self.c.execute("CREATE USER %s@'%%' IDENTIFIED BY %s",(user,password))
                users.append(user)
                self.c.execute(f"GRANT `{role}` TO '{user}'@'%'")
                self.c.execute(f"SET DEFAULT ROLE `{role}` TO '{user}'@'%'")
                db=pymysql.connect(host=base.URL.hostname,port=base.URL.port or 3306,user=user,password=password,database=base.SCHEMA)
                with db.cursor() as q:
                    q.execute("SELECT COUNT(*) FROM PRODUCTO")
                    if original=='rol_administrador':
                        q.execute("CREATE TABLE PRUEBA_ROL(id INT PRIMARY KEY)")
                        q.execute("DROP TABLE PRUEBA_ROL")
                    else:
                        with self.assertRaises(pymysql.MySQLError):
                            q.execute("UPDATE PROVEEDOR SET razon_social='No autorizado' WHERE id_proveedor=%s",(self.provider,))
                    if original=='rol_ventas':
                        with self.assertRaises(pymysql.MySQLError):
                            q.execute("UPDATE PRODUCTO SET nombre='No autorizado' WHERE id_producto=%s",(self.helmet,))
                db.rollback();db.close()
        finally:
            for user in users:self.c.execute(f"DROP USER IF EXISTS '{user}'@'%'")

    def test_stored_procedures_and_stock_rollback(self):
        self.c.callproc('sp_registrar_compra_detallada',('SP-'+self.token,self.provider,self.origin_user,self.a,
                       json.dumps([{'id_producto':self.helmet,'cantidad':2,'costo_unitario':'10'}])))
        while self.c.nextset():pass
        self.c.execute('SELECT stock_actual FROM INVENTARIO_SUCURSAL WHERE id_sucursal=%s AND id_producto=%s',(self.a,self.helmet))
        self.assertEqual(self.c.fetchone()['stock_actual'],12)
        lines=[{'id_producto':self.helmet,'cantidad':2,'precio_unitario':'20','descuento':'0','vin_chasis':None,'numero_motor':None}]
        number=secrets.randbelow(1000000000)+1
        self.c.callproc('sp_registrar_venta_detallada',('PROC',number,'Efectivo',self.client,self.seller,self.a,json.dumps(lines)))
        while self.c.nextset():pass
        self.c.execute('SELECT stock_actual FROM INVENTARIO_SUCURSAL WHERE id_sucursal=%s AND id_producto=%s',(self.a,self.helmet))
        self.assertEqual(self.c.fetchone()['stock_actual'],10)

        lines[0]['cantidad']=9999
        with self.assertRaises(pymysql.MySQLError):
            self.c.callproc('sp_registrar_venta_detallada',('PROC',number+1,'Efectivo',self.client,self.seller,self.a,json.dumps(lines)))
        self.c.execute('SELECT COUNT(*) n FROM VENTA WHERE serie_factura=%s AND numero_factura=%s',('PROC',number+1))
        self.assertEqual(self.c.fetchone()['n'],0)
        self.c.execute('SELECT stock_actual FROM INVENTARIO_SUCURSAL WHERE id_sucursal=%s AND id_producto=%s',(self.a,self.helmet))
        self.assertEqual(self.c.fetchone()['stock_actual'],10)

    def test_invalid_input_and_under_cost_sales_are_rejected(self):
        client,token=self.login(self.admin)
        data={'codigo_barra':'INVALID'+self.token,'nombre':'Inválido '+self.token,'descripcion':'Prueba','precio_costo':'10','precio_venta':'5','stock_minimo':'1','id_categoria':str(self.category()),'csrf_token':token}
        self.assertEqual(client.post('/productos/nuevo',data=data).status_code,200)
        self.db.rollback()
        self.c.execute('SELECT COUNT(*) n FROM PRODUCTO WHERE codigo_barra=%s',(data['codigo_barra'],))
        self.assertEqual(self.c.fetchone()['n'],0)
        sale={'csrf_token':token,'id_cliente':str(self.client),'tipo_pago':'Efectivo','id_producto':str(self.helmet),'cantidad':'1','descuento':'15','vin_chasis':'','numero_motor':''}
        self.assertEqual(client.post('/ventas/nueva',data=sale).status_code,200)
        sale['cantidad']='cantidad inválida'
        self.assertEqual(client.post('/ventas/nueva',data=sale).status_code,200)
        self.db.rollback()
        self.c.execute('SELECT COUNT(*) n FROM VENTA WHERE id_cliente=%s',(self.client,))
        self.assertEqual(self.c.fetchone()['n'],0)
        lines=[{'id_producto':self.helmet,'cantidad':1,'precio_unitario':'20','descuento':'15','vin_chasis':None,'numero_motor':None}]
        number=secrets.randbelow(1000000000)+1
        with self.assertRaises(pymysql.MySQLError):
            self.c.callproc('sp_registrar_venta_detallada',('MARGEN',number,'Efectivo',self.client,self.seller,self.a,json.dumps(lines)))
        self.c.execute('SELECT COUNT(*) n FROM VENTA WHERE serie_factura=%s AND numero_factura=%s',('MARGEN',number))
        self.assertEqual(self.c.fetchone()['n'],0)
        self.c.execute('INSERT INTO CATEGORIA(nombre) VALUES(%s)',('Repuestos de Motor '+self.token,))
        category=self.c.lastrowid
        self.c.execute('INSERT INTO PRODUCTO(nombre,precio_costo,precio_venta,id_categoria) VALUES(%s,10,20,%s)',('Repuesto '+self.token,category))
        part=self.c.lastrowid
        self.c.execute('SELECT requiere_serie FROM PRODUCTO WHERE id_producto=%s',(part,))
        self.assertEqual(self.c.fetchone()['requiere_serie'],0)
        control.register_purchase(self.c,self.origin_user,self.a,'MOTOR-'+self.token,self.provider,
                                  [{'id_producto':part,'cantidad':1,'costo_unitario':'10','series':''}])



if __name__=='__main__':
    if '--isolated' not in sys.argv:raise SystemExit('Requiere --isolated; solo usa base y roles temporales.')
    sys.argv.remove('--isolated')
    report={}
    try:
        files=base.install(seed=True,roles=True)
        report=metadata(files)
        result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(DeliveryAcceptance))
        report['aceptacion']={'ejecutadas':result.testsRun,'fallos':len(result.failures),'errores':len(result.errors),'correcto':result.wasSuccessful()}
    finally:
        db=base.connect()
        with db.cursor() as c:
            c.execute(f"DROP DATABASE `{base.SCHEMA}`")
            for role in base.ROLE_NAMES.values():c.execute(f"DROP ROLE IF EXISTS `{role}`")
        db.close()
        report['esquema_y_roles_temporales_eliminados']=True
        REPORT.parent.mkdir(parents=True,exist_ok=True)
        REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2,default=str)+'\n')
    raise SystemExit(0 if report.get('aceptacion',{}).get('correcto') else 1)
