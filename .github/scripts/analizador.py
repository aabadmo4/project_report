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
        tipo = "style"
        alcance = "ui"
        descripcion_corta = "update styling and layout design"
    elif 'fix' in diff_lower or 'error' in diff_lower or 'bug' in diff_lower:
        tipo = "fix"
        alcance = "core"
        descripcion_corta = "resolve minor bug or syntax issue"
    elif 'workflow' in diff_lower or 'actions' in archivo_lower:
        tipo = "ci"
        alcance = "actions"
        descripcion_corta = "update CI/CD pipeline workflow configuration"
    elif 'analizador.py' in archivo_lower or 'html' in archivo_lower:
        tipo = "refactor"
        alcance = "report"
        descripcion_corta = "refactor script analytics and HTML layout generation"
    else:
        tipo = "feat"
        alcance = "app"
        descripcion_corta = "update codebase features and components"

    commit_sugerido = f"{tipo}({alcance}): {descripcion_corta}"
    
    lineas_agregadas = sum(1 for l in diff_texto.split('\n') if l.startswith('+') and not l.startswith('+++'))
    lineas_eliminadas = sum(1 for l in diff_texto.split('\n') if l.startswith('-') and not l.startswith('---'))
    
    texto_resumen = (
        f"Se han modificado componentes clave en el archivo <code>{archivo}</code>. "
        f"El análisis detectó un total de <b>{lineas_agregadas} líneas añadidas</b> y <b>{lineas_eliminadas} líneas eliminadas</b>. "
        f"Los ajustes se centran en mejorar la estructura visual, la presentación de datos y la automatización del workspace."
    )

    return commit_sugerido, texto_resumen

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
    full_repo = os.getenv('GITHUB_REPOSITORY', 'usuario/repositorio')
    if '/' in full_repo:
        org_owner, repo_name = full_repo.split('/', 1)
    else:
        org_owner, repo_name = "Desconocido", full_repo

    actor = os.getenv('GITHUB_ACTOR', 'Desconocido')
    fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    historial_commits = obtener_info_git_completa()
    commit_actual = historial_commits[0] if historial_commits else {
        'hash': 'N/A', 'author': actor, 'email': 'N/A', 'date': fecha_actual, 'message': 'Sin commits'
    }

    changelog_html = ""
    for c in historial_commits:
        changelog_html += f"""
        <tr>
            <td><code>{c['hash']}</code></td>
            <td><b>{c['message']}</b></td>
            <td>{c['author']}</td>
            <td style="font-size: 11px; color: #858585;">{c['date']}</td>
        </tr>
        """

    lista_archivos, archivo_principal, diff_contenido = obtener_archivos_y_diff()
    commit_sugerido, descripcion_cambios = analizar_y_generar_conventional_commit(archivo_principal, diff_contenido)

    explorer_html = ""
    for f in lista_archivos[:25]:
        activo_class = "active-file" if f == archivo_principal else ""
        explorer_html += f'<div class="vscode-explorer-item {activo_class}">📄 {f}</div>'

    editor_lineas = ""
    line_num = 1
    for linea in diff_contenido.split('\n'):
        if linea.startswith('+++') or linea.startswith('---') or linea.startswith('index') or linea.startswith('diff --git'):
            continue
            
        clase_linea = ""
        if linea.startswith('+'):
            clase_linea = "line-added"
        elif linea.startswith('-'):
            clase_linea = "line-removed"
        elif linea.startswith('@@'):
            clase_linea = "line-chunk"

        prefijo, codigo_html = colorear_sintaxis_codely(linea)
        
        editor_lineas += f"""<div class="vscode-row {clase_linea}">
            <span class="vscode-linenr">{line_num}</span>
            <span class="vscode-code-text"><span class="diff-prefix">{prefijo}</span>{codigo_html}</span>
        </div>"""
        line_num += 1

    plantilla_html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>{repo_name} - Workspace Dashboard</title>
    <style>
        :root {{
            --codely-bg: #151718;
            --codely-sidebar: #1b1e1f;
            --codely-titlebar: #111314;
            --codely-border: #282c2e;
            --codely-text: #d8dee9;
            --codely-accent: #f38020;
            --codely-keyword: #cc99cc;
            --codely-string: #99cc99;
            --codely-comment: #65737e;
            --codely-variable: #f8c555;
        }}

        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.5; color: var(--codely-text); max-width: 1150px; margin: 20px auto; padding: 0 15px; background: var(--codely-bg); }}
        h1, h2 {{ color: #ffffff; border-bottom: 1px solid var(--codely-border); padding-bottom: .3em; }}
        
        .section-box {{ background: var(--codely-sidebar); border: 1px solid var(--codely-border); border-radius: 6px; padding: 20px; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.4); }}
        
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px; margin-bottom: 25px; }}
        .metric-box {{ background: #1f2324; border: 1px solid var(--codely-border); border-radius: 6px; padding: 15px; }}
        .metric-box h3 {{ margin: 0 0 8px 0; font-size: 11px; color: var(--codely-accent); border: none; text-transform: uppercase; letter-spacing: 1px; }}
        .metric-box p {{ margin: 0; font-size: 15px; font-weight: bold; color: #ffffff; word-break: break-all; }}

        table {{ width: 100%; border-collapse: collapse; font-size: 13px; color: var(--codely-text); }}
        th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid var(--codely-border); }}
        th {{ background-color: #1a1d1e; color: var(--codely-accent); }}
        tr:hover {{ background-color: #222628; }}

        .ai-summary-box {{ background: #1a1d1e; border-left: 4px solid var(--codely-accent); padding: 15px; border-radius: 4px; margin-bottom: 15px; font-size: 14px; }}
        .conventional-tag {{ display: inline-block; background: #282c2e; color: var(--codely-accent); padding: 4px 8px; border-radius: 4px; font-family: Consolas, monospace; font-size: 13px; margin-top: 8px; border: 1px solid #3c4245; }}

        .vscode-window {{ background-color: var(--codely-bg); border-radius: 8px; overflow: hidden; border: 1px solid var(--codely-border); box-shadow: 0 8px 24px rgba(0,0,0,0.6); margin-top: 15px; }}
        .vscode-titlebar {{ background-color: var(--codely-titlebar); color: #cccccc; padding: 10px 15px; font-size: 13px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--codely-border); }}
        .vscode-dots {{ display: flex; gap: 6px; }}
        .vscode-dot {{ width: 12px; height: 12px; border-radius: 50%; }}
        .dot-red {{ background-color: #ff5f56; }}
        .dot-yellow {{ background-color: #ffbd2e; }}
        .dot-green {{ background-color: #27c93f; }}

        .vscode-body {{ display: flex; height: 480px; background-color: var(--codely-bg); }}
        .vscode-sidebar {{ width: 240px; background-color: var(--codely-sidebar); border-right: 1px solid var(--codely-border); overflow-y: auto; font-size: 12px; color: #a0a8b0; }}
        .vscode-sidebar-title {{ padding: 10px 12px; font-weight: bold; font-size: 11px; text-transform: uppercase; color: var(--codely-accent); letter-
    
