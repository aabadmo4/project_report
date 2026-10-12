import subprocess
import os

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
