pipeline {
    agent any

    stages {

        stage('Deploy') {
            steps {
                echo 'Deploying....'
                //sh 'cf target -o dit-services -s webops'
                //sh 'cf set-env pingdom-redirect-checker CHECK_INTERVAL 300'
                //sh 'cf push pingdom-redirect-checker'
                sh 'sleep 10'
            }
        }
    }
    
    post {
        success {
            githubNotify(
                status: "SUCCESS",
                description: "Tests Passed",
                //credentialsId: "7ba5c792-f75d-471f-b8be-ec2535b4386f",
                //account: "uktrade",
                //repo: "pingdom-redirect-checker")
        }
        failure {
            githubNotify(
                status: "FAILURE",
                //description: "Tests Failed",
                //credentialsId: "7ba5c792-f75d-471f-b8be-ec2535b4386f",
                //account: "uktrade",
                //repo: "pingdom-redirect-checker")
        }
    }
}
