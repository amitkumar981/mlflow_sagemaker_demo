pipeline {
    agent any

    environment {
        VENV_PATH = "venv"
    }

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

        stage('Install Dependencies') {
            steps {
                script {
                    echo 'Setting up virtual environment and installing dependencies...'
                    sh '''
                        python3 -m venv venv
                        . venv/bin/activate && \
                        pip install --upgrade pip && \
                        pip install --retries=5 --timeout=60 -r requirements.txt
                    '''
                }
            }
        }

        stage('Run Model Loading Test') {
            steps {
                script {
                    echo 'Running model loading test...'
                    sh '''
                        . venv/bin/activate && \
                        python tests/run_model_loading.py
                    '''
                }
            }
        }

        stage('Run Model Performance Test') {
            steps {
                script {
                    echo 'Running model performance test...'
                    sh '''
                        . venv/bin/activate && \
                        python tests/test_model_perf.py
                    '''
                }
            }
        }
    }
}
