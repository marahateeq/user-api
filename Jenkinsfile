// Jenkinsfile for User API Service
// This pipeline builds the Python Flask API, creates Docker images, and publishes to registry

pipeline {
    agent any

    environment {
        APP_NAME = 'user-api'
        GIT_URL = 'https://github.com/marahateeq/user-api.git'
        BRANCH_NAME = "${env.BRANCH_NAME ?: 'main'}"
        NOTIFICATION_EMAIL = 'yuseffathi@gmail.com,marahateeq@gmail.com'
        SHARED_LIB_REPO = 'https://github.com/marahateeq/pipeline-build.git'
        SHARED_LIB_BRANCH = '*/main'
        SHARED_LIB_DIR = 'pipeline-build'
        SHARED_LIB_CREDENTIALS = ''
    }

    stages {
        stage('Fetch Shared Library') {
            steps {
                script {
                    if (!env.SHARED_LIB_REPO?.trim()) {
                        error "SHARED_LIB_REPO is not defined"
                    }

                    def branchRef = env.SHARED_LIB_BRANCH?.trim() ?: '*/main'
                    def targetDir = env.SHARED_LIB_DIR?.trim() ?: 'pipeline-build'
                    def userRemote = [url: env.SHARED_LIB_REPO.trim()]

                    if (env.SHARED_LIB_CREDENTIALS?.trim()) {
                        userRemote.credentialsId = env.SHARED_LIB_CREDENTIALS.trim()
                    }

                    dir(targetDir) {
                        checkout([
                            $class: 'GitSCM',
                            branches: [[name: branchRef]],
                            doGenerateSubmoduleConfigurations: false,
                            extensions: [[$class: 'CleanBeforeCheckout']],
                            submoduleCfg: [],
                            userRemoteConfigs: [userRemote]
                        ])
                    }
                }
            }
        }

        stage('Build') {
            steps {
                script {
                    echo "Building User API Service..."

                    // Load the Python build pipeline from shared library
                    def libDir = env.SHARED_LIB_DIR?.trim() ?: 'pipeline-build'
                    def pythonPipeline = load "${libDir}/Jenkinsfile.python"
                    pythonPipeline.executePipeline()
                }
            }
        }
    }

    post {
        success {
            echo "✅ User API build completed successfully"
        }
        failure {
            echo "❌ User API build failed"
        }
    }
}
