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

def obtener_archivos_y_codigo():
    try:
        # Obtener listado de archivos tracked del repo para el explorador lateral
        resultado_archivos = subprocess.run(
            ['git', 'ls-files'],
            capture_output=True, text=True, check=True
        )
        archivos = [linea.strip() for linea in resultado_archivos.stdout.strip().split('\n') if linea.strip()]
        
        # Tomar el primer archivo modificado o por defecto el script
        archivo_principal = ".github/scripts/analizador.py"
        resultado_mod = subprocess.run(
            ['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD'],
            capture_output=True, text=True
        )
        modificados = [l.strip() for l in resultado_mod.stdout.strip().split('\n') if l.strip()]
        if modificados:
            archivo_principal = modificados[0]

        # Leer el contenido completo del archivo principal para mostrarlo en modo editor
        contenido_archivo = "# Archivo no encontrado"
        if os.path.exists(archivo_principal):
            with open(archivo_principal, 'r', encoding='utf-8') as f:
                contenido_archivo = f.read()

        return archivos, archivo_principal, contenido_archivo
    except Exception as e:
        return [], "analizador.py", f"# Error cargando archivos: {str(e)}"

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
            <td style="font-size: 11px; color: #586069;">{c['date']}</td>
        </tr>
        """

    lista_archivos, archivo_principal, contenido_codigo = obtener_archivos_y_codigo()

    # Construir el explorador de archivos lateral estilo VS Code
    explorer_html = ""
    for f in lista_archivos[:25]: # Limitar para que no sea infinito
        activo_class = "active-file" if f == archivo_principal else ""
        explorer_html += f'<div class="vscode-explorer-item {activo_class}">📄 {f}</div>'

    # Construir líneas del editor con números y color tipo tema oscuro CodelyTV
    editor_lineas = ""
    for idx, linea in enumerate(contenido_codigo.split('\n'), start=1):
        linea_escaped = linea.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        editor_lineas += f"""<div class="vscode-row">
            <span class="vscode-linenr">{idx}</span>
            <span class="vscode-code-text">{linea_escaped}</span>
        </div>"""

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>{repo_name} - VS Code View</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.5; color: #24292e; max-width: 1150px; margin: 20px auto; padding: 0 15px; background: #1e1e1e; }}
        h1, h2 {{ color: #ffffff; border-bottom: 1px solid #333; padding-bottom: .3em; }}
        
        .section-box {{ background: #252526; border: 1px solid #333; border-radius: 6px; padding: 20px; margin-bottom: 25px; color: #d4d4d4; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }}
        
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px; margin-bottom: 25px; }}
        .metric-box {{ background: #2d2d2d; border: 1px solid #3c3c3c; border-radius: 6px; padding: 15px; color: #d4d4d4; }}
        .metric-box h3 {{ margin: 0 0 8px 0; font-size: 11px; color: #4ec9b0; border: none; text-transform: uppercase; letter-spacing: 1px; }}
        .metric-box p {{ margin: 0; font-size: 15px; font-weight: bold; color: #ffffff; word-break: break-all; }}

        table {{ width: 100%; border-collapse: collapse; font-size: 13px; color: #d4d4d4; }}
        th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid #333; }}
        th {{ background-color: #2d2d2d; color: #9cdcfe; }}
        tr:hover {{ background-color: #2a2d2e; }}

        /* Estética de Entorno VS Code (Estilo CodelyTV Theme) */
        .vscode-window {{ background-color: #181818; border-radius: 8px; overflow: hidden; border: 1px solid #333; box-shadow: 0 8px 24px rgba(0,0,0,0.5); margin-top: 15px; }}
        .vscode-titlebar {{ background-color: #323233; color: #cccccc; padding: 10px 15px; font-size: 13px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #252526; }}
        .vscode-dots {{ display: flex; gap: 6px; }}
        .vscode-dot {{ width: 12px; height: 12px; border-radius: 50%; }}
        .dot-red {{ background-color: #ff5f56; }}
        .dot-yellow {{ background-color: #ffbd2e; }}
        .dot-green {{ background-color: #27c93f; }}

        .vscode-body {{ display: flex; height: 500px; background-color: #1e1e1e; }}
        .vscode-sidebar {{ width: 240px; background-color: #252526; border-right: 1px solid #1e1e1e; overflow-y: auto; font-size: 12px; color: #bbbbbb; }}
        .vscode-sidebar-title {{ padding: 10px 12px; font-weight: bold; font-size: 11px; text-transform: uppercase; color: #bbbbbb; letter-spacing: 0.8px; }}
        .vscode-explorer-item {{ padding: 6px 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; cursor: pointer; }}
        .vscode-explorer-item:hover {{ background-color: #2a2d2e; color: #ffffff; }}
        .vscode-explorer-item.active-file {{ background-color: #37373d; color: #ffffff; border-left: 2px solid #007acc; }}

        .vscode-main-area {{ flex: 1; display: flex; flexDirection: column; overflow: hidden; background-color: #1e1e1e; }}
        .vscode-tabs {{ background-color: #2d2d2d; display: flex; border-bottom: 1px solid #252526; }}
        .vscode-tab {{ background-color: #1e1e1e; color: #ffffff; padding: 8px 16px; font-size: 12px; display: flex; align-items: center; gap: 6px; border-top: 2px solid #007acc; border-right: 1px solid #252526; font-family: Consolas, monospace; }}

        .vscode-editor {{ flex: 1; overflow: auto; font-family: Consolas, "Courier New", monospace; font-size: 13px; padding: 10px 0; background-color: #1e1e1e; color: #d4d4d4; }}
        .vscode-row {{ display: flex; width: 100%; line-height: 22px; }}
        .vscode-linenr {{ width: 50px; color: #858585; text-align: right; padding-right: 15px; user-select: none; font-size: 12px; }}
        .vscode-code-text {{ white-space: pre; flex: 1; }}

        footer {{ text-align: center; font-size: 12px; color: #858585; margin-top: 30px; }}
    </style>
</head>
<body>
    <h1>⚡ {repo_name} - Workspace Dashboard</h1>
    <p style="color: #9cdcfe;">Generado el <b>{fecha_actual}</b></p>

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
            <span style="font-size: 11px; color: #858585;">{commit_actual['email']}</span>
        </div>
        <div class="metric-box">
            <h3>Último Commit</h3>
            <p><code>{commit_actual['hash']}</code></p>
            <span style="font-size: 11px; color: #ce9178;">{commit_actual['message']}</span>
        </div>
    </div>

    <div class="section-box">
        <h2>📜 Changelog Reciente</h2>
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

    <div class="section-box">
        <h2>💻 Explorador y Visor de Código (Entorno VS Code)</h2>
        
        <div class="vscode-window">
            <div class="vscode-titlebar">
                <div class="vscode-dots">
                    <div class="vscode-dot dot-red"></div>
                    <div class="vscode-dot dot-yellow"></div>
                    <div class="vscode-dot dot-green"></div>
                </div>
                <span>{repo_name} - Visual Studio Code (Solo Lectura)</span>
                <span style="font-size: 11px; color: #858585;">UTF-8 | Python</span>
            </div>
            
            <div class="vscode-body">
                <!-- Barra lateral de explorador -->
                <div class="vscode-sidebar">
                    <div class="vscode-sidebar-title">📁 Explorer</div>
                    {explorer_html}
                </div>
                
                <!-- Área principal con pestañas y editor -->
                <div class="vscode-main-area">
                    <div class="vscode-tabs">
                        <div class="vscode-tab">📄 {archivo_principal}</div>
                    </div>
                    <div class="vscode-editor">
                        {editor_lineas}
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer>
        <p>Pipeline automatizado con Python y GitHub Actions.</p>
    </footer>
</body>
</html>
"""

    os.makedirs('public', exist_ok=True)
    with open('public/index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("¡Workspace estilo VS Code generado con éxito!")

if __name__ == '__main__':
    datos = cargar_datos_evento()
    generar_html(datos)
    
