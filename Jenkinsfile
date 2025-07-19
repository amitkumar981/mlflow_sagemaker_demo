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
                    ${VENV_PATH}/bin/pip install --upgrade pip
                '''
            }
        }

        stage('Clone GitHub Repo to Jenkins') {
            steps {
                echo 'Cloning GitHub repo to Jenkins...'
                checkout scmGit(branches: [[name: '*/master']], extensions: [], userRemoteConfigs: [[url: 'https://github.com/amitkumar981/mlflow_sagemaker_demo.git']])
            }
        }

        stage('Install Project Dependencies') {
            steps {
                sh '''
                    ${VENV_PATH}/bin/pip install -r requirements.txt
                '''
            }
        }

        stage('DVC Pull Data') {
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

        stage('DVC Reproduce Pipeline') {
            steps {
                withCredentials([
                    string(credentialsId: 'aws-access-key-id', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-access-key', variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    sh '''
                        . ${VENV_PATH}/bin/activate
                        ${VENV_PATH}/bin/dvc repro
                    '''
                }
            }
        }

        stage('DVC Push and Git Commit') {
            steps {
                withCredentials([
                    string(credentialsId: 'aws-access-key-id', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-access-key', variable: 'AWS_SECRET_ACCESS_KEY'),
                    string(credentialsId: 'github_token', variable: 'GITHUB_TOKEN')
                ]) {
                    sh '''
                        echo "Pushing DVC data to remote..."
                        ${VENV_PATH}/bin/dvc push

                        echo "Configuring Git..."
                        git config --global user.email "jenkins@yourdomain.com"
                        git config --global user.name "Jenkins"
                        git remote set-url origin https://x-access-token:${GITHUB_TOKEN}@github.com/amitkumar981/mlflow_sagemaker_demo.git

                        CURRENT_BRANCH=$(git symbolic-ref --short HEAD || echo "detached")

                        if [ "$CURRENT_BRANCH" != "master" ]; then
                            echo "Switching to master branch..."
                            git add .
                            git diff-index --quiet HEAD || git commit -m "Temp commit before switching to master"
                            git checkout master
                        fi

                        echo "Pulling latest changes from origin/master..."
                        git pull origin master --rebase

                        echo "Committing new changes (if any)..."
                        git add .
                        git diff-index --quiet HEAD || git commit -m "Update after DVC repro [automated]"

                        echo "Pushing to GitHub..."
                        git push origin master
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
                        ${VENV_PATH}/bin/pytest tests/test_model_loading.py
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
                        ${VENV_PATH}/bin/pytest tests/test_model_perf.py
                    '''
                }
            }
        }

        stage('Login to ECR') {
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

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build -t swiggytimepredictor .
                '''
            }
        }

        stage('Tag Docker Image') {
            steps {
                sh '''
                    docker tag swiggytimepredictor:latest 565393027942.dkr.ecr.ap-south-1.amazonaws.com/swiggytimepredictor:latest
                '''
            }
        }

        stage('Push Docker Image to ECR') {
            steps {
                sh '''
                    docker push 565393027942.dkr.ecr.ap-south-1.amazonaws.com/swiggytimepredictor:latest
                '''
            }
        }

        stage("Deploy the image on SageMaker") {
            steps {
                withCredentials([
                    string(credentialsId: 'aws-access-key-id', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-access-key', variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    sh '''
                        ${VENV_PATH}/bin/python deploy.py
                    '''
                }
            }
        }
    }
}
