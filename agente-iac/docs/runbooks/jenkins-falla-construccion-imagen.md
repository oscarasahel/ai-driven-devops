# Runbook: falla la construcción de la imagen de Jenkins

- **Estado:** probado parcialmente. Surge de 3 incidentes reales del 2026-11-16 durante la fase 5; los pasos de diagnóstico se ejecutaron entonces, los de remediación se aplicaron una vez cada uno.
- **Versión:** 0.2 · **Dueño:** responsable del repo
- **Nivel de autonomía recomendado:** L2 (el agente sugiere comandos de solo lectura; el humano ejecuta y aprueba cualquier cambio)

## 1. Disparador (trigger)
`docker compose build jenkins` termina con `failed to solve: process "/bin/sh -c ..." did not complete successfully`.

## 2. Contexto
- `jenkins/Dockerfile`: base `jenkins/jenkins:<LTS>-jdk21`; Terraform, TFLint y Trivy se copian de imágenes oficiales; AWS CLI por zip; Checkov en un Python 3.12 aislado (uv); plugins con `jenkins-plugin-cli`.
- La base cambia de sistema operativo y de Python entre LTS: lo que compilaba con una versión puede dejar de hacerlo.

## 3. Diagnóstico (solo lectura)
1. Identificar el paso que falla: `docker compose build jenkins --progress=plain 2>&1 | grep -E "ERROR|error|404|requires"`.
2. Según el mensaje:
   - `curl: (22) ... 404` -> la URL del binario ya no existe: `curl -sIL -o /dev/null -w '%{http_code}' <url>`.
   - `requires a greater version of Jenkins (X) than Y` -> los plugins "última versión" exigen un núcleo más nuevo.
   - `Failed building wheel for <paquete>` -> falta una rueda binaria para esa versión de Python (ver `python3 --version` de la imagen base).

## 4. Hipótesis
| Evidencia | Hipótesis | Qué la confirma |
|---|---|---|
| 404 al descargar un binario | La release se movió o se retiró | `curl -I` devuelve 404 pero la página de la release responde 200 |
| "requires a greater version of Jenkins" | Plugins sin versión fijada avanzaron | El mensaje cita la versión mínima del núcleo |
| "Failed building wheel" con Rust | Python de la base más nuevo que las ruedas publicadas | `pip` intenta compilar y pide un compilador de Rust |

## 5. Remediación (requiere aprobación del dueño del repo)
- 404 de binario -> copiar el binario desde la imagen oficial con versión fija (`COPY --from=<imagen>:<tag> <ruta> <destino>`). *Aplicado para Trivy, TFLint y Terraform.*
- Núcleo/plugins -> subir el núcleo a la LTS actual **o** fijar versiones de plugins. *Aplicado: núcleo 2.580.2.*
- Rueda no disponible -> instalar un Python compatible aislado (`uv venv --python 3.12`). *Aplicado para Checkov 3.2.255.*
- **Rollback:** `git revert` del commit que toca `jenkins/Dockerfile` y reconstruir.

## 6. Validación
- `docker compose build jenkins` termina en `Built`.
- `docker compose up -d --wait jenkins` queda `healthy`.
- `docker compose exec jenkins sh -c 'terraform version; tflint --version; trivy --version; checkov --version; aws --version'` imprime las cinco versiones.

## 7. Qué registrar
Paso que falló, mensaje exacto, causa, remediación aplicada y si hay que fijar la versión que provocó el cambio.

## Pendiente de este runbook
Los plugins de Jenkins siguen sin fijar por versión; es la causa más probable del próximo incidente.
