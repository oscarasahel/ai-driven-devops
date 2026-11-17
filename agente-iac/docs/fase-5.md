# Fase 5 – Jenkins con pipeline y aprobación manual (2026-11-16)

> **Estado: construido pero NO verificado de extremo a extremo.** El usuario canceló la prueba del pipeline para ahorrar tiempo.

## Qué se entregó
- `jenkins/Dockerfile`: Jenkins LTS 2.580.2 (jdk21) con Terraform 1.9.8, TFLint 0.53.0 y Trivy 0.58.1 (copiados de imágenes oficiales fijadas), AWS CLI 2.22.0 y Checkov 3.2.255 (Python 3.12 aislado con uv).
- JCasC (`jenkins/casc/`): usuario admin desde `.env`, sin acceso anónimo, job `agente-iac` creado con Job DSL.
- `jenkins/Jenkinsfile`: Preparar -> Validate/lint/seguridad (JUnit + SARIF) -> Plan (artefacto `plan.txt`) -> **Aprobación manual** (`input`, 30 min) -> Apply -> Pruebas de humo. Parámetro `ACCION` apply/destroy (destroy también pide aprobación).
- `docker-compose.yml`: servicio `jenkins` en la red del emulador (su certificado solo vale para localhost/127.0.0.1); UI en `127.0.0.1:8080`.
- `scripts/seguridad.sh` y `scripts/verificar-criterios.sh` con modo nativo (`SEGURIDAD_MODO=nativo`, `VERIFICAR_MODO=nativo`) para correr sin Docker dentro de Jenkins.
- `scripts/jenkins.sh`: cliente de la API (disparar, aprobar, rechazar, log).

## Verificado
- La imagen se construye y Jenkins arranca sano (healthcheck) cargando la configuración JCasC; el log confirma la creación del job `agente-iac`.
- El gate de seguridad en modo Docker sigue en verde tras refactorizar `seguridad.sh`.

## No verificado (pendiente)
- Ninguna ejecución del pipeline completo: ni el modo nativo del gate dentro de Jenkins, ni el `input` de aprobación, ni apply/pruebas de humo desde Jenkins.
- `scripts/jenkins.sh`: al probarlo devolvió 404 en `esperar-aprobacion 1` (el build #1 no apareció). Causa sin diagnosticar; puede ser el disparo de la primera ejecución (job sin parámetros definidos aún) o el propio cliente.
- Criterio global "no aplica sin aprobación" queda sin evidencia hasta ejecutar el pipeline (se puede disparar a mano desde la UI en `http://127.0.0.1:8080`).

## Decisiones y desviaciones
- Descargas directas de Trivy daban 404; se copian los binarios de las imágenes oficiales.
- Los plugins de Jenkins se instalan en su última versión (sin fijar); la versión del núcleo sí está fijada.
- Contraseña de prueba solo local (`.env`, ignorado por git).
