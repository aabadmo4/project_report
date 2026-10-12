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
        f"El análisis detectó un total de <b>{lineas_agregadas} líneas añadás</b> y <b>{lineas_eliminadas} líneas eliminadas</b>. "
        f"Los ajustes se centran en mejorar la estructura visual, la presentación de datos y la automatización del workspace."
    )

    return commit_sugerido, texto_resumen
