os = __import__('os')
json = __import__('json')
from datetime import datetime

def cargar_datos_evento():
    event_path = os.getenv('GITHUB_EVENT_PATH')
    if event_path and os.path.exists(event_path):
        with open(event_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def generar_html(event_data):
    repo_name = os.getenv('GITHUB_REPOSITORY', 'Mi Repositorio')
    actor = os.getenv('GITHUB_ACTOR', 'Desconocido')
    evento_tipo = os.getenv('GITHUB_EVENT_NAME', 'push')
    fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    commits = event_data.get('commits', [])
    pull_request = event_data.get('pull_request', {})
    
    # 1. Procesar Commits y extraer cambios de archivos si existen
    commits_html = ""
    diff_html = ""
    
    if commits:
        for commit in commits:
            msg = commit.get('message', 'Sin mensaje')
            author = commit.get('author', {}).get('name', 'Anónimo')
            url = commit.get('url', '#')
            commits_html += f"<li><b>{author}</b>: <a href='{url}' target='_blank'>{msg}</a></li>"
            
            # Extraer ficheros modificados, añadidos o eliminados en el commit
            added = commit.get('added', [])
            modified = commit.get('modified', [])
            removed = commit.get('removed', [])
            
            if added or modified or removed:
                diff_html += f"<div class='commit-block'><h4>Commit: {msg} (<span>{author}</span>)</h4>"
                
                for f in added:
                    diff_html += f"<div class='file-change added'>[AÑADIDO] {f}</div>"
                for f in modified:
                    diff_html += f"<div class='file-change modified'>[MODIFICADO] {f}</div>"
                for f in removed:
                    diff_html += f"<div class='file-change removed'>[ELIMINADO] {f}</div>"
                
                diff_html += "</div>"
    else:
        commits_html = "<li>No hay commits recientes en este evento o es un tipo de evento diferente.</li>"

    if not diff_html:
        diff_html = "<p>No se registraron cambios directos de archivos en este evento específico.</p>"

    # 2. Procesar Pull Request si aplica
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

    # HTML completo con estilos para el visor de código
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Dashboard y Visor de Código - {repo_name}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #24292e; max-width: 950px; margin: 40px auto; padding: 0 20px; background: #f6f8fa; }}
        h1, h2, h3 {{ color: #24292e; border-bottom: 1px solid #eaecef; padding-bottom: .3em; }}
        .card {{ background: #fff; border: 1px solid #e1e4e8; border-radius: 6px; padding: 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }}
        .metric-box {{ background: #f1f8ff; border: 1px solid #c8e1ff; border-radius: 6px; padding: 15px; text-align: center; }}
        .metric-box h3 {{ margin: 0 0 10px 0; font-size: 14px; color: #0366d6; border: none; }}
        .metric-box p {{ margin: 0; font-size: 22px; font-weight: bold; color: #24292e; }}
        ul {{ padding-left: 20px; }}
        pre {{ background: #f6f8fa; padding: 12px; border-radius: 6px; border: 1px solid #e1e4e8; overflow-x: auto; font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace; font-size: 13px; }}
        
        /* Estilos del Visor de Código / Diff */
        .commit-block {{ background: #fff; border: 1px solid #d1d5db; border-radius: 6px; margin-bottom: 15px; overflow: hidden; }}
        .commit-block h4 {{ background: #f3f4f6; margin: 0; padding: 10px 15px; font-size: 14px; border-bottom: 1px solid #e5e7eb; display: flex; justify-content: space-between; align-items: center; }}
        .commit-block h4 span {{ color: #4b5563; font-weight: normal; font-size: 12px; }}
        .file-change {{ padding: 8px 15px; font-family: monospace; font-size: 13px; border-bottom: 1px solid #f3f4f6; }}
        .file-change.added {{ background-color: #ecfdf5; color: #065f46; border-left: 4px solid #10b981; }}
        .file-change.modified {{ background-color: #eff6ff; color: #1e40af; border-left: 4px solid #3b82f6; }}
        .file-change.removed {{ background-color: #fef2f2; color: #991b1b; border-left: 4px solid #ef4444; }}

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
            <p>{len(commits)}</p>
        </div>
    </div>

    <div class="card">
        <h2>📑 Changelog Reciente</h2>
        <ul>
            {commits_html}
        </ul>
    </div>

    <div class="card">
        <h2>💻 Visor de Cambios en Código (Diff / Archivos Afectados)</h2>
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
    print("¡Página con visor de código generada con éxito!")

if __name__ == '__main__':
    datos = cargar_datos_evento()
    generar_html(datos)
        
