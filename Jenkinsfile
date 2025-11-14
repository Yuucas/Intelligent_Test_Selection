pipeline {
    agent any

    environment {
        PYTHON_VERSION = '3.9'
        ITS_THRESHOLD = '0.7'
    }

    stages {
        stage('Setup') {
            steps {
                echo 'Setting up environment...'
                sh '''
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Check Model') {
            steps {
                script {
                    def modelExists = fileExists('data/models/test_selector_model.pkl')
                    if (!modelExists) {
                        echo 'Model not found. Generating test history and training...'
                        sh 'python src/main.py --mode generate-history --num-runs 100'
                        sh 'python src/main.py --mode train'
                    } else {
                        echo 'Model already exists. Skipping training.'
                    }
                }
            }
        }

        stage('Intelligent Test Selection') {
            steps {
                echo 'Selecting tests with ITS...'
                sh "python src/main.py --mode select --threshold ${ITS_THRESHOLD}"
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running selected tests...'
                sh """
                    pytest --its-enabled --its-threshold ${ITS_THRESHOLD} \\
                           -v --cov --cov-report=html --cov-report=xml \\
                           --junitxml=test-results.xml
                """
            }
        }

        stage('Generate Report') {
            steps {
                echo 'Generating test selection report...'
                sh 'python src/main.py --mode report --output test_selection_report.md'
            }
        }
    }

    post {
        always {
            junit 'test-results.xml'

            publishHTML(target: [
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'htmlcov',
                reportFiles: 'index.html',
                reportName: 'Coverage Report'
            ])

            archiveArtifacts artifacts: 'test_selection_report.md, selected_tests.txt',
                             fingerprint: true

            echo 'Pipeline completed!'
        }

        success {
            echo 'Tests passed successfully!'
        }

        failure {
            echo 'Tests failed!'
        }
    }
}
