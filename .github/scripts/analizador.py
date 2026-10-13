import os
import json
import subprocess
import html as html_mod
from datetime import datetime

def cargar_datos_evento():
    event_path = os.getenv('GITHUB_EVENT_PATH')
    if event_path and os.path.exists(event_path):
        with open(event_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def obtener_info_git_completa():
    try:
        formato_git = "%h|%an|%ae|%ad|%s"
        resultado = subprocess.run(
            ['git', 'log', '-n', '15', f'--pretty=format:{formato_git}'],
            capture_output=True, text=True, check=True
        )
        commits = []
        for linea in resultado.stdout.strip().split('\n'):
            if not linea:
                continue
            partes = linea.split('|', 4)
            if len(partes) == 5:
                commits.append({
                    'hash': partes[0],
                    'author': partes[1],
                    'email': partes[2],
                    'date': partes[3],
                    'message': partes[4]
                })
        return commits
    except Exception as e:
        return []

def obtener_archivos_y_diff():
    try:
        resultado_archivos = subprocess.run(
            ['git', 'ls-files'],
            capture_output=True, text=True, check=True
        )
        archivos = [linea.strip() for linea in resultado_archivos.stdout.strip().split('\n') if linea.strip()]
        
        resultado_diff = subprocess.run(
            ['git', 'diff', 'HEAD~1', 'HEAD'],
            capture_output=True, text=True
        )
        diff_texto = resultado_diff.stdout if resultado_diff.returncode == 0 else "No hay diff disponible."

        resultado_mod = subprocess.run(
            ['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD'],
            capture_output=True, text=True
        )
        modificados = [l.strip() for l in resultado_mod.stdout.strip().split('\n') if l.strip()]
        archivo_principal = modificados[0] if modificados else "cambios.diff"

        return archivos, archivo_principal, diff_texto
    except Exception as e:
        return [], "cambios.diff", f"Error: {str(e)}"

def analizar_y_generar_conventional_commit(archivo, diff_texto):
    archivo_lower = archivo.lower()
    diff_lower = diff_texto.lower()
    
    if 'style' in diff_lower or 'css' in diff_lower or 'color' in diff_lower:
        tipo, alcance, desc = "style", "ui", "update styling and layout design"
    elif 'fix' in diff_lower or 'error' in diff_lower or 'bug' in diff_lower:
        tipo, alcance, desc = "fix", "core", "resolve minor bug or syntax issue"
    elif 'workflow' in diff_lower or 'actions' in archivo_lower:
        tipo, alcance, desc = "ci", "actions", "update CI/CD pipeline workflow configuration"
    elif 'analizador.py' in archivo_lower or 'html' in archivo_lower:
        tipo, alcance, desc = "refactor", "report", "refactor script analytics and HTML layout generation"
    else:
        tipo, alcance, desc = "feat", "app", "update codebase features and components"

    commit_sugerido = f"{tipo}({alcance}): {desc}"
    agregadas = sum(1 for l in diff_texto.split('\n') if l.startswith('+') and not l.startswith('+++'))
    eliminadas = sum(1 for l in diff_texto.split('\n') if l.startswith('-') and not l.startswith('---'))
    
    descripcion_cambios = (
        f"Se han modificado componentes clave en el archivo <code>{archivo}</code>. "
        f"El análisis detectó un total de <b>{agregadas} líneas añadidas</b> y <b>{eliminadas} líneas eliminadas</b>."
    )

    cuerpo_generado = (
        "* Actualiza los componentes y la estructura del proyecto en el workspace.\n"
        "* Optimiza la presentación visual y el flujo automatizado de reportes."
    )

    texto_para_copiar = f"{commit_sugerido}\n\n{cuerpo_generado}"

    return commit_sugerido, cuerpo_generado, descripcion_cambios, agregadas, eliminadas, texto_para_copiar

def colorear_sintaxis_codely(linea):
    linea_escaped = html_mod.escape(linea)
    prefijo = ""
    if linea_escaped.startswith('+'):
        prefijo = "+"
        linea_escaped = linea_escaped[1:]
    elif linea_escaped.startswith('-'):
        prefijo = "-"
        linea_escaped = linea_escaped[1:]

    if linea_escaped.strip().startswith('#') or linea_escaped.strip().startswith('"""'):
        linea_formateada = f'<span class="tok-comment">{linea_escaped}</span>'
    else:
        palabras_clave = ['def ', 'import ', 'return ', 'class ', 'try:', 'except', 'for ', 'in ', 'if ', 'with ', 'as ']
        reemplazado = linea_escaped
        for kw in palabras_clave:
            reemplazado = reemplazado.replace(kw, f'<span class="tok-keyword">{kw}</span>')
        
        reemplazado = reemplazado.replace('os.', '<span class="tok-variable">os</span>.')
        reemplazado = reemplazado.replace('subprocess.', '<span class="tok-variable">subprocess</span>.')
        linea_formateada = reemplazado

    return prefijo, linea_formateada

def generar_html(event_data):
    full_repo = os.getenv('GITHUB_REPOSITORY', 'aabadmo4/project_report')
    org_owner, repo_name = full_repo.split('/') if '/' in full_repo else ("Desconocido", full_repo)
    actor = os.getenv('GITHUB_ACTOR', 'Desconocido')
    fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    historial_commits = obtener_info_git_completa()
    commit_actual = historial_commits[0] if historial_commits else {'hash': 'N/A', 'author': actor, 'email': 'N/A', 'date': fecha_actual, 'message': 'Sin commits'}
    
    mensaje_original = commit_actual['message']
    repo_url = f"https://github.com/{full_repo}"

    changelog_html = "".join([
        f'<tr class="changelog-row"><td><a href="{repo_url}/commit/{c["hash"]}" target="_blank" class="hash-link"><code>{c["hash"]}</code></a></td><td class="msg-cell"><b>{c["message"]}</b></td><td class="author-cell">{c["author"]}</td><td style="font-size: 11px; color: #858585;">{c["date"]}</td></tr>'
        for c in historial_commits
    ])

    lista_archivos, archivo_principal, diff_contenido = obtener_archivos_y_diff()
    commit_sugerido, cuerpo_generado, descripcion_cambios, agregadas, elimin
    
