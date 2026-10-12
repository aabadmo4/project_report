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

def obtener_cambios_git():
    """Obtiene los archivos modificados y el diff usando comandos de Git locales"""
    try:
        # Obtener los archivos modificados en el último commit
        resultado_archivos = subprocess.run(
            ['git', 'diff-tree', '--no-commit-id', '--name-status', '-r', 'HEAD'],
            capture_output=True, text=True, check=True
        )
        
        lineas = resultado_archivos.stdout.strip().split('\n')
        cambios_archivos = []
        for linea in lineas:
            if not linea:
                continue
            partes = linea.split('\t')
            if len(partes) >= 2:
                estado, archivo = partes[0], partes[1]
                cambios_archivos.append((estado, archivo))

        # Obtener el diff detallado de líneas
        resultado_diff = subprocess.run(
            ['git', 'diff', 'HEAD~1', 'HEAD'],
            capture_output=True, text=True
        )
        diff_texto = resultado_diff.stdout if resultado_diff.returncode == 0 else "No hay diff disponible (primer commit o rama única)."

        return cambios_archivos, diff_texto
    except Exception as e:
        return [], f"Error obteniendo diff de git: {str(e)}"

def generar_html(event_data):
    repo_name = os.getenv('GITHUB_REPOSITORY', 'Mi Repositorio')
    actor = os.getenv('GITHUB_ACTOR', 'Desconocido')
    evento_tipo = os.getenv('GITHUB_EVENT_NAME', 'push')
    fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    commits = event_data.get('commits', [])
    pull_request = event_data.get('pull_request', {})
    
    commits_html = ""
    if commits:
        for commit in commits:
            msg = commit.get('message', 'Sin mensaje')
            author = commit.get('author', {}).get('name', 'Anónimo')
            url = commit.get('url', '#')
            commits_html += f"<li><b>{author}</b>: <a href='{url}' target='_blank'>{msg}</a></li>"
    else:
        commits_html = "<li>No hay commits recientes listados en el evento.</li>"

    # Obtener los cambios reales mediante Git
    archivos_git, diff_git = obtener_cambios_git()
    
    diff_html = ""
    if archivos_git:
        diff_html += "<div class='commit-block'><h4>Archivos Modificados en este Commit</h4>"
        for estado, archivo in archivos_git:
            if estado == 'A':
                diff_html += f"<div class='file-change added'>[AÑADIDO] {archivo}</div>"
            elif estado == 'M':
                diff_html += f"<div class='file-change modified'>[MODIFICADO] {archivo}</div>"
            elif estado == 'D':
                diff_html += f"<div class='file-change removed'>[ELIMINADO] {archivo}</div>"
            else:
                diff_html += f"<div class='file-change modified'>[{estado}] {archivo}</div>"
        diff_html += "</div>"
    
    # Añadir el visor de código de líneas (Diff formateado)
    diff_html += f"<h4>Diff de Código (Líneas afectadas)</h4><pre class='code-diff'>"
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

    # Procesar Pull Request si aplica
    pr_html = ""
    if pull_request:
        pr_title = pull_request.get('title', 'Sin título')
        pr_user = pull_request.get('user', {}).get('login', 'Desconocido')
        pr_body = pull_request.get('body', 'Sin descripción')
        pr_url = pull_request.get('html_url', '#')
        pr_html = f"""
        <div class="card">
            <h3>Pull Request Activo: <a href="{pr_url}" target="_blank">{pr_title}</a></h3>
            <p><b>Autor:</b> {pr_user}</p>
            <p><b>Descripción del PR:</b></p>
            <pre>{pr_body}</pre>
        </div>
        """
    else:
        pr_html = "<p>Este workflow no fue disparado por un Pull Request directo.</p>"

    # HTML completo con estilos mejorados para el diff
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Dashboard y Visor de Código - {repo_name}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #24292e; max-width: 950px; margin: 40px auto; padding: 0 20px; background: #f6f8fa; }}
        h1, h2, h3, h4 {{ color: #24292e; border-bottom: 1px solid #eaecef; padding-bottom: .3em; }}
        .card {{ background: #fff; border: 1px solid #e1e4e8; border-radius: 6px; padding: 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }}
        .metric-box {{ background: #f1f8ff; border: 1px solid #c8e1ff; border-radius: 6px; padding: 15px; text-align: center; }}
        .metric-box h3 {{ margin: 0 0 10px 0; font-size: 14px; color: #0366d6; border: none; }}
        .metric-box p {{ margin: 0; font-size: 22px; font-weight: bold; color: #24292e; }}
        ul {{ padding-left: 20px; }}
        pre {{ background: #f6f8fa; padding: 12px; border-radius: 6px; border: 1px solid #e1e4e8; overflow-x: auto; font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace; font-size: 13px; }}
        
        .commit-block {{ background: #fff; border: 1px solid #d1d5db; border-radius: 6px; margin-bottom: 15px; overflow: hidden; }}
        .file-change {{ padding: 6px 12px; font-family: monospace; font-size: 13px; border-bottom: 1px solid #f3f4f6; }}
        .file-change.added {{ background-color: #ecfdf5; color: #065f46; border-left: 4px solid #10b981; }}
        .file-change.modified {{ background-color: #eff6ff; color: #1e40af; border-left: 4px solid #3b82f6; }}
        .file-change.removed {{ background-color: #fef2f2; color: #991b1b; border-left: 4px solid #ef4444; }}

        /* Estilos específicos para las líneas del Diff */
        .code-diff {{ background-color: #1e1e1e; color: #d4d4d4; padding: 15px; border-radius: 6px; }}
        .line-added {{ background-color: rgba(16, 185, 129, 0.2); color: #34d399; display: block; }}
        .line-removed {{ background-color: rgba(239, 68, 68, 0.2); color: #f87171; display: block; }}
        .line-chunk {{ color: #569cd6; font-weight: bold; display: block; margin-top: 5px; }}

        footer {{ text-align: center; font-size: 12px; color: #586069; margin-top: 40px; }}
    </style>
</head>
<body>
    <h1>📊 Panel de Actividad y Visor de Código</h1>
    <p>Repositorio: <b>{repo_name}</b> | Actualizado el <b>{fecha_actual}</b> por <i>{actor}</i>.</p>

    <div class="metrics-grid">
        <div class="metric-box">
            <h3>Tipo de Evento</h3>
            <p>{evento_tipo}</p>
        </div>
        <div class="metric-box">
            <h3>Commits Analizados</h3>
            <p>{len(commits) if commits else 1}</p>
        </div>
    </div>

    <div class="card">
        <h2>📑 Changelog Reciente</h2>
        <ul>
            {commits_html}
        </ul>
    </div>

    <div class="card">
        <h2>💻 Visor de Cambios en Código (Diff en vivo)</h2>
        {diff_html}
    </div>

    <div class="card">
        <h2>🔍 Detalles del Pull Request</h2>
        {pr_html}
    </div>

    <footer>
        <p>Generado automáticamente mediante GitHub Actions y Python.</p>
    </footer>
</body>
</html>
"""

    os.makedirs('public', exist_ok=True)
    with open('public/index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("¡Página con visor de Git Diff generada con éxito!")

if __name__ == '__main__':
    datos = cargar_datos_evento()
    generar_html(datos)
        
