// Spec 005: el pipeline y el código salen de Git (rama main por defecto) y un polling de 5 minutos lanza el build tras un merge.
// REPO_URL y REPO_BRANCH llegan del entorno del contenedor (ver docker-compose.yml); los valores por defecto son los de producción de la PoC.
// Lectura anónima por HTTPS: no hay credenciales en este archivo. Si el repo fuera privado, usar un token de solo lectura inyectado por entorno.
def repoUrl = System.getenv('REPO_URL') ?: 'https://github.com/oscarasahel/ai-driven-devops.git'
def repoBranch = System.getenv('REPO_BRANCH') ?: 'main'

pipelineJob('agente-iac') {
  description('validate -> lint -> security -> plan -> [aprobación manual] -> apply en el emulador -> pruebas de humo; staging verificado encola local')
  definition {
    cpsScm {
      scm {
        git {
          remote { url(repoUrl) }
          branches("*/${repoBranch}")
        }
      }
      scriptPath('agente-iac/jenkins/Jenkinsfile')
      lightweight(true)
    }
  }
  triggers {
    scm('H/5 * * * *')
  }
}
