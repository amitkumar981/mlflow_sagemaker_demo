pipeline {
    agent any

    stages {
        stage('Clone GitHub Repo to Jenkins') {
            steps {
                script {
                    echo 'Cloning GitHub repo to Jenkins...'
                    checkout([$class: 'GitSCM',
                        branches: [[name: '*/master']],
                        extensions: [],
                        userRemoteConfigs: [[
                            credentialsId: 'github-token',
                            url: 'https://github.com/amitkumar981/mlflow_sagemaker_demo.git'
                        ]]
                    ])
                }
            }
        }

        stage('Run DVC Pipeline') {
            steps {
                script {
                    echo 'Running DVC pipeline......'
                    sh 'dvc repro'
                }
            }
        }
    }
}
