Hoy hay que lanzar a mano el pipeline de Jenkins (scripts/jenkins.sh disparar ...) después de cada merge, y Jenkins trabaja con la carpeta local del equipo, no con lo que hay en GitHub.
Queremos que, después de fusionar un cambio en main, el pipeline se lance solo y quede lo más automatizado posible.
La aprobación humana antes de cualquier apply o destroy se mantiene.
