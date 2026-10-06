# 📚 Explicación Técnica: Scraping y API de Formando Capital Humano (Vouchers)

Este documento detalla la arquitectura de funcionamiento interno de la plataforma [Formando Capital Humano - Vouchers](https://formando.capitalhumano.gob.ar/VOUCHERS/), el análisis de la API de comunicación utilizada por el sitio web, la estructura de la base de datos descargada y cómo ejecutar el scraper automatizado.

---

## 🔍 1. Arquitectura y Análisis de la Plataforma Web

La página web de Vouchers opera como una Single Page Application (SPA) montada sobre WordPress con Elementor y un plugin nativo propio llamado `voucher-cursos-fch-r`.

A diferencia de sitios estáticos, la grilla de cursos **no se renderiza en el servidor (SSR)**, sino que la interfaz realiza llamadas dinámicas a través del cliente mediante JavaScript (`vch-main.js` y `vch-api.js`).

### 🛠️ Endpoints y Mecanismo de Fetching

El sistema consulta dos fuentes principales de datos:

1. **API SISOC (Sistema de Información Social / Cursos)**:
   * **Mecanismo**: Realiza consultas mediante un proxy de WordPress (`admin-ajax.php`) para interactuar de forma segura con los servidores backend de SISOC.
   * **URL Base**: `https://formando.capitalhumano.gob.ar/wp-admin/admin-ajax.php`
   * **Acción AJAX**: `vch_api_proxy`
   * **Endpoint Proxy**: `vat/cursos/buscar/`
   * **Parámetros GET**:
     * `action`: `vch_api_proxy`
     * `nonce`: Token CSRF dinámico inyectado en el HTML (`vchConfig.nonce`).
     * `endpoint`: `vat/cursos/buscar/`
     * `provincia_id`: ID numérico de la provincia (opcional, ej. `2` para Buenos Aires, `1` para CABA, omitir para todo el país).
     * `page`: Número de página (ej. `1`, `2`, ...).
     * `page_size`: Cantidad de resultados por página (hasta `100` elementos por consulta).
     * `nuevos`: `false` / `true`

2. **API REST de Portal Empleo**:
   * **URL Base**: `https://formando.capitalhumano.gob.ar/wp-json/vouchers/v1/portal-empleo`
   * **Parámetros GET**: `limit`, `offset`, `provincia_id`, `s` (búsqueda).

---

## 💾 2. Estructura del Dataset Completado (`cursos_argentina_completo.json`)

El archivo JSON generado contiene la base de datos de cursos a nivel nacional. Cada objeto del arreglo posee la siguiente estructura normalizada:

```json
{
  "id": "SISOC-31827",
  "fuente": "SISOC",
  "id_original": 31827,
  "nombre": "Instalador y Administrador de Redes Informaticas",
  "institucion": "Centro De Formación Profesional (C.F.P.) Nº 401",
  "plan_estudio": "Instalación, Administración y Mantenimiento de Redes Informáticas",
  "modalidad": "Educación Común",
  "provincias": ["Buenos Aires"],
  "municipios": ["La Plata", "Avellaneda"],
  "comisiones_count": 2,
  "inscripcion_libre": true,
  "usa_voucher": false,
  "tipo": ["inet"],
  "comisiones": [
    {
      "id": 34748,
      "lugar": "Sede Principal CFP N° 401",
      "direccion": "Calle 41 N° 825",
      "municipio": "La Plata",
      "provincia": "Buenos Aires",
      "cupo": 25
    }
  ],
  "raw_data": { ... }
}
```

### 📋 Campos Principales
* `id`: Identificador único (prefijo `SISOC-` o `PE-`).
* `nombre`: Nombre oficial del curso.
* `institucion`: Centro de Formación Profesional (CFP), Escuela Técnica u organismo dictante.
* `plan_estudio`: Nombre de la certificación o nomenclatura educativa oficial.
* `modalidad`: Modalidad de cursada (Presencial, A distancia, Educación Común, etc.).
* `provincias`: Lista de provincias donde se dictan las comisiones activas.
* `municipios`: Lista de municipios o localidades de las sedes.
* `comisiones`: Detalle de comisiones abiertas, vacantes y ubicaciones.

---

## 🚀 3. Instrucciones de Uso del Scraper (`scraper.py`)

### Requisitos Previos
* Python 3.8 o superior.
* Sin dependencias externas pesadas (utiliza librerías estándar de Python: `urllib`, `json`, `concurrent.futures`).

### Ejecución Directa

```bash
# Descargar todos los cursos de Argentina
python scraper.py

# Filtrar por una provincia específica (ejemplo: provincia_id=2 para Buenos Aires)
python scraper.py --provincia 2
```

El script extrae dinámicamente el `nonce` de sesión activo, realiza solicitudes concurrentes en paralelo para máxima velocidad y genera los archivos `cursos_argentina_completo.json` y `cursos_argentina_resumen.json`.

---

## 📊 4. Estadísticas del Catálogo Nacional

* **Total de Cursos Registrados**: **5.153 ofertas de formación**.
* **Distribución Geográfica**:
  * Provincia de Buenos Aires: ~4.153 cursos.
  * Ciudad Autónoma de Buenos Aires y resto de las provincias: ~1.000 cursos.
* **Sectores de Mayor Oferta**:
  * Oficios Industriales y Mecánica: ~34%
  * Gestión, Contabilidad y Administración: ~21%
  * Electrónica, Robótica y Automatización: ~17%
  * Programación, Software y Redes: ~9%
  * Salud y Servicios Generales: ~19%
