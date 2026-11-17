---
name: bitacora
description: Registra una sesión de trabajo (fase, tema, archivos, decisiones, evidencia, métricas, riesgos) en la bitácora y regenera BITACORA.md, la ficha sesion-NN-*.md y bitacora.json para Grafana. Úsala al cerrar cada fase o sesión. Nunca registra como real lo que no se ejecutó.
---

# bitacora

## Cuándo usarla
Al terminar una fase o sesión, **después** de commitear: la evidencia exige un commit que ya exista.

## Entradas
Un JSON con una sesión (ver las existentes en `bitacora/sesiones.json`): `numero, fecha, fase, tema, slug, rama, simulado, temas_curso[], objetivo, archivos[], decisiones[{decision,porque}], evidencia[{tipo,ref,detalle}], metricas{}, riesgos[], siguiente`.
Rutas de `archivos` y de evidencia tipo `archivo` son relativas a la raíz del repo. Evidencia tipo `commit` lleva el SHA.

## Pasos
1. Commitear el trabajo de la sesión.
2. Escribir el JSON de la sesión con el SHA real y las métricas reales (no estimadas).
3. `python scripts/bitacora.py agregar <archivo.json>` (valida y regenera).
4. `python scripts/bitacora.py validar` debe terminar en OK.
5. Commitear `bitacora/sesiones.json`, `BITACORA.md` y la ficha nueva.

## Reglas de veracidad (impuestas en código por `scripts/bitacora.py`)
- Sesión real: debe tener al menos un commit existente en git y archivos existentes; si no, **no se agrega**.
- Sesión simulada o reconstruida: va en `bitacora/simuladas.local.json` con `simulado: true`, sin commits; se distingue en Grafana.
- Si algo no se verificó (p. ej. un pipeline sin ejecutar), dilo en `riesgos` y en `metricas` (`pipeline_verificado: false`).
- Sin secretos ni datos reales. `bitacora/bitacora.json` y las simuladas son locales (confidenciales, ignorados por git).
