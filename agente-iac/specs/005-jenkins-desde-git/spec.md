# Spec 005 – Jenkins desde Git: pipeline automático tras el merge

- **Estado:** aprobada
- **Aprobación:** delegada por el usuario al agente, 2026-11-17 (polling de main cada 5 min, staging hasta la aprobación manual y encolado de local); no revisada línea a línea por un humano
- **Fecha:** 2026-11-17
- **Requerimiento origen:** requerimiento.md

## Objetivo
Hacer que Jenkins obtenga el código desde el repositorio de GitHub (rama `main`) y lance el pipeline por sí solo tras cada merge, deteniéndose en la aprobación manual existente, en lugar de depender de la carpeta local y de un disparo a mano.

## Alcance
- El job `agente-iac` obtiene el pipeline y el código desde el repositorio Git, rama `main`, en lugar del montaje local de solo lectura.
- Disparo automático por consulta periódica (polling) del repositorio: un commit nuevo en `main` encola un build.
- El build automático usa siempre el entorno `staging` y la acción `apply`; llega hasta la etapa de aprobación manual y espera.
- Tras un `apply` de staging aprobado y verificado, se encola de forma automática el build de `local`, que se detiene en su propia aprobación manual.
- Jenkins incorpora lo necesario para clonar (herramienta Git y el plugin de Git con versión fijada).
- Se conserva el estado de Terraform de las ejecuciones anteriores y la compuerta de promoción por huella de `infra/`.

## Fuera de alcance
- Webhooks desde GitHub, túneles o exponer Jenkins a internet.
- Aplicar sin aprobación manual, o aprobar de forma automática (ni siquiera en staging).
- Ejecutar `destroy` de forma automática.
- Separar solicitante y aprobador (sigue habiendo un único usuario).
- Disparar por ramas distintas de `main` o por pull requests (eso lo cubre el CI de GitHub Actions).
- Colector OpenTelemetry y cualquier cambio en los módulos de Terraform.

## Recursos
| Recurso | Servicio | Propósito |
|---|---|---|
| Job `agente-iac` con definición desde Git | Jenkins | Obtener pipeline y código desde `main` |
| Disparador por polling de `main` | Jenkins | Lanzar el build tras un merge |
| Plugin de Git y herramienta Git en la imagen | Jenkins | Clonar el repositorio |
| Encadenado staging -> local | Jenkins | Encolar `local` tras un staging verificado |

## Criterios de aceptación
**CA-1 – El pipeline sale de Git**
- Dado el job `agente-iac` configurado
- Cuando se consulta su definición por la API de Jenkins
- Entonces el pipeline se obtiene de un repositorio Git en la rama `main` y no de un archivo copiado en la imagen

**CA-2 – El código del build sale de Git**
- Dado un commit nuevo fusionado en `main`
- Cuando se ejecuta el build
- Entonces el registro del build muestra el checkout de ese commit y el directorio de trabajo contiene exactamente ese commit

**CA-3 – El merge dispara el build sin intervención**
- Dado el job configurado con polling y sin builds en curso
- Cuando se fusiona un commit nuevo en `main` y transcurre el intervalo de consulta
- Entonces aparece un build nuevo con el commit fusionado sin ejecutar `scripts/jenkins.sh disparar`

**CA-4 – El build automático es staging y apply**
- Dado un build lanzado por el polling
- Cuando se consultan sus parámetros
- Entonces `ENTORNO` es `staging` y `ACCION` es `apply`, y ninguna ruta de disparo automático usa `destroy`

**CA-5 – La aprobación manual se mantiene**
- Dado un build automático de staging
- Cuando llega a la etapa de aprobación
- Entonces queda en estado de espera y el emulador no contiene recursos nuevos hasta que un humano apruebe

**CA-6 – Local se encola solo, pero espera aprobación**
- Dado un build de staging con `apply` aprobado y pruebas de humo en verde
- Cuando termina con éxito
- Entonces se crea un build de `local` con `apply` que se detiene en la aprobación manual, tras superar la compuerta de promoción

**CA-7 – Sin cambios nuevos no hay builds**
- Dado `main` sin commits nuevos
- Cuando transcurren varios intervalos de consulta
- Entonces no se crea ningún build adicional

