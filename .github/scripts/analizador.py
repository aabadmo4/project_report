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
    lineas_agregadas = sum(1 for l in diff_texto.split('\n') if l.startswith('+') and not l.startswith('+++'))
    lineas_eliminadas = sum(1 for l in diff_texto.split('\n') if l.startswith('-') and not l.startswith('---'))
    
    texto_resumen = f"Se han modificado componentes clave en el archivo <code>{archivo}</code>. Detectadas <b>{lineas_agregadas} líneas añadidas</b> y <b>{lineas_eliminadas} eliminadas</b>."
    texto_copiar = f"{commit_sugerido}\n\n* Actualiza componentes y estructura del proyecto."

    return commit_sugerido, texto_resumen, lineas_agregadas, lineas_eliminadas, texto_copiar

def generar_html(event_data):
    full_repo = os.getenv('GITHUB_REPOSITORY', 'aabadmo4/project_report')
    org_owner, repo_name = full_repo.split('/') if '/' in full_repo else ("Desconocido", full_repo)
    actor = os.getenv('GITHUB_ACTOR', 'Desconocido')
    fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    historial_commits = obtener_info_git_completa()
    commit_actual = historial_commits[0] if historial_commits else {'hash': 'N/A', 'author': actor, 'email': 'N/A', 'date': fecha_actual, 'message': 'Sin commits'}
    repo_url = f"https://github.com/{full_repo}"

    changelog_html = "".join([
        f'<tr class="changelog-row"><td><a href="{repo_url}/commit/{c["hash"]}" target="_blank"><code>{c["hash"]}</code></a></td><td><b>{c["message"]}</b></td><td>{c["author"]}</td><td>{c["date"]}</td></tr>'
        for c in historial_commits
    ])

    lista_archivos, archivo_principal, diff_contenido = obtener_archivos_y_diff()
    commit_sugerido, descripcion_cambios, agregadas, eliminadas, texto_copiar = analizar_y_generar_conventional_commit(archivo_principal, diff_contenido)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
    template_path = os.path.join(script_dir, 'template.html')

    # Leer la plantilla HTML externa de manera limpia
    with open(template_path, 'r', encoding='utf-8') as f:
        plantilla = f.read()

    html_content = plantilla.format(
        repo_name=repo_name,
        org_owner=org_owner,
        fecha_actual=fecha_actual,
        autor=commit_actual['author'],
        email=commit_actual['email'],
        hash_c=commit_actual['hash'],
        mensaje_c=commit_actual['message'],
        repo_url=repo_url,
        descripcion_cambios=descripcion_cambios,
        commit_sugerido=commit_sugerido,
        changelog_html=changelog_html,
        texto_copiar=texto_copiar.replace('"', '\\"')
    )

    public_dir = os.path.join(repo_root, 'public')
    os.makedirs(public_dir, exist_ok=True)
    with open(os.path.join(public_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("¡Dashboard generado con éxito desde plantilla externa!")

if __name__ == '__main__':
    generar_html(cargar_datos_evento())
    
