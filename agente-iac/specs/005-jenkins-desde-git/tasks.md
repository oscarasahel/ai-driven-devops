# Tareas – Spec 005

Ver `plan.md`. Estado a 2026-11-17.

| # | Tarea | Criterio | Estado | Evidencia |
|---|---|---|---|---|
| T1 | Spec 005 redactada y aprobada (delegada) | Todos | Hecha | `spec.md`; `validar_spec.py` en OK |
| T2 | Job con definición desde Git y polling | CA-1, CA-3 | Hecha (configuración) | Instancia desechable: `config.xml` con `GitSCM` `*/main`, `scriptPath` y `SCMTrigger H/5 * * * *` |
| T3 | Imagen con `git` y plugins fijados | CA-1 | Hecha | `docker compose build jenkins`; `git 2.47.3`, `git.jpi` y `git-client.jpi` en la imagen |
| T4 | Quitar la copia local del código y añadir `Encadenar local` | CA-2, CA-6 | Hecha (código) | `jenkins/Jenkinsfile`; ejecución real pendiente |
| T5 | Pruebas que imponen los controles | CA-1, CA-4 a CA-6, CA-9 | Hecha | `tests/test_jenkins_desde_git.py` (8); 128 pruebas en total |
| T6 | Gate de seguridad y Gitleaks | CA-9, CA-10 | Hecha | `seguridad.sh`: 6 PASS; Gitleaks: 44 commits sin hallazgos |
| T7 | Jenkins alcanza GitHub desde el contenedor | Supuesto | Hecha | `git ls-remote` anónimo desde el contenedor devolvió el commit de `main` |
| T8 | Build real desde Git, sin disparo manual, hasta la aprobación | CA-2, CA-3, CA-5 | Pendiente | Requiere la rama en GitHub y recrear Jenkins |
| T9 | Encadenado staging -> local y estado conservado | CA-6, CA-8 | Pendiente | Idem |
| T10 | Sin builds nuevos con `main` quieto | CA-7 | Pendiente | Observación de varios intervalos |
