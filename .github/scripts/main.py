import os
import datetime
from .git_service import obtener_info_git_completa, obtener_archivos_y_diff
from .commit_analyzer import analizar_y_generar_conventional_commit
from .html_generator import construir_html_dashboard

def main():
    full_repo = os.getenv('GITHUB_REPOSITORY', 'usuario/repositorio')
    if '/' in full_repo:
        org_owner, repo_name = full_repo.split('/', 1)
    else:
        org_owner, repo_name = "Desconocido", full_repo

    actor = os.getenv('GITHUB_ACTOR', 'Desconocido')
    fecha_actual = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

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

    html_final = construir_html_dashboard(
        repo_name, org_owner, fecha_actual, commit_actual,
        commit_sugerido, descripcion_cambios, changelog_html,
        lista_archivos, archivo_principal, diff_contenido
    )

    os.makedirs('public', exist_ok=True)
    with open('public/index.html', 'w', encoding='utf-8') as f:
        f.write(html_final)
    print("¡Dashboard modular generado con éxito!")

if __name__ == '__main__':
    main()
    
