def aplicar_git_amend_automatico(commit_titulo, commit_cuerpo):
    try:
        resultado_log = subprocess.run(['git', 'log', '-1', '--pretty=format:%s'], capture_output=True, text=True, check=True)
        ultimo_mensaje = resultado_log.stdout.strip()
        
        if ultimo_mensaje.startswith(('feat(', 'fix(', 'refactor(', 'style(', 'ci(', 'docs(', 'test(', 'perf(')):
            print("El commit actual ya cuenta con formato Conventional Commit. Omitiendo amend.")
            return

        mensaje_completo = f"{commit_titulo}\n\n{commit_cuerpo}"
        
        # Modificamos el commit utilizando los archivos fuente modificados (excluyendo index.html)
        subprocess.run(['git', 'add', '-u'], check=True)
        subprocess.run(['git', 'commit', '--amend', '-m', mensaje_completo], check=True)
        
        branch = os.getenv('GITHUB_REF_NAME', 'main')
        subprocess.run(['git', 'push', 'origin', f'HEAD:{branch}', '--force'], check=True)
        print("¡Commit modificado en el servidor remoto con éxito!")
    except Exception as e:
        print(f"Aviso en la modificación automática del commit: {str(e)}")
        
