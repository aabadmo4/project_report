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

def obtener_cambios_git():
    try:
        resultado_archivos = subprocess.run(
            ['git', 'diff-tree', '--no-commit-id', '--name-status', '-r', 'HEAD'],
            capture_output=True, text=True, check=True
        )
        
        cambios_archivos = []
        archivo_principal = "archivo.py"
        for linea in resultado_archivos.stdout.strip().split('\n'):
            if not linea:
                continue
            partes = linea.split('\t')
            if len(partes) >= 2:
                cambios_archivos.append((partes[0], partes[1]))
                archivo_principal = partes[1] # Tomamos el primer archivo modificado para la pestaña

        resultado_diff = subprocess.run(
            ['git', 'diff', 'HEAD~1', 'HEAD'],
            capture_output=True, text=True
        )
        diff_texto = resultado_diff.stdout if resultado_diff.returncode == 0 else "No hay diff disponible."
        return cambios_archivos, diff_texto, archivo_principal
    except Exception as e:
        return [], f"Error obteniendo diff: {str(e)}", "analizador.py"

def generar_html(event_data):
    full_repo = os.getenv('GITHUB_REPOSITORY', 'usuario/repositorio')
    if '/' in full_repo:
        org_owner, repo_name = full_repo.split('/', 1)
    else:
        org_owner, repo_name = "Desconocido", full_repo

    actor = os.getenv('GITHUB_ACTOR', 'Desconocido')
    evento_tipo = os.getenv('GITHUB_EVENT_NAME', 'push')
    fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    historial_commits = obtener_info_git_completa()
    commit_actual = historial_commits[0] if historial_commits else {
        'hash': 'N/A', 'author': actor, 'email': 'N/A', 'date': fecha_actual, 'message': 'Sin commits recientes'
    }

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

    archivos_git, diff_git, archivo_principal = obtener_cambios_git()
    
    diff_html = ""
    if archivos_git:
        diff_html += "<div class='file-list' style='margin-bottom: 12px;'>"
        for estado, archivo in archivos_git:
            clase = "added" if estado == 'A' else ("removed" if estado == 'D' else "modified")
            diff_html += f"<span class='file-badge {clase}'><b>[{estado}]</b> {archivo}</span> "
        diff_html += "</div>"

    # Construir el editor simulando VS Code Web con números de línea
    editor_linhas = ""
    line_num = 1
    for linea_diff in diff_git.split('\n'):
        if linea_diff.startswith('+++') or linea_diff.startswith('---') or linea_diff.startswith('index') or linea_diff.startswith('diff --git'):
            continue # Omitir cabeceras feas de git para dejarlo limpio como un editor
            
        clase_linea = ""
        if linea_diff.startswith('+'):
            clase_linea = "vscode-line-added"
        elif linea_diff.startswith('-'):
            clase_linea = "vscode-line-removed"
        elif linea_diff.startswith('@@'):
            clase_linea = "vscode-line-chunk"

        # Escapar caracteres HTML básicos para evitar roturas
        linea_escaped = linea_diff.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        editor_linhas += f"""<div class="vscode-row {clase_linea}">
            <span class="vscode-linenr">{line_num}</span>
            <span class="vscode-code-text">{linea_escaped}</span>
        </div>"""
        line_num += 1

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
        pr_html = f"<p style='color: #586069;'>Este reporte se generó por un evento de tipo <b>{evento_tipo}</b>.</p>"

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>VS Code Web View - {repo_name}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.5; color: #24292e; max-width: 1050px; margin: 30px auto; padding: 0 20px; background: #f0f2f5; }}
        h1, h2, h3 {{ color: #24292e; border-bottom: 1px solid #eaecef; padding-bottom: .3em; }}
        .card {{ background: #fff; border: 1px solid #e1e4e8; border-radius: 6px; padding: 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px; margin-bottom: 20px; }}
        .metric-box {{ background: #ffffff; border: 1px solid #e1e4e8; border-radius: 6px; padding: 15px; box-shadow: 0 1px 2px rgba(0,0,0,0.02); }}
        .metric-box h3 {{ margin: 0 0 8px 0; font-size: 12px; color: #0366d6; border: none; text-transform: uppercase; letter-spacing: 0.5px; }}
        .metric-box p {{ margin: 0; font-size: 15px; font-weight: bold; color: #24292e; word-break: break-all; }}
        
        table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
        th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid #eaecef; }}
        th {{ background-color: #f6f8fa; color: #586069; }}
        tr:hover {{ background-color: #f8f9fa; }}

        .file-badge {{ display: inline-block; padding: 4px 8px; font-family: monospace; font-size: 12px; border-radius: 4px; margin-right: 5px; }}
        .file-badge.added {{ background-color: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }}
        .file-badge.modified {{ background-color: #eff6ff; color: #1e40af; border-1px solid #bfdbfe; }}
        .file-badge.removed {{ background-color: #fef2f2; color: #991b1b; border-1px solid #fecaca; }}

        /* Estética VS Code Web */
        .vscode-container {{ background-color: #1e1e1e; border-radius: 8px; overflow: hidden; box-shadow: 0 6px 16px rgba(0,0,0,0.25); border: 1px solid #333; margin-top: 10px; }}
        .vscode-titlebar {{ background-color: #323233; color: #cccccc; padding: 10px 15px; font-size: 13px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #252526; }}
        .vscode-dots {{ display: flex; gap: 6px; }}
        .vscode-dot {{ width: 10px; height: 10px; border-radius: 50%; }}
        .dot-red {{ background-color: #ff5f56; }}
        .dot-yellow {{ background-color: #ffbd2e; }}
        .dot-green {{ background-color: #27c93f; }}
        
        .vscode-tab {{ background-color: #1e1e1e; color: #ffffff; padding: 6px 14px; font-size: 12px; display: inline-flex; align-items: center; gap: 6px; border-top: 2px solid #007acc; border-right: 1px solid #2d2d2d; font-family: Consolas, monospace; }}
        
        .vscode-editor {{ background-color: #1e1e1e; color: #d4d4d4; font-family: Consolas, "Courier New", monospace; font-size: 12px; overflow-x: auto; padding: 10px 0; }}
        .vscode-row {{ display: flex; width: 100%; line-height: 20px; }}
        .vscode-linenr {{ width: 45px; color: #858585; text-align: right; padding-right: 15px; user-select: none; font-size: 11px; }}
        .vscode-code-text {{ white-space: pre; flex: 1; }}
        
        .vscode-line-added {{ background-color: rgba(46, 160, 67, 0.15); }}
        .vscode-line-added .vscode-code-text {{ color: #7ee787; }}
        .vscode-line-removed {{ background-color: rgba(248, 81, 73, 0.15); }}
        .vscode-line-removed .vscode-code-text {{ color: #ffa198; }}
        .vscode-line-chunk {{ color: #569cd6; font-weight: bold; background-color: rgba(86, 156, 214, 0.1); }}

        footer {{ text-align: center; font-size: 12px; color: #586069; margin-top: 40px; }}
    </style>
</head>
<body>
    <h1>⚡ Code Studio & Changelog</h1>
    <p>Pipeline ejecutado el <b>{fecha_actual}</b></p>

    <div class="metrics-grid">
        <div class="metric-box">
            <h3>Organización</h3>
            <p>🏢 {org_owner}</p>
        </div>
        <div class="metric-box">
            <h3>Repositorio</h3>
            <p>📦 {repo_name}</p>
        </div>
        <div class="metric-box">
            <h3>Autor</h3>
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
        <h2>📜 Historial de Commits (Changelog)</h2>
        <table>
            <thead>
                <tr>
                    <th>Hash</th>
                    <th>Mensaje</th>
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
        <h2>💻 Visor de Código (Estética VS Code Web)</h2>
        {diff_html}
        
        <div class="vscode-container">
            <div class="vscode-titlebar">
                <div class="vscode-dots">
                    <div class="vscode-dot dot-red"></div>
                    <div class="vscode-dot dot-yellow"></div>
                    <div class="vscode-dot dot-green"></div>
                </div>
                <span>{repo_name} - Visual Studio Code (Solo Lectura)</span>
                <span style="font-size: 11px; color: #858585;">UTF-8 | Python</span>
            </div>
            <div style="background-color: #2d2d2d; padding-left: 10px;">
                <div class="vscode-tab">📄 {archivo_principal}</div>
            </div>
            <div class="vscode-editor">
                {editor_linhas}
            </div>
        </div>
    </div>

    <div class="card">
        <h2>🔍 Detalles del Evento</h2>
        {pr_html}
    </div>

    <footer>
        <p>Generado automáticamente con Python y GitHub Actions.</p>
    </footer>
</body>
</html>
"""

    os.makedirs('public', exist_ok=True)
    with open('public/index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("¡Página con estética VS Code Web generada con éxito!")

if __name__ == '__main__':
    datos = cargar_datos_evento()
    generar_html(datos)
    
