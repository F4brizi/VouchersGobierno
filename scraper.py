#!/usr/bin/env python3
"""
Scraper oficial para Vouchers de Formando Capital Humano Argentina.
Extrae todos los cursos disponibles o los filtra por provincia.
"""

import argparse
import urllib.request
import urllib.parse
import ssl
import json
import re
import time
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def get_nonce():
    url = 'https://formando.capitalhumano.gob.ar/VOUCHERS/'
    req = urllib.request.Request(url, headers=headers)
    html = urllib.request.urlopen(req, context=ctx).read().decode('utf-8', errors='ignore')
    m_nonce = re.search(r'"nonce":"([a-f0-9]+)"', html)
    return m_nonce.group(1) if m_nonce else '120e67e51c'

def fetch_sisoc_page(nonce, page, page_size=100, prov_id=None):
    ajax_url = 'https://formando.capitalhumano.gob.ar/wp-admin/admin-ajax.php'
    params = {
        'action': 'vch_api_proxy',
        'nonce': nonce,
        'endpoint': 'vat/cursos/buscar/',
        'page': str(page),
        'page_size': str(page_size),
        'nuevos': 'false'
    }
    if prov_id:
        params['provincia_id'] = str(prov_id)
        
    query = urllib.parse.urlencode(params)
    full_url = f"{ajax_url}?{query}"
    for attempt in range(3):
        try:
            req = urllib.request.Request(full_url, headers=headers)
            resp = urllib.request.urlopen(req, context=ctx, timeout=25).read().decode('utf-8', errors='ignore')
            data = json.loads(resp)
            if data.get('success') and data.get('data'):
                return data['data']
        except Exception as e:
            time.sleep(1)
    return None

def fetch_pe_page(offset, limit=50, prov_id=None):
    url = f'https://formando.capitalhumano.gob.ar/wp-json/vouchers/v1/portal-empleo?limit={limit}&offset={offset}'
    if prov_id:
        url += f'&provincia_id={prov_id}'
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=headers)
            resp = urllib.request.urlopen(req, context=ctx, timeout=25).read().decode('utf-8', errors='ignore')
            data = json.loads(resp)
            if data.get('success') and data.get('data'):
                return data['data']
        except Exception as e:
            time.sleep(1)
    return None

