/* Global variables */
def manifests_folder = "./install/manifests"
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
  def exported_objs = null
  stage("Export promoted objects"){
    openshift.withCluster() {
      openshift.withProject() {
        // Uncomment for debug mode
        //openshift.verbose()
        def maps = openshift.selector(
                     'dc,svc,route,is,cm,pvc',
                     [ 'branch': 'master', 'promotion-group': 'api' ]
                   )
        exported_objs = maps.objects( exportable:true )

        // We must to clean objects...
        for ( obj in exported_objs ){
          obj.metadata.remove('annotations')
          obj.metadata.remove('namespace')
          switch (obj.kind) {
            case 'DeploymentConfig':
              for (ct in obj.spec.template.spec.containers){
                ct.image = " "
              }
              for (trigger in obj.spec.triggers){
                if (trigger.imageChangeParams != null){
                  trigger.imageChangeParams.from.remove('namespace')
                }
              }
              break
            case 'Service':
              break
            case 'Route':
              obj.spec.remove('host')
              break
            case 'ImageStream':
              obj.spec.tags = []
              break
            case 'ConfigMap':
              break
            case 'PersistentVolumeClaim':
              obj.spec.remove('volumeName')
              obj.spec.remove('storageClassName')
              break
          }
        }
      }
    }
  }
  stage("Import promoted objects"){
    withCredentials([usernamePassword(credentialsId: "${env.SRC_PROJECT}-env-${env.ENVIRONMENT}", usernameVariable: "DUMMY", passwordVariable: "SA_TOKEN")]) {
      openshift.withCluster(env.DST_CLUSTER_URL, env.SA_TOKEN){
        openshift.withProject(env.DST_PROJECT){
          echo "Importing objects"
          openshift.apply( exported_objs )
        }
      }
    }
  }
  stage("Promote to the next environment"){
    openshift.withCluster() {
      openshift.withProject() {
        def cfSelector = openshift.selector( "configmap", "promote-${env.ENVIRONMENT}-config" )
        if ( cfSelector.count() == 1 ) {
          echo "Promote is running"
          def isSelector = openshift.selector( "imagestream", [ "branch": env.GIT_BRANCH, "promotion-group": "api" ] )
          isSelector.withEach {
            def models = openshift.process("-f", "${manifests_folder}/promote.yaml",
              "-p", "GIT_BRANCH=${env.GIT_BRANCH}",
              "-p", "IMAGE_STREAM=${it.object().metadata.name}",
              "-p", "BUILD_NUMBER=${env.BUILD_NUMBER}",
              "-p", "ENVIRONMENT=${env.ENVIRONMENT}"
            )
            def created = openshift.apply( models )
          }
        }
        else {
          echo "Config not present for promotion"
        }
      }
    }
  }
  // Checker que les imagesstreams sont là
  withCredentials([usernamePassword(credentialsId: "${env.SRC_PROJECT}-env-${env.ENVIRONMENT}", usernameVariable: "DUMMY", passwordVariable: "SA_TOKEN")]) {
    openshift.withCluster(env.DST_CLUSTER_URL, env.SA_TOKEN){
      openshift.withProject(env.DST_PROJECT){
        stage("Check image promotion"){
          echo "Vérification de la présence des imagesstreams"
          def imagestreams = openshift.selector("imagestream", [ "branch": env.GIT_BRANCH, "promotion-group": "api" ] )
          imagestreams.describe()
          timeout(10){
            imagestreams.untilEach {
              def isOK = false
              try {
                echo "Cluster: ${openshift.cluster()}, project: ${openshift.project()}, image: ${it.object().metadata.name}:${env.BUILD_NUMBER} --> ${it.object().metadata.name}:latest, ok: ${isOK}"
                openshift.tag("${env.DST_PROJECT}/${it.object().metadata.name}:${env.BUILD_NUMBER}", "${env.DST_PROJECT}/${it.object().metadata.name}:latest")
                isOK = true
              } catch (Exception e) {}
              return isOK
            }
          }
        }
        stage("Check deployments"){
	  timeout(10) {
            def dc = openshift.selector('dc', [
              branch: "master"
            ])
            dc.withEach {
              def name = it.name().split('/')last()
              openshiftVerifyDeployment(name)
            }
          }
        }
        if (env.ENVIRONMENT != env.PRODUCTION_ENVIRONMENT_NAME) {
          // Do things related to non-prouction environments
          stage("tests"){
            echo "tests"
          }
        }
      }
    }
  }
}