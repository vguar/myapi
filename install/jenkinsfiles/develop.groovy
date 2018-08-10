/* Global variables */
def manifests_folder = "./install/manifests"
def new_project = true
def url = ''
def project_name = 'vga-api'
def job_name = 'vga-api'

node ("python27") {
  /* Source git */
  stage("Git clone"){
    deleteDir()
    checkout scm
    url = sh(returnStdout: true, script: 'git config remote.origin.url').trim()
  }

  /* Check syntax */
  stage("Run pep8 test"){
    output = sh(returnStdout: true, script: 'pycodestyle consumer*').trim()
    println output
  }

  /* Common services */
  stage("Deploy route + service + redis"){
    openshift.withCluster() {
      openshift.withProject( ) {
        def models = openshift.process("-f", "${manifests_folder}/services.yaml",
          "-p", "GIT_BRANCH=${env.GIT_BRANCH}"
        )
        def created = openshift.apply( models )
        openshiftVerifyDeployment( created.narrow('dc').name().split('/')[1] )
      }
    }
  }

  /* API front */
  stage("Build and deploy api front"){
    openshift.withCluster() {
      openshift.withProject() {
        def api_tpl = openshift.process("-f", "${manifests_folder}/api.yaml",
          "-p", "GIT_URL=" + url,
          "-p", "GIT_BRANCH=${env.GIT_BRANCH}"
        )
        def api_created = openshift.apply( api_tpl )
        openshiftBuild(api_created.narrow("bc").name().split('/')[1])
      }
    }
  }

  /* Manage configmap */
  stage("Initialize configmap"){
    openshift.withCluster() {
      openshift.withProject( ) {
        def cfSelector = openshift.selector( "configmap", "config-${env.GIT_BRANCH}" )
        if ( cfSelector.count() == 0 ){
          echo "Creation of configmap"
          def models = openshift.process("-f", "${manifests_folder}/config.yaml",
            "-p", "GIT_BRANCH=${env.GIT_BRANCH}"
          )
          def created = openshift.apply( models )
        }
        else {
          echo "Configmap already exist"
        }
      }
    }
  }

  /* Consumers */
  def consumers = []
  findFiles().findAll({ return (it.directory && it.name.contains("consumer-")) }).each{
      consumers << it.name.split("-")[1]
  }
  consumers.each { consumer ->
    stage("Build and deploy ${consumer} consumer"){
      openshift.withCluster() {
        openshift.withProject() {
          def consumer_tpl = openshift.process("-f", "${manifests_folder}/consumer.yaml",
            "-p", "CONSUMER_NAME=" + consumer,
            "-p", "GIT_URL=" + url,
            "-p", "GIT_BRANCH=${env.GIT_BRANCH}"
          )
          def consumer_created = openshift.apply( consumer_tpl )
          openshiftBuild(consumer_created.narrow("bc").name().split('/')[1])
        }
      }
    }
  }

  /* Deploy check */
  stage("Check deployments completion"){
    openshift.withCluster() {
      openshift.withProject() {
        timeout(10) {
          def dc = openshift.selector('dc', [
            app: "${env.GIT_BRANCH}",
            branch: "${env.GIT_BRANCH}"
          ])
          dc.withEach {
            def name = it.name().split('/')last()
            openshiftVerifyDeployment(name)
          }
        }
      }
    }
  }
}