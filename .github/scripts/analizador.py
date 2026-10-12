os = __import__('os')
json = __import__('json')
subprocess = __import__('subprocess')
from datetime import datetime

def cargar_datos_evento():
    event_path = os.getenv('GITHUB_EVENT_PATH')
    if event_path and os.path.exists(event_path):
        with open(event_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def obtener_info_git_completa():
    """Extrae el historial de commits recientes usando git log para un changelog en condiciones"""
    try:
        # Formato: HASH | AUTOR | EMAIL | FECHA | MENSAJE
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

def obtener_cambios_git():
    try:
        resultado_archivos = subprocess.run(
            ['git', 'diff-tree', '--no-commit-id', '--name-status', '-r', 'HEAD'],
            capture_output=True, text=True, check=True
        )
        
        cambios_archivos = []
        for linea in resultado_archivos.stdout.strip().split('\n'):
            if not linea:
                continue
            partes = linea.split('\t')
            if len(partes) >= 2:
                cambios_archivos.append((partes[0], partes[1]))

        resultado_diff = subprocess.run(
            ['git', 'diff', 'HEAD~1', 'HEAD'],
            capture_output=True, text=True
        )
        diff_texto = resultado_diff.stdout if resultado_diff.returncode == 0 else "No hay diff disponible."
        return cambios_archivos, diff_texto
    except Exception as e:
        return [], f"Error obteniendo diff: {str(e)}"

def generar_html(event_data):
    # Variables de entorno de GitHub Actions
    full_repo = os.getenv('GITHUB_REPOSITORY', 'usuario/repositorio') # ej: aabadmo4/proyect_report
    if '/' in full_repo:
        org_owner, repo_name = full_repo.split('/', 1)
    else:
        org_owner, repo_name = "Desconocido", full_repo

    actor = os.getenv('GITHUB_ACTOR', 'Desconocido')
    evento_tipo = os.getenv('GITHUB_EVENT_NAME', 'push')
    fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Obtener historial de commits con git log
    historial_commits = obtener_info_git_completa()
    
    # Commit actual (el primero de la lista)
    commit_actual = historial_commits[0] if historial_commits else {
        'hash': 'N/A', 'author': actor, 'email': 'N/A', 'date': fecha_actual, 'message': 'Sin commits recientes'
    }

    # Generar HTML del Changelog completo
    changelog_html = ""
    for c in historial_commits:
        changelog_html += f"""
        <tr>
            <td><code>{c['hash']}</code></td>
            <td><b>{c['message']}</b></td>
            <td>{c['author']}</td>
            <td style="font-size: 11px; color: #586069;">{c['date']}</td>
        </tr>
        """

    # Obtener cambios y diff
    archivos_git, diff_git = obtener_cambios_git()
    
    diff_html = ""
    if archivos_git:
        diff_html += "<div class='file-list'>"
        for estado, archivo in archivos_git:
            clase = "added" if estado == 'A' else ("removed" if estado == 'D' else "modified")
            diff_html += f"<div class='file-change {clase}'><b>[{estado}]</b> {archivo}</div>"
        diff_html += "</div>"
    
    diff_html += f"<pre class='code-diff'>"
    for linea_diff in diff_git.split('\n'):
        if linea_diff.startswith('+') and not linea_diff.startswith('+++'):
            diff_html += f"<span class='line-added'>{linea_diff}</span>\n"
        elif linea_diff.startswith('-') and not linea_diff.startswith('---'):
            diff_html += f"<span class='line-removed'>{linea_diff}</span>\n"
        elif linea_diff.startswith('@@'):
            diff_html += f"<span class='line-chunk'>{linea_diff}</span>\n"
        else:
            diff_html += f"{linea_diff}\n"
    diff_html += "</pre>"

    # Pull Request info si existe
    pull_request = event_data.get('pull_request', {})
    pr_html = ""
    if pull_request:
        pr_html = f"""
        <div class="card">
            <h3>Pull Request: {pull_request.get('title')}</h3>
            <p><b>Autor:</b> {pull_request.get('user', {}).get('login')}</p>
            <pre>{pull_request.get('body', 'Sin descripción')}</pre>
        </div>
        """
    else:
        pr_html = "<p style='color: #586069;'>Este reporte se generó por un evento de tipo <b>{0}</b>.</p>".format(evento_tipo)

    # Estructura de la página web con diseño profesional
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Changelog y Panel - {repo_name}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.5; color: #24292e; max-width: 1000px; margin: 30px auto; padding: 0 20px; background: #f6f8fa; }}
        h1, h2, h3 {{ color: #24292e; border-bottom: 1px solid #eaecef; padding-bottom: .3em; }}
        .card {{ background: #fff; border: 1px solid #e1e4e8; border-radius: 6px; padding: 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px; margin-bottom: 20px; }}
        .metric-box {{ background: #f1f8ff; border: 1px solid #c8e1ff; border-radius: 6px; padding: 15px; }}
        .metric-box h3 {{ margin: 0 0 8px 0; font-size: 13px; color: #0366d6; border: none; text-transform: uppercase; }}
        .metric-box p {{ margin: 0; font-size: 16px; font-weight: bold; color: #24292e; word-break: break-all; }}
        
        table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
        th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid #eaecef; }}
        th {{ background-color: #f6f8fa; color: #586069; }}
        tr:hover {{ background-color: #f8f9fa; }}

        .file-change {{ padding: 6px 12px; font-family: monospace; font-size: 13px; margin-bottom: 4px; border-radius: 4px; }}
        .file-change.added {{ background-color: #ecfdf5; color: #065f46; border-left: 4px solid #10b981; }}
        .file-change.modified {{ background-color: #eff6ff; color: #1e40af; border-left: 4px solid #3b82f6; }}
        .file-change.removed {{ background-color: #fef2f2; color: #991b1b; border-left: 4px solid #ef4444; }}

        .code-diff {{ background-color: #1e1e1e; color: #d4d4d4; padding: 15px; border-radius: 6px; font-family: monospace; font-size: 12px; overflow-x: auto; }}
        .line-added {{ background-color: rgba(16, 185, 129, 0.2); color: #34d399; display: block; }}
        .line-removed {{ background-color: rgba(239, 68, 68, 0.2); color: #f87171; display: block; }}
        .line-chunk {{ color: #569cd6; font-weight: bold; display: block; margin-top: 5px; }}

        footer {{ text-align: center; font-size: 12px; color: #586069; margin-top: 40px; }}
    </style>
</head>
<body>
    <h1>🚀 Panel de Control y Changelog</h1>
    <p>Actualizado automáticamente el <b>{fecha_actual}</b></p>

    <div class="metrics-grid">
        <div class="metric-box">
            <h3>Organización / Propietario</h3>
            <p>🏢 {org_owner}</p>
        </div>
        <div class="metric-box">
            <h3>Repositorio</h3>
            <p>📦 {repo_name}</p>
        </div>
        <div class="metric-box">
            <h3>Autor del Cambio</h3>
            <p>👤 {commit_actual['author']}</p>
            <span style="font-size: 11px; color: #586069;">{commit_actual['email']}</span>
        </div>
        <div class="metric-box">
            <h3>Último Commit</h3>
            <p><code>{commit_actual['hash']}</code></p>
            <span style="font-size: 11px; color: #24292e;">{commit_actual['message']}</span>
        </div>
    </div>

    <div class="card">
        <h2>📜 Changelog Completo (Historial Reciente)</h2>
        <table>
            <thead>
                <tr>
                    <th>Hash</th>
                    <th>Mensaje del Commit</th>
                    <th>Autor</th>
                    <th>Fecha</th>
                </tr>
            </thead>
            <tbody>
                {changelog_html}
            </tbody>
        </table>
    </div>

    <div class="card">
        <h2>💻 Visor de Código (Diff del último cambio)</h2>
        {diff_html}
    </div>

    <div class="card">
        <h2>🔍 Información del Evento ({evento_tipo})</h2>
        {pr_html}
    </div>

    <footer>
        <p>Generado por pipeline de Python y GitHub Actions.</p>
    </footer>
</body>
</html>
"""

    os.makedirs('public', exist_ok=True)
    with open('public/index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("¡Changelog y paneles de metadatos generados con éxito!")

if __name__ == '__main__':
    datos = cargar_datos_evento()
    generar_html(datos)
    
