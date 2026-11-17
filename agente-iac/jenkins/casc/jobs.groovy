// El Jenkinsfile se copia en la imagen; el repo se monta en solo lectura en /repo.
pipelineJob('agente-iac') {
  description('validate -> lint -> security -> plan -> [aprobación manual] -> apply en el emulador -> pruebas de humo')
  definition {
    cps {
      script(new File('/usr/share/jenkins/Jenkinsfile').text)
      sandbox(true)
    }
  }
}
