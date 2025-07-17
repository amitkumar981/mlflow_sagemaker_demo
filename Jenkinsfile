pipeline{
    agent any

    stages{
        stage('clone github repo to jenkins'){
            steps{
                scripts{
                    echo 'cloning git hub  repro to jenkins......'
                    checkout scmGit(branches: [[name: '*/master']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/amitkumar981/mlflow_sagemaker_demo.git']])
                }
            }
        }
    }
}