def main():
    parser = argparse.ArgumentParser(description="Scraper de Vouchers Formando Capital Humano")
    parser.add_argument('--provincia', type=str, default=None, help="ID de provincia (ej: 2 para Buenos Aires, 1 para CABA)")
    parser.add_argument('--output', type=str, default="cursos_argentina_completo.json", help="Archivo de salida JSON")
    args = parser.parse_args()

    prov_msg = f"para provincia_id={args.provincia}" if args.provincia else "para toda Argentina"
    print(f"[+] Extrayendo catálogo de Formando Capital Humano {prov_msg}...")
    
    nonce = get_nonce()
    print(f"[+] Nonce activo: {nonce}")

    # 1. SISOC
    page1 = fetch_sisoc_page(nonce, 1, page_size=100, prov_id=args.provincia)
    total_sisoc = page1.get('count', 0) if page1 else 0
    print(f"[+] SISOC Total Cursos: {total_sisoc}")

    sisoc_courses = []
    if page1 and page1.get('results'):
        sisoc_courses.extend(page1['results'])

    total_pages = (total_sisoc + 99) // 100
    if total_pages > 1:
        print(f"[+] Descargando {total_pages - 1} páginas restantes en paralelo...")
        with ThreadPoolExecutor(max_workers=12) as executor:
            futures = {executor.submit(fetch_sisoc_page, nonce, p, 100, args.provincia): p for p in range(2, total_pages + 1)}
            for future in as_completed(futures):
                res = future.result()
                if res and res.get('results'):
                    sisoc_courses.extend(res['results'])

    print(f"[+] SISOC extracción completa: {len(sisoc_courses)} cursos obetenidos.")

    # 2. Portal Empleo
    pe_page1 = fetch_pe_page(0, limit=50, prov_id=args.provincia)
    total_pe = pe_page1.get('pagination', {}).get('total', 0) if pe_page1 else 0
    print(f"[+] Portal Empleo Total Cursos: {total_pe}")

    pe_courses = []
    if pe_page1 and pe_page1.get('items'):
        pe_courses.extend(pe_page1['items'])

    if total_pe > 50:
        pe_offsets = list(range(50, total_pe, 50))
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {executor.submit(fetch_pe_page, off, 50, args.provincia): off for off in pe_offsets}
            for future in as_completed(futures):
                res = future.result()
                if res and res.get('results'):
                    pe_courses.extend(res['results'])
                elif res and res.get('items'):
                    pe_courses.extend(res['items'])

    print(f"[+] Portal Empleo extracción completa: {len(pe_courses)} cursos obtenidos.")

    # Normalizar Datos
    all_courses = []

    for c in sisoc_courses:
        centro = c.get('centro')
        inst_name = centro.get('nombre') if isinstance(centro, dict) else (c.get('institucion_nombre') or '')
        
        comisiones = c.get('comisiones', [])
        provincias = set()
        municipios = set()
        comision_list = []

        for com in comisiones:
            ub = com.get('ubicacion')
            if isinstance(ub, dict):
                prov = ub.get('provincia_nombre') or ''
                muni = ub.get('municipio_nombre') or ''
                if prov: provincias.add(prov)
                if muni: municipios.add(muni)
                comision_list.append({
                    'id': com.get('id'),
                    'lugar': ub.get('nombre'),
                    'direccion': ub.get('direccion'),
                    'municipio': muni,
                    'provincia': prov,
                    'cupo': com.get('cupo')
                })

        all_courses.append({
            'id': f"SISOC-{c.get('id')}",
            'fuente': 'SISOC',
            'id_original': c.get('id'),
            'nombre': c.get('nombre') or c.get('nombre_curso') or '',
            'institucion': inst_name,
            'plan_estudio': c.get('plan_estudio_nombre') or '',
            'modalidad': c.get('modalidad_nombre') or '',
            'provincias': list(provincias),
            'municipios': list(municipios),
            'comisiones_count': len(comisiones),
            'inscripcion_libre': c.get('inscripcion_libre'),
            'usa_voucher': c.get('usa_voucher'),
            'tipo': c.get('tipo', []),
            'comisiones': comision_list,
            'raw_data': c
        })

    for c in pe_courses:
        all_courses.append({
            'id': f"PE-{c.get('id') or c.get('identificacion_curso')}",
            'fuente': 'Portal Empleo',
            'id_original': c.get('id') or c.get('identificacion_curso'),
            'nombre': c.get('nombre') or c.get('titulo') or c.get('denominacion') or '',
            'institucion': c.get('oferente') or c.get('institucion') or c.get('organismo') or '',
            'plan_estudio': c.get('grupo_tematico') or '',
            'modalidad': c.get('modalidad') or '',
            'provincias': [c.get('provincia')] if c.get('provincia') else [],
            'municipios': [c.get('localidad')] if c.get('localidad') else [],
            'comisiones_count': 1,
            'inscripcion_libre': True,
            'usa_voucher': True,
            'tipo': ['portal_empleo'],
            'comisiones': [],
            'raw_data': c
        })

    print(f"[+] Total Cursos Procesados: {len(all_courses)}")

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(all_courses, f, ensure_ascii=False, indent=2)

    resumen_file = args.output.replace('.json', '_resumen.json') if '.json' in args.output else f"{args.output}_resumen.json"
    resumen = []
    for c in all_courses:
        resumen.append({
            'id': c['id'],
            'fuente': c['fuente'],
            'nombre': c['nombre'],
            'institucion': c['institucion'],
            'plan_estudio': c['plan_estudio'],
            'modalidad': c['modalidad'],
            'provincias': c['provincias'],
            'municipios': c['municipios']
        })

    with open(resumen_file, 'w', encoding='utf-8') as f:
        json.dump(resumen, f, ensure_ascii=False, indent=2)

    print(f"[+] Archivos guardados exitosamente: `{args.output}` y `{resumen_file}`.")

if __name__ == '__main__':
    main()
