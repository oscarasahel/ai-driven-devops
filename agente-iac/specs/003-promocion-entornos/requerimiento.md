Queremos probar los cambios de infraestructura en un entorno de staging antes de tocar el entorno principal.
Staging vive en el mismo emulador, con otro prefijo de nombres y su propio estado, y no debe afectar a los recursos del entorno principal.
Solo se puede aplicar en el entorno principal el mismo código que ya se aplicó y verificó en staging.
Ambos entornos siguen exigiendo aprobación manual antes de cualquier apply o destroy.
