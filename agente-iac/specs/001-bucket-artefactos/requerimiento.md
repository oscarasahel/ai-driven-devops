Necesitamos un bucket S3 para guardar los artefactos de build de nuestro pipeline.
Debe ser privado, cifrado y con versionado, para poder recuperar versiones previas.
Los artefactos de más de 30 días se pueden borrar; las versiones antiguas, a los 7 días.
Solo debe aceptar conexiones por HTTPS.
Además, un rol de IAM que use el pipeline para leer y escribir artefactos solo en ese bucket, sin acceso a nada más.
Todo con las etiquetas project, env y owner.
