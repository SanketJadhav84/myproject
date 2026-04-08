pipeline {
    agent any

    stages {

        stage('Clean old container') {
            steps {
                sh 'docker rm -f myapp-container || true'
            }
        }

        stage('Clone Repository') {
            steps {
                git 'https://github.com/SanketJadhav84/myproject.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t myprojectimg .'
            }
        }

        stage('Run Docker Container') {
            steps {
                sh 'docker run -d -p 8080:8080 --name myapp-container myprojectimg'
            }
        }
    }
}