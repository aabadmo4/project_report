# ⚡ Workspace Dashboard & Auto-Documenter

Un panel de control interactivo para CI/CD y automatización de repositorios impulsado por **Python 3.11** y **GitHub Actions**. Analiza de forma inteligente la actividad del repositorio, genera sugerencias bajo el estándar de *Conventional Commits* y normaliza automáticamente el historial de commits del servidor.

---

## 🚀 Características Principales

* **📊 Workspace Dashboard Visual**: Una interfaz web moderna e interactiva desplegada automáticamente a través de **GitHub Pages**, con un diseño inspirado en entornos de desarrollo avanzados (estilo oscuro).
* **🤖 Análisis Inteligente de Diff**: El script en Python (`analizador.py`) examina los cambios del último commit (archivos modificados y líneas de código añadidas/eliminadas) para clasificar y redactar de forma contextual los mensajes de commit.
* **✍️ Automatización de `git commit --amend`**: Modifica y normaliza de forma autónoma el último commit en el servidor remoto aplicando Conventional Commits y manteniendo la limpieza del historial.
* **💻 Visor de Código Integrado**: Explora la estructura de archivos del proyecto y visualiza las diferencias de código (*diffs*) con resaltado de sintaxis directamente en el navegador.
* **📜 Changelog Dinámico y Buscador**: Tabla integrada con el historial reciente de commits y un filtro en tiempo real por autor, hash o mensaje.

---

## 🛠️ Stack Tecnológico

* **Lenguaje**: Python 3.11
* **Automatización**: GitHub Actions (`contents: write`, `pages: write`)
* **Despliegue**: GitHub Pages / `actions/upload-pages-artifact`
* **Frontend**: HTML5 / CSS3 personalizado (Variables CSS, diseño responsivo, tipografía Consolas)

---

## ⚙️ Funcionamiento del Pipeline

1. **Checkout & Git Config**: El flujo de GitHub Actions clona el repositorio con profundidad completa (`fetch-depth: 0`) y configura la identidad del agente automatizado.
2. **Análisis y Generación**: El script de Python `analizador.py` recopila el log de git, analiza el diff de los archivos modificados y genera el archivo `index.html` optimizado para la raíz del sitio.
3. **Modificación Remota (Amend)**: Si el commit actual no cumple con el formato estándar, el script ejecuta localmente `git commit --amend` y actualiza la rama remota mediante `git push --force`.
4. **Despliegue Continuo**: El artefacto generado se empaqueta y se publica instantáneamente en **GitHub Pages**.

---

## 📂 Estructura del Proyecto

```text
project_report/
├── .github/
│   ├── scripts/
│   │   ├── analizador.py       # Script principal de análisis y automatización Git
│   │   └── template.html       # Plantilla HTML del dashboard visual
│   └── workflows/
│       └── generar-reporte.yml # Workflow de CI/CD y despliegue en Pages
├── index.html                  # Dashboard generado automáticamente (Raíz)
└── README.md                   # Documentación del proyecto
