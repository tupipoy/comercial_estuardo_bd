"""Audita estructura y patrones de secretos sin imprimir valores encontrados."""
import json
import ast
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

ROOT=Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT)


def main():
    patterns={
        'token_github':re.compile(rb'gh[pousr]_[A-Za-z0-9_]{25,}'),
        'clave_privada':re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----\s*\n'),
        'clave_aws':re.compile(rb'AKIA[A-Z0-9]{16}'),
        'conexion_mysql_literal':re.compile(rb'mysql://[^\s:@{}]+:[^\s@{}]+@[A-Za-z0-9.-]+:\d+'),
    }
    findings=[]
    def inspect(data,location):
        for name,pattern in patterns.items():
            if pattern.search(data):findings.append({'ubicacion':location,'patron':name})
    paths=git('ls-files','--cached','--others','--exclude-standard').decode().splitlines()
    checked=0
    for name in paths:
        p=ROOT/name
        if p.is_file() and p.suffix.lower() in ('.py','.md','.sql','.yml','.yaml','.txt','.example'):
            inspect(p.read_bytes(),'archivo:'+name);checked+=1
    objects=git('rev-list','--objects','--all').decode().splitlines()
    history=0
    for line in objects:
        parts=line.split(' ',1)
        if len(parts)!=2:continue
        oid,name=parts
        if Path(name).suffix.lower() not in ('.py','.md','.sql','.yml','.yaml','.txt','.example') and Path(name).name!='.env':continue
        kind=git('cat-file','-t',oid).strip()
        if kind!=b'blob':continue
        inspect(git('cat-file','blob',oid),'historial:'+oid+':'+name);history+=1
    required=['README.md','INSTALL.md','.gitignore','.env.example','docs/entrega-1','docs/entrega-2','docs/entrega-3','docs/entrega-4','docs/diagramas','docs/certificaciones','docs/bitacora-ia','docs/casos-prueba','sql/ddl','sql/dml','sql/views','sql/triggers','sql/procedures','sql/security','web']
    result={'fecha_utc':datetime.now(timezone.utc).isoformat(),'estructura':{p:(ROOT/p).exists() for p in required},
            'archivos_texto_inspeccionados':checked,'objetos_historicos_inspeccionados':history,'patrones_sensibles_encontrados':findings,
            'alcance':'Revisión automática de patrones conocidos; no equivale a una garantía absoluta de ausencia de secretos.',
            'participacion':git('shortlog','-sne','--all').decode().splitlines()}
    result['sql_sin_encabezado']=[]
    result['fk_sin_acciones_explicitas']=[]
    for p in (ROOT/'sql').rglob('*.sql'):
        sql=p.read_text()
        if not all(field in sql[:1000] for field in ('Archivo:','Autor:','Descripción:','Dependencias:')):result['sql_sin_encabezado'].append(str(p.relative_to(ROOT)))
        for match in re.finditer(r'REFERENCES\s+\w+\s*\([^\)]+\)((?:\s+ON\s+(?:DELETE|UPDATE)\s+(?:CASCADE|RESTRICT|NO ACTION|SET NULL))*)',sql,re.I):
            if not all(re.search(r'ON\s+'+action,match.group(1),re.I) for action in ('DELETE','UPDATE')):result['fk_sin_acciones_explicitas'].append(str(p.relative_to(ROOT)))
    result['funciones_bd_sin_docstring']=[]
    for p in (ROOT/'web').glob('*.py'):
        for node in ast.walk(ast.parse(p.read_text())):
            if isinstance(node,ast.FunctionDef) and not ast.get_docstring(node) and any(isinstance(c,ast.Call) and ((isinstance(c.func,ast.Attribute) and c.func.attr in ('execute','callproc','executemany')) or (isinstance(c.func,ast.Name) and c.func.id=='get_db_connection')) for c in ast.walk(node)):
                result['funciones_bd_sin_docstring'].append(f'{p.relative_to(ROOT)}:{node.name}')
    result['enlaces_locales_rotos']=[]
    for p in [ROOT/'README.md',ROOT/'INSTALL.md',*(ROOT/'docs').rglob('*.md')]:
        for target in re.findall(r'\]\(([^\s)]+)(?:\s+[^)]*)?\)',p.read_text()):
            if target.startswith(('http://','https://','mailto:','#','/')):continue
            target=unquote(target.split('#')[0])
            if target and not (p.parent/target).exists():result['enlaces_locales_rotos'].append(f'{p.relative_to(ROOT)}:{target}')
    out=ROOT/'docs/entrega-4/evidencias/AUDITORIA_REPOSITORIO.json'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('Estructura:',all(result['estructura'].values()),'· patrones sensibles:',len(findings),'· textos:',checked,'· objetos históricos:',history)
    if findings or any(result[key] for key in ('sql_sin_encabezado','fk_sin_acciones_explicitas','funciones_bd_sin_docstring','enlaces_locales_rotos')):
        raise SystemExit('Revisar ubicaciones en el informe; no se imprimieron valores sensibles.')


if __name__=='__main__':main()
