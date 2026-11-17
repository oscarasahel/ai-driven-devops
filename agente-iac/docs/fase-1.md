# Fase 1 – Infra base (verificada 2026-11-16)

## Cómo reproducir (PowerShell, desde `agente-iac/`)
```powershell
New-Item -ItemType Directory -Force .data/emulator | Out-Null
docker compose up -d --wait                          # emulador sano
docker compose run --rm terraform init
docker compose run --rm terraform validate
docker compose run --rm terraform apply              # pide confirmación (aprobación humana)
docker compose run --rm awscli s3 ls                 # debe listar agente-iac-smoke-test
docker compose run --rm terraform plan -detailed-exitcode   # exit 0 = sin cambios
docker compose run --rm terraform destroy            # limpieza
```

## Resultado real
- Emulador v1.0.485 (release 2026.11.17, commit a2568e8), imagen construida desde `emulator/Dockerfile`, healthcheck OK, puerto solo en 127.0.0.1.
- Terraform 1.9.8 (imagen fijada) + provider `hashicorp/aws` v5.100.0 (fijado en `.terraform.lock.hcl`).
- `apply` creó `agente-iac-smoke-test`; `awscli s3 ls` lo listó; segundo `plan` sin diferencias.

## Hallazgos que cierran pendientes de fase 0
- El provider funciona con HTTPS + CA propia usando solo variables de entorno `AWS_ENDPOINT_URL`, `AWS_CA_BUNDLE`, `AWS_SHARED_CREDENTIALS_FILE` (no hizo falta bloque `endpoints`). Con `s3_use_path_style = true`.
- La herramienta corre con `network_mode: service:aws-emulator`, por eso `127.0.0.1:9297` coincide con el certificado.
- Versión del emulador: sigue sin poder fijarse; queda registrada aquí (1.0.485).

## Nota sobre aprobación
En esta fase el `apply` de la prueba de humo se ejecutó con `-auto-approve` porque es un bucket desechable en un emulador local, bajo autorización explícita del usuario para trabajo autónomo. Desde la fase 5 el apply solo ocurre tras aprobación manual en Jenkins.

## Pendiente
- Fidelidad por servicio y lista oficial de servicios siguen sin verificarse (se revisa por servicio al elegir los requerimientos de la fase 2).
