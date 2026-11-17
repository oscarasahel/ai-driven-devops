# Genera grafana/dashboards/avance-por-sesion.json (dashboard como código). Uso, desde agente-iac/: python scripts/generar_dashboard.py
import json
DS={"type":"yesoreyeram-infinity-datasource","uid":"bitacora"}
def q(archivo,root,cols):
    return [{"datasource":DS,"refId":"A","type":"json","source":"url","parser":"backend","format":"table",
             "url":f"http://bitacora-web/{archivo}","url_options":{"method":"GET"},"root_selector":root,
             "columns":[{"selector":s,"text":t,"type":ty} for s,t,ty in cols]}]
def panel(i,title,typ,x,y,w,h,targets,opts=None,fc=None,desc=""):
    p={"id":i,"title":title,"type":typ,"datasource":DS,"gridPos":{"x":x,"y":y,"w":w,"h":h},"targets":targets,"description":desc,
       "fieldConfig":fc or {"defaults":{},"overrides":[]},"options":opts or {}}
    return p
tipo_colores={"defaults":{"custom":{"cellOptions":{"type":"color-text"}}},"overrides":[{"matcher":{"id":"byName","options":"Tipo"},"properties":[
 {"id":"mappings","value":[{"type":"value","options":{"SIMULADO":{"color":"orange","text":"SIMULADO"},"REAL":{"color":"green","text":"REAL"}}}]},
 {"id":"custom.cellOptions","value":{"type":"color-text"}}]}]}
cols_b=[("numero","#","number"),("fecha","Fecha","string"),("fase","Fase","string"),("tema","Tema","string"),("tipo","Tipo","string"),("rama","Rama","string"),("commit","Commit","string")]
dash={"uid":"avance-por-sesion","title":"Avance por sesión","tags":["agente-iac"],"timezone":"browser","schemaVersion":39,"version":1,
"refresh":"1m","time":{"from":"now-90d","to":"now"},"editable":False,"templating":{"list":[]},"annotations":{"list":[]},
"description":"Reales vs simuladas se distinguen en la columna Tipo. Fuente: bitacora/resumen.json (generado por scripts/bitacora.py).",
"panels":[
 panel(1,"Línea de tiempo de sesiones","table",0,0,24,9,q("resumen.json","bitacora",cols_b),
   {"showHeader":True,"sortBy":[{"displayName":"Fecha","desc":False}]},tipo_colores,
   "Una fila por sesión ordenada por fecha. SIMULADO = reconstruida, sin evidencia verificable."),
 panel(2,"Temas del curso: aplicados vs pendientes","piechart",0,9,8,8,
   q("resumen.json","totales",[("temas_aplicados","Aplicados","number"),("temas_pendientes","Pendientes","number")]),
   {"pieType":"donut","legend":{"displayMode":"list","placement":"bottom"},"reduceOptions":{"calcs":["lastNotNull"],"values":False}},
   {"defaults":{},"overrides":[{"matcher":{"id":"byName","options":"Aplicados"},"properties":[{"id":"color","value":{"mode":"fixed","fixedColor":"green"}}]},
                                  {"matcher":{"id":"byName","options":"Pendientes"},"properties":[{"id":"color","value":{"mode":"fixed","fixedColor":"orange"}}]}]},
   "Solo cuentan temas aplicados en sesiones reales."),
 panel(3,"Detalle de temas del curso","table",8,9,16,8,
   q("resumen.json","temas",[("id","Id","string"),("nombre","Tema","string"),("estado","Estado","string"),("sesiones","Sesiones reales","string")]),
   {"showHeader":True},{"defaults":{},"overrides":[{"matcher":{"id":"byName","options":"Estado"},"properties":[
     {"id":"mappings","value":[{"type":"value","options":{"aplicado":{"color":"green","text":"aplicado"},"pendiente":{"color":"orange","text":"pendiente"}}}]},
     {"id":"custom.cellOptions","value":{"type":"color-text"}}]}]}),
 panel(4,"Recursos Terraform por sesión","barchart",0,17,12,8,
   q("resumen.json","recursos_por_sesion",[("tema","Sesión","string"),("recursos_terraform","Recursos Terraform","number")]),
   {"xField":"Sesión","legend":{"displayMode":"list","placement":"bottom"},"orientation":"auto","showValue":"auto"},None,
   "Recursos Terraform gestionados al cierre de cada sesión (métrica registrada, no inferida)."),
 panel(5,"Hallazgos de seguridad por severidad (antes / después)","barchart",12,17,12,8,
   q("resumen.json","hallazgos",[("severidad","Severidad","string"),("antes","Antes","number"),("despues","Después","number")]),
   {"xField":"Severidad","legend":{"displayMode":"list","placement":"bottom"},"orientation":"auto","showValue":"auto"},None,
   "Fase 4: 'alta' viene de Trivy; Checkov y TFLint no informan severidad. Después = tras corregir o documentar excepciones."),
 panel(6,"Estado del último pipeline","stat",0,25,8,5,
   q("resumen.json","pipeline",[("estado","Estado","string"),("detalle","Detalle","string")]),
   {"textMode":"value","colorMode":"background","reduceOptions":{"calcs":["lastNotNull"],"fields":"/^Estado$/","values":False}},
   {"defaults":{"mappings":[{"type":"value","options":{"ok":{"color":"green","text":"OK"},"fallido":{"color":"red","text":"FALLIDO"},"no verificado":{"color":"orange","text":"NO VERIFICADO"}}}]},"overrides":[]},
   "Se actualiza en bitacora/sesiones.json (campo pipeline.estado)."),
 panel(7,"Bitácora (reales y simuladas)","table",8,25,16,5,q("resumen.json","bitacora",cols_b),{"showHeader":True},tipo_colores),
]}
json.dump(dash,open("grafana/dashboards/avance-por-sesion.json","w",encoding="utf-8"),ensure_ascii=False,indent=2)
