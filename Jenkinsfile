pipeline {
    agent any

    stages {

        stage('Deploy') {
            steps {
                echo "Uploading to PaaS"
        
                //sh "git clone ${params.github_url}/${params.project_name}-envs.git"
                
                if ("${params.environment}" == "production") {
                        env.app_space = "${params.paas_space}"
                        env.app_name = "${params.project_name}"
                    } else {
                        env.app_space = "${params.environment}-${params.paas_space}"
                        env.app_name = "${params.project_name}-${params.environment}"
                    }

                sh "cf login -a api.cloud.service.gov.uk -u ${params.cf_username} -p ${params.cf_password} -s ${env.app_space}"
                sh "cf set-env ${env.app_name} CHECK_INTERVAL 300"
                sh "cf push ${env.app_name}" 
            }
        }
    }
    
    post {
        success {
            //githubNotify(
                //status: "SUCCESS",
                //description: "Tests Passed",
                //credentialsId: "7ba5c792-f75d-471f-b8be-ec2535b4386f",
                //account: "uktrade",
                //repo: "pingdom-redirect-checker")
        }
        failure {
            //githubNotify(
                //status: "FAILURE",
                //description: "Tests Failed",
                //credentialsId: "7ba5c792-f75d-471f-b8be-ec2535b4386f",
                //account: "uktrade",
                //repo: "pingdom-redirect-checker")
        }
    }
}