**CA-8 – Estado de Terraform conservado**
- Dado un build de staging posterior a uno ya aplicado
- Cuando se ejecuta el plan
- Entonces el estado previo se conserva y el plan no propone recrear recursos ya existentes

**CA-9 – Sin secretos en el repositorio ni en el job**
- Dado el código y la configuración de Jenkins versionados
- Cuando se ejecuta Gitleaks sobre el historial
- Entonces no hay hallazgos, y cualquier credencial de lectura del repositorio se inyecta por variable de entorno, no está escrita en archivos

**CA-10 – Gate de seguridad**
- Dado el código generado
- Cuando se ejecutan Checkov, TFLint y Trivy
- Entonces no hay hallazgos HIGH ni CRITICAL sin excepción documentada

## Restricciones
- Versiones fijadas: el plugin de Git y la herramienta Git de la imagen con versión explícita; la imagen se reconstruye con `docker compose build jenkins`.
- Jenkins solo sale a GitHub por HTTPS (lectura); no se abre ningún puerto al exterior.
- Los valores por defecto de los parámetros del job son `staging` y `apply`; `destroy` nunca es el valor por defecto.
- La rama de la fase sale de `main` y se llama `feature/fase-20-jenkins-desde-git`.
- Documentación en español; código y nombres de recursos en inglés.

## Compatibilidad con el emulador
| Operación | Verificada | Nota |
|---|---|---|
| Ninguna operación nueva de AWS | No aplica | Esta spec solo cambia cómo Jenkins obtiene el código y cuándo lanza el pipeline; el apply sigue siendo contra el emulador, ya verificado |
| Salida de Jenkins a GitHub por HTTPS | No | Hay que comprobar que el contenedor de Jenkins resuelve y alcanza GitHub; el contenedor comparte la red del emulador |

## Supuestos
- El repositorio se clona de forma anónima por HTTPS, en modo lectura, porque el README lo declara público. Si fuera privado, haría falta un token de solo lectura inyectado por variable de entorno (CA-9).
- Intervalo de consulta de 5 minutos: equilibra rapidez y carga.
- Cualquier commit en `main` dispara un build, incluidos los de solo documentación; filtrar por rutas queda como mejora posterior.
- Los builds automáticos no se acumulan: `disableConcurrentBuilds` se mantiene y, si hay uno esperando aprobación, el siguiente espera en cola.
- Si nadie aprueba en 30 minutos el build termina abortado, como hoy; el siguiente commit lo vuelve a lanzar.
- El encadenado a `local` solo se encola; la compuerta de promoción y la aprobación manual siguen mandando.

## Preguntas abiertas
- ¿El repositorio es público o privado? Hay una discrepancia entre el README (público) y las reglas del proyecto (privado). No bloquea: se asume lectura anónima.
- Resuelta por el usuario el 2026-11-17: el encadenado automático a `local` (CA-6) se mantiene.

## Riesgos
- Un build automático que se queda esperando aprobación bloquea los siguientes (`disableConcurrentBuilds`). Mitigación: el tiempo máximo de 30 minutos de la aprobación.
- Ejecutar un pipeline por cada merge puede aplicar cambios de `main` sin que nadie lo espere. Mitigación: la aprobación manual sigue siendo obligatoria en staging y en local.
- Si el repositorio fuera privado y se usara un token, es una credencial nueva. Mitigación: variable de entorno, mínimo privilegio (solo lectura) y Gitleaks (CA-9).
- Cambiar el origen del código modifica el comportamiento del estado de Terraform y de la compuerta de promoción (hoy leen el directorio local). Mitigación: CA-8 y las pruebas de promoción existentes (`scripts/probar-promocion-jenkins.sh`).
- Dependencia de GitHub: si no está disponible, no hay disparo. Mitigación: `scripts/jenkins.sh disparar` sigue sirviendo como respaldo manual.

## Nivel de aprobación
- Spec: humano (propietario del requerimiento); aprobación delegada al agente el 2026-11-17.
- `apply` y `destroy`: aprobación manual en Jenkins; sin acciones destructivas automáticas.
