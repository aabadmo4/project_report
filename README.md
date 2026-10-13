# ⚡ Proyect Report & Workspace Dashboard

![Estado de GitHub Actions](https://github.com/aabadmo4/proyect_report/actions/workflows/generar-reporte.yml/badge.svg)

> Pipeline automatizado con Python y GitHub Actions que genera un dashboard interactivo al estilo **CodelyTV / VS Code** para visualizar la actividad del repositorio, diffs de código, sugerencias estructuradas de Conventional Commits y un changelog detallado en GitHub Pages.

---

## 🚀 Características Principales

* **🤖 Sugerencia Inteligente de Commits**: Analiza automáticamente los cambios del último diff para proponer un título bajo el estándar de **Conventional Commits** (`feat`, `fix`, `refactor`, `style`, `ci`), acompañado de un cuerpo y pie estructurados.
* **💻 Visor de Código Estilo VS Code**: Interfaz oscura personalizada con barra lateral de explorador, pestañas y resaltado de sintaxis dinámico para inspeccionar los archivos modificados.
* **📜 Changelog Reciente**: Tabla limpia y moderna con el historial de los últimos commits de la rama (hash, mensaje, autor y fecha).
* **📊 Métricas Clave del Workspace**: Tarjetas informativas con detalles de la organización, repositorio, autor y último commit realizado.
* **🔄 Automatización CI/CD**: Despliegue continuo integrado mediante GitHub Actions y publicado de forma automática en **GitHub Pages**.

---

## 🛠️ Stack Tecnológico

* **Python 3.11+**: Motor principal para la interacción con la CLI de Git, análisis de diffs y generación del HTML.
* **GitHub Actions**: Orquestador del pipeline de compilación y despliegue.
* **HTML5 / CSS3 (Tema CodelyTV)**: Diseño minimalista, oscuro y optimizado para desarrolladores.

---

## 📂 Estructura del Proyecto

```text
proyect_report/
├── .github/
│   ├── scripts/
│   │   └── analizador.py      # Script principal que procesa Git y genera el HTML
│   └── workflows/
│       └── generar-reporte.yml # Definición del pipeline de GitHub Actions
└── README.md                  # Documentación del proyecto
