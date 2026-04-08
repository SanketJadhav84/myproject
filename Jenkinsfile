pipeline {
    agent any

    stages {

        stage('Clean old container') {
            steps {
                sh 'docker rm -f myapp-container || true'
                sh 'docker system prune -f || true'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t myprojectimg .'
            }
        }

        stage('Run Docker Container') {
            steps {
                sh 'docker-compose up -d --build'
            }
        }
    }
}