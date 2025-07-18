pipeline {
    agent any

    environment {
        VENV_PATH = "venv"
        MLFLOW_TRACKING_URI = 'http://ec2-13-233-192-43.ap-south-1.compute.amazonaws.com:5000/'
    }

    stages {
        stage('Install Python and Dependencies') {
            steps {
                echo 'Installing Python3 and dependencies...'
                sh '''
                    apt-get update && apt-get install -y python3 python3-venv python3-pip git curl
                    python3 -m venv ${VENV_PATH}
                    . ${VENV_PATH}/bin/activate
                    pip install --upgrade pip
                '''
            }
        }

        stage('Clone GitHub Repo to Jenkins') {
            steps {
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

        stage('Install Project Dependencies') {
            steps {
                sh '''
                    . ${VENV_PATH}/bin/activate
                    pip install -r requirements.txt
                '''
            }
        }

        stage('DVC Pull Data') {
            steps {
                withCredentials([
                    string(credentialsId: 'aws-access-key-id', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-access-key', variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    echo 'Pulling data from DVC remote (S3)...'
                    sh '''
                        . ${VENV_PATH}/bin/activate
                        dvc pull
                    '''
                }
            }
        }

        stage('DVC Reproduce Pipeline') {
            steps {
                withCredentials([
                    string(credentialsId: 'aws-access-key-id', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-access-key', variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    echo 'Reproducing DVC pipeline...'
                    sh '''
                        . ${VENV_PATH}/bin/activate
                        dvc repro
                    '''
                }
            }
        }

        stage('Run Model Loading Test') {
            steps {
                withCredentials([
                    string(credentialsId: 'aws-access-key-id', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-access-key', variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    sh '''
                        . ${VENV_PATH}/bin/activate
                        pytest tests/test_model_loading.py
                    '''
                }
            }
        }

        stage('Run Model Performance Test') {
            steps {
                withCredentials([
                    string(credentialsId: 'aws-access-key-id', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-access-key', variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    sh '''
                        . ${VENV_PATH}/bin/activate
                        pytest tests/test_model_perf.py
                    '''
                }
            }
        }
    }
}

