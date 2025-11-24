@Library('pipeline-build') _

// Jenkinsfile for User API Service
// This pipeline builds the Python Flask API, creates Docker images, and publishes to registry

pipeline {
    agent any

    environment {
        APP_NAME = 'user-api'
        GIT_URL = 'https://github.com/example/user-api.git'
        BRANCH_NAME = "${env.BRANCH_NAME ?: 'main'}"
        NOTIFICATION_EMAIL = 'dev-team@example.com'
    }

    stages {
        stage('Build') {
            steps {
                script {
                    echo "Building User API Service..."

                    // Load the Python build pipeline from shared library
                    def pythonPipeline = load "../pipeline-build/Jenkinsfile.python"
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
