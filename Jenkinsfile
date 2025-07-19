pipeline {
    agent any

    environment {
        VENV_PATH = "venv"
        MLFLOW_TRACKING_URI = 'http://ec2-13-233-192-43.ap-south-1.compute.amazonaws.com:5000/'
    }

    stages {
        stage('1. Install System Dependencies') {
            steps {
                sh '''
                    apt-get update && apt-get install -y \
                        python3 python3-venv python3-pip git curl unzip docker.io
                '''
            }
        }

        stage('2. Install AWS CLI') {
            steps {
                sh '''
                    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
                    unzip -q awscliv2.zip
                    ./aws/install
                    aws --version
                '''
            }
        }

        stage('3. Install Python and Create Venv') {
            steps {
                sh '''
                    python3 -m venv ${VENV_PATH}
                    ${VENV_PATH}/bin/pip install --upgrade pip
                '''
            }
        }

        stage('4. Clone GitHub Repo') {
            steps {
                echo 'Cloning GitHub repo to Jenkins...'
                checkout scmGit(branches: [[name: '*/master']], extensions: [], userRemoteConfigs: [[url: 'https://github.com/amitkumar981/mlflow_sagemaker_demo.git']])
            }
        }

        stage('5. Install Project Dependencies') {
            steps {
                sh '''
                    ${VENV_PATH}/bin/pip install -r requirements.txt
                '''
            }
        }

        stage('6. DVC Pull Data') {
            steps {
                withCredentials([
                    string(credentialsId: 'aws-access-key-id', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-access-key', variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    sh '''
                        ${VENV_PATH}/bin/dvc pull
                    '''
                }
            }
        }

        stage('7. DVC Reproduce Pipeline') {
            steps {
                withCredentials([
                    string(credentialsId: 'aws-access-key-id', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-access-key', variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    sh '''
                        ${VENV_PATH}/bin/dvc repro
                    '''
                }
            }
        }

        stage('8. Run Model Loading Test') {
            steps {
                withCredentials([
                    string(credentialsId: 'aws-access-key-id', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-access-key', variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    sh '''
                        ${VENV_PATH}/bin/pytest tests/test_model_loading.py
                    '''
                }
            }
        }

        stage('9. Run Model Performance Test') {
            steps {
                withCredentials([
                    string(credentialsId: 'aws-access-key-id', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-access-key', variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    sh '''
                        ${VENV_PATH}/bin/pytest tests/test_model_perf.py
                    '''
                }
            }
        }

        stage('10. Login to ECR') {
            steps {
                withCredentials([
                    string(credentialsId: 'aws-access-key-id', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-access-key', variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    sh '''
                        aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 565393027942.dkr.ecr.ap-south-1.amazonaws.com
                    '''
                }
            }
        }

        stage('11. Build Docker Image') {
            steps {
                sh '''
                    docker build -t swiggytimepredictor .
                '''
            }
        }

        stage('12. Tag Docker Image') {
            steps {
                sh '''
                    docker tag swiggytimepredictor:latest 565393027942.dkr.ecr.ap-south-1.amazonaws.com/swiggytimepredictor:latest
                '''
            }
        }

        stage('13. Push Docker Image to ECR') {
            steps {
                sh '''
                    docker push 565393027942.dkr.ecr.ap-south-1.amazonaws.com/swiggytimepredictor:latest
                '''
            }
        }
    }
}

