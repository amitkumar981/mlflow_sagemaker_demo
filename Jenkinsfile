pipeline {
    agent any

    environment {
        VENV_PATH = "venv"
        MLFLOW_TRACKING_URI = 'http://ec2-13-233-192-43.ap-south-1.compute.amazonaws.com:5000/'
    }

    stages {
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

        stage('Install Dependencies') {
            steps {
                echo 'Setting up virtual environment and installing dependencies...'
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate && \
                    pip install --upgrade pip && \
                    pip install --retries=5 --timeout=60 -r requirements.txt
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
                        . venv/bin/activate && \
                        export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID && \
                        export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY && \
                        dvc pull
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
                    echo 'Running model loading test...'
                    sh '''
                        . venv/bin/activate && \
                        export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID && \
                        export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY && \
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
                    echo 'Running model performance test...'
                    sh '''
                        . venv/bin/activate && \
                        export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID && \
                        export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY && \
                        pytest tests/test_model_perf.py
                    '''
                }
            }
        }
    }
}
