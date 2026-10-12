import os
import json
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

    # Extracción básica de información según el evento
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
        commits_html = "<li>No hay commits recientes en este evento o es un tipo de evento diferente (PR/Merge).</li>"

    pr_html = ""
    if pull_request:
        pr_title = pull_request.get('title', 'Sin título')
        pr_user = pull_request.get('user', {}).get('login', 'Desconocido')
        pr_body = pull_request.get('descripción', pull_request.get('body', 'Sin descripción'))
        pr_url = pull_request.get('html_url', '#')
        pr_html = f"""
        <div class="card">
            <h3>Pull Request Activo: <a href="{pr_url}" target="_blank">{pr_title}</a></h3>
            <p><b>Autor:</b> {pr_user}</p>
            <p><b>Descripción / Explicación:</b></p>
            <pre>{pr_body}</pre>
        </div>
        """
    else:
        pr_html = "<p>Este workflow no fue disparado por un Pull Request directo.</p>"

    # HTML completo y estructurado para la GitHub Page
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Dashboard y Changelog - {repo_name}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; max-width: 900px; margin: 40px auto; padding: 0 20px; background: #f6f8fa; }}
        h1, h2 {{ color: #24292e; border-bottom: 1px solid #eaecef; padding-bottom: .3em; }}
        .card {{ background: #fff; border: 1px solid #e1e4e8; border-radius: 6px; padding: 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }}
        .metric-box {{ background: #f1f8ff; border: 1px solid #c8e1ff; border-radius: 6px; padding: 15px; text-align: center; }}
        .metric-box h3 {{ margin: 0 0 10px 0; font-size: 14px; color: #0366d6; }}
        .metric-box p {{ margin: 0; font-size: 24px; font-weight: bold; color: #24292e; }}
        ul {{ padding-left: 20px; }}
        pre {{ background: #f6f8fa; padding: 10px; border-radius: 4px; border: 1px solid #e1e4e8; overflow-x: auto; }}
        footer {{ text-align: center; font-size: 12px; color: #586069; margin-top: 40px; }}
    </style>
</head>
<body>
    <h1>📊 Panel de Actividad: {repo_name}</h1>
    <p>Generado automáticamente mediante GitHub Actions y Python el <b>{fecha_actual}</b>.</p>

    <div class="metrics-grid">
        <div class="metric-box">
            <h3>Tipo de Evento</h3>
            <p>{evento_tipo}</p>
        </div>
        <div class="metric-box">
            <h3>Actor Principal</h3>
            <p style="font-size: 18px; word-break: break-all;">{actor}</p>
        </div>
        <div class="metric-box">
            <h3>Commits en este evento</h3>
            <p>{len(commits)}</p>
        </div>
    </div>

    <div class="card">
        <h2>📑 Changelog / Commits Recientes</h2>
        <ul>
            {commits_html}
        </ul>
    </div>

    <div class="card">
        <h2>🔍 Detalles del Pull Request</h2>
        {pr_html}
    </div>

    <footer>
        <p>Proyecto automatizado con Python y GitHub Actions.</p>
    </footer>
</body>
</html>
"""

    os.makedirs('public', exist_ok=True)
    with open('public/index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("¡Página estática generada con éxito en la carpeta 'public/'!")

if __name__ == '__main__':
    datos = cargar_datos_evento()
    generar_html(datos)
