# 🎓 Vouchers de Formación Capital Humano - Argentina Scraper & Dataset

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Data](https://img.shields.io/badge/Status-Base%20de%20Datos%20Completa-orange)

Herramienta automatizada de scraping y dataset completo descargado del portal oficial de **Vouchers de Formación** del Ministerio de Capital Humano Argentina (`formando.capitalhumano.gob.ar`).

---

## 📁 Archivos Disponibles en este Repositorio

* 📄 **`EXPLICACION.md`**: Explicación técnica detallada sobre la ingeniería inversa de las APIs (`admin-ajax.php`, `SISOC` y `Portal Empleo`), estructura de endpoints, diccionarios de datos y arquitectura.
* 📦 **`cursos_argentina_completo.json`**: Base de datos completa en formato JSON con los **5.153+ cursos** de toda la República Argentina, enriquecida con sedes, municipios, provincias, instituciones y comisiones.
* 📊 **`cursos_argentina_resumen.json`**: Resumen ligero de la base de datos para filtrados y consultas rápidas.
* 🐍 **`scraper.py`**: Script en Python multihilo de alto rendimiento para volver a extraer o actualizar la base de datos en cualquier momento.

---

## 🚀 Inicio Rápido

Para ejecutar el scraper o actualizar el catálogo:

```bash
# Clonar el repositorio
git clone https://github.com/F4brizi/VouchersGobierno.git
cd VouchersGobierno

# Descargar todos los cursos de Argentina
python scraper.py
```

### ⚙️ Parámetros de Filtrado en `scraper.py`

El script permite consultar todo el país o filtrar por provincia pasando el ID correspondiente:

```python
# Ejemplo en Python o mediante argumentos del script
python scraper.py --provincia 2  # Provincia de Buenos Aires
```

---

## 📊 Resumen de la Base de Datos

| Métrica | Valor |
| :--- | :--- |
| **Total Cursos Nacionales** | **5.153 Cursos** |
| **Centros de Formación / Instituciones** | 350+ CFP y Escuelas Técnicas |
| **Cobertura Geográfica** | 24 Jurisdicciones / Provincias de Argentina |
| **Modalidades** | Presencial, A Distancia, Educación Común, Laboral |

---

## 📝 Licencia

Este proyecto se comparte con fines educativos y de transparencia de información pública.
