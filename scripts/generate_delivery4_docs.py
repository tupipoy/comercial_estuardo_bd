"""Genera diccionario y modelo relacional desde metadatos de aceptación aislada.

Requiere Pillow solo para exportar los diagramas; no es dependencia de la app.
"""
import html
import json
import math
import re
import struct
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/entrega-4'
DIAGRAMS=ROOT/'docs/diagramas'


def main():
    data=json.loads((OUT/'evidencias/VERIFICACION_ENTREGA4.json').read_text())
    tables=[r['TABLE_NAME'] for r in data['tablas'] if r['TABLE_TYPE']=='BASE TABLE']
    cols={t:[c for c in data['columnas'] if c['TABLE_NAME']==t] for t in tables}
    fks={(f['TABLE_NAME'],f['COLUMN_NAME']):f for f in data['fks']}
    lines=['# Diccionario de datos actualizado — Entrega 4','',
        'Fuente: instalación limpia de `sql/ddl/01_schema.sql` más migraciones 08, 09 y 10, comprobada en MySQL 8.4. La evidencia estructural completa está en [VERIFICACION_ENTREGA4.json](evidencias/VERIFICACION_ENTREGA4.json).',
        '',f'El modelo vigente contiene **{len(tables)} tablas**, 3 vistas, 15 triggers y 8 procedimientos. Las ocho entidades principales del negocio son SUCURSAL, EMPLEADO, CLIENTE, CATEGORIA, PRODUCTO, PROVEEDOR, COMPRA y VENTA. Las restantes resuelven relaciones, existencias, auditoría y operaciones.','',
        'Convención conservada: tablas `UPPER_SNAKE_CASE`, columnas `snake_case`. No se renombraron tablas productivas para corregir estilo.','']
    def escape(value):return str(value if value is not None else '—').replace('|','\\|').replace('\n',' ')
    for table in tables:
        lines += [f'## {table}','','| Campo | Tipo | Nulo | Clave | Predeterminado / detalle |','|---|---|---|---|---|']
        for c in cols[table]:
            details=[]
            if c['COLUMN_DEFAULT'] is not None:details.append('DEFAULT '+str(c['COLUMN_DEFAULT']))
            if c['EXTRA']:details.append(c['EXTRA'])
            if c['GENERATION_EXPRESSION']:details.append(c['GENERATION_EXPRESSION'])
            fk=fks.get((table,c['COLUMN_NAME']))
            if fk:details.append(f"FK {fk['REFERENCED_TABLE_NAME']}.{fk['REFERENCED_COLUMN_NAME']}; UPDATE {fk['UPDATE_RULE']}; DELETE {fk['DELETE_RULE']}")
            lines.append('| '+' | '.join(escape(x) for x in (c['COLUMN_NAME'],c['COLUMN_TYPE'],'Sí' if c['IS_NULLABLE']=='YES' else 'No',c['COLUMN_KEY'] or '—','; '.join(details)))+' |')
        restrictions=[r for r in data['restricciones'] if r['TABLE_NAME']==table and r['CONSTRAINT_TYPE'] in ('CHECK','UNIQUE')]
        if restrictions:
            lines += ['','Restricciones adicionales:']
            for r in restrictions:
                check=next((x['CHECK_CLAUSE'] for x in data['checks'] if x['CONSTRAINT_NAME']==r['CONSTRAINT_NAME']),None)
                lines.append(f"- `{r['CONSTRAINT_NAME']}` ({r['CONSTRAINT_TYPE']})"+(f": `{escape(check)}`" if check else '.'))
        lines.append('')
    lines += ['## Reglas de interpretación','',
        '- `UNIDAD_PRODUCTO` impone unicidad global de VIN y motor. Los seriales de DETALLE_VENTA se conservan como dato histórico y no son únicos allí: una unidad devuelta puede venderse de nuevo.',
        '- `stock_actual` representa existencias físicas; `stock_reservado` las unidades apartadas. Disponible se calcula como físico menos reservado; tránsito se deriva de traslados pendientes.',
        '- Los totales y subtotales se calculan en procedimientos/servicios dentro de la misma transacción. Se conservan como importes históricos y se comprueba su consistencia. Es una desnormalización controlada que el equipo debe justificar frente a S7.',
        '- `CORRECCION_DOCUMENTO` permite actualizar cabeceras con versiones anteriores y nuevas. Las correcciones de cantidades se realizan con reversos, sin borrar líneas emitidas.',
        '- Los JSON de auditoría conservan versiones históricas; no sustituyen las entidades relacionales ni las dos relaciones N:M principales.',
        '- Las acciones RESTRICT declaradas explícitamente en los scripts nuevos conservan la semántica restrictiva de las referencias previas.', '']
    (OUT/'ENTREGA4_DICCIONARIO_DATOS.md').write_text('\n'.join(lines))

    # Recuperar el Chen original, sin redibujarlo ni inventar aprobación docente.
    raw=(DIAGRAMS/'comercialchen3.drawio.png').read_bytes();offset=8;chen=None
    while offset<len(raw):
        length=struct.unpack('>I',raw[offset:offset+4])[0];kind=raw[offset+4:offset+8];payload=raw[offset+8:offset+8+length];offset+=length+12
        if kind==b'tEXt' and payload.startswith(b'mxfile\0'):
            chen=unquote(payload.split(b'\0',1)[1].decode());break
    if not chen:raise ValueError('No se encontró el modelo Chen incrustado en el PNG.')
    if len(ET.fromstring(chen).findall('.//mxCell'))<20:raise ValueError('El modelo recuperado está incompleto.')
    (DIAGRAMS/'comercialchen4.drawio').write_text(chen)

    order=['SUCURSAL','EMPLEADO','CLIENTE','CATEGORIA','PROVEEDOR','INVENTARIO_SUCURSAL','PRODUCTO','VENTA','COMPRA','PROPUESTA_PROVEEDOR','MOVIMIENTO_INVENTARIO','DETALLE_VENTA','DETALLE_COMPRA','EVENTO_PROVEEDOR','CONTEO_INVENTARIO','UNIDAD_PRODUCTO','HISTORIAL_UNIDAD','TRASLADO','DETALLE_TRASLADO','TRASLADO_UNIDAD','REVERSO_DOCUMENTO','DETALLE_REVERSO','CORRECCION_DOCUMENTO','EVENTO_TRASLADO','RESPALDO_EJECUCION']
    order=[t for t in order if t in tables]+[t for t in tables if t not in order]
    width=3120;card_width=540;gap=65;left=70;top=175
    positions={};y=top
    for start in range(0,len(order),5):
        row=order[start:start+5]
        for index,table in enumerate(row):positions[table]=(left+index*(card_width+gap),y,card_width,55+len(cols[table])*25)
        y+=max(positions[t][3] for t in row)+110
    height=y+50
    image=Image.new('RGB',(width,height),'#f4f7fb');draw=ImageDraw.Draw(image)
    fonts=['/System/Library/Fonts/Supplemental/Arial.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']
    font_path=next((f for f in fonts if Path(f).exists()),None)
    def font(size):return ImageFont.truetype(font_path,size) if font_path else ImageFont.load_default()
    draw.text((70,35),'COMERCIAL ESTUARDO · MODELO RELACIONAL · ENTREGA 4',fill='#122b45',font=font(32))
    draw.text((70,90),'PK = clave primaria · FK = referencia · UQ = única · NN = obligatoria. Las líneas unen tablas hijas con sus tablas padre.',fill='#475569',font=font(19))
    draw.text((70,120),'Modelo físico completo, generado desde la instalación limpia. El Chen base se conserva por separado y las extensiones se documentan aquí.',fill='#475569',font=font(18))
    mx=ET.Element('mxfile',host='app.diagrams.net');diagram=ET.SubElement(mx,'diagram',name='Modelo relacional vigente')
    model=ET.SubElement(diagram,'mxGraphModel',grid='1',gridSize='10',page='1',pageWidth=str(width),pageHeight=str(height));root=ET.SubElement(model,'root')
    ET.SubElement(root,'mxCell',id='0');ET.SubElement(root,'mxCell',id='1',parent='0')
    for number,fk in enumerate(data['fks']):
        child,parent=fk['TABLE_NAME'],fk['REFERENCED_TABLE_NAME']
        cx,cy,cw,ch=positions[child];px,py,pw,ph=positions[parent]
        start=(cx+cw//2,cy);end=(px+pw//2,py+ph)
        if child==parent:continue
        mid=(start[1]+end[1])//2
        draw.line([start,(start[0],mid),(end[0],mid),end],fill='#a7b8cc',width=2)
        column=next(c for c in cols[child] if c['COLUMN_NAME']==fk['COLUMN_NAME'])
        unique=column['COLUMN_KEY']=='UNI' or (column['COLUMN_KEY']=='PRI' and sum(c['COLUMN_KEY']=='PRI' for c in cols[child])==1)
        edge=ET.SubElement(root,'mxCell',id=f'fk_{number}',value=fk['COLUMN_NAME'],edge='1',parent='1',source=child,target=parent,
             style='edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#94a3b8;startArrow='+('ERzeroToOne' if unique else 'ERzeroToMany')+';endArrow='+('ERzeroToOne' if column['IS_NULLABLE']=='YES' else 'ERone')+';fontSize=10;')
        ET.SubElement(edge,'mxGeometry',relative='1',attrib={'as':'geometry'})
    for table in order:
        x,y,w,h=positions[table];color='#16324f' if table in ('SUCURSAL','EMPLEADO','CLIENTE','CATEGORIA','PRODUCTO','PROVEEDOR','COMPRA','VENTA') else '#0f766e'
        draw.rounded_rectangle((x,y,x+w,y+h),radius=10,fill='white',outline='#b8c7d8',width=2)
        draw.rectangle((x,y+8,x+w,y+43),fill=color);draw.text((x+14,y+10),table,fill='white',font=font(20))
        text=[]
        for index,c in enumerate(cols[table]):
            flags=[{'PRI':'PK','UNI':'UQ'}[c['COLUMN_KEY']]] if c['COLUMN_KEY'] in ('PRI','UNI') else []
            if (table,c['COLUMN_NAME']) in fks:flags.append('FK')
            if c['IS_NULLABLE']=='NO':flags.append('NN')
            label=f"{c['COLUMN_NAME']}: {c['COLUMN_TYPE']} {' '.join(flags)}"
            draw.text((x+12,y+50+index*25),label,fill='#25384e',font=font(17))
            text.append(html.escape(label))
        value='<b>'+table+'</b><hr>'+'<br>'.join(text)
        node=ET.SubElement(root,'mxCell',id=table,value=value,vertex='1',parent='1',style='rounded=1;whiteSpace=wrap;html=1;align=left;verticalAlign=top;spacing=10;fillColor=#ffffff;strokeColor=#94a3b8;fontSize=14;')
        ET.SubElement(node,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),attrib={'as':'geometry'})
    name='ENTREGA4_MODELO_RELACIONAL'
    ET.ElementTree(mx).write(DIAGRAMS/(name+'.drawio'),encoding='utf-8',xml_declaration=True)
    image.save(DIAGRAMS/(name+'.png'))
    original=Image.open(DIAGRAMS/'comercialchen3.drawio.png').convert('RGB')
    original.save(DIAGRAMS/'ENTREGA4_DIAGRAMAS.pdf',save_all=True,append_images=[image],resolution=120)
    print('Diccionario:',len(tables),'tablas · Chen editable recuperado · Modelo relacional PNG, PDF y editable generados.')


if __name__=='__main__':main()
