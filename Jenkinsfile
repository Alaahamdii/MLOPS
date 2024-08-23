def getGitBranchName() { 
                return scm.branches[0].name 
            }
def branchName
def targetBranch

pipeline{
    agent any

    environment {
      DOCKERHUB_USERNAME = "hamdiiala"
      PROD_TAG = "${DOCKERHUB_USERNAME}/courzelo-course-attendance-prediction:v1.0.0-prod"

     
  }
     parameters {
       string(name: 'BRANCH_NAME', defaultValue: "${scm.branches[0].name}", description: 'Git branch name')
       string(name: 'CHANGE_ID', defaultValue: '', description: 'Git change ID for merge requests')
       string(name: 'CHANGE_TARGET', defaultValue: '', description: 'Git change ID for the target merge requests')
  }
    stages{

      stage('branch name') {
      steps {
        script {
          branchName = params.BRANCH_NAME
          echo "Current branch name: ${branchName}"
        }
      }
    }

    stage('target branch') {
      steps {
        script {
          targetBranch = branchName
          echo "Target branch name: ${targetBranch}"
        }
      }
    }
        stage('Git Checkout'){
            steps{
                git branch: 'main', credentialsId: 'AlaGitH', url: 'https://github.com/Alaahamdii/MLOPS.git'
	    }
        }
        

        stage('Install Dependencies') {
            steps {
                // Install required Python packages
                sh 'pip3 install -r requirements.txt'
            }
        }
           
         /*stage('Run Script') {
            steps {
                // Run the converted Python script and capture the output
                sh 'python3 train.py > output.log'
            }
        }*/
        stage('Build Docker') {
          when {
            expression {
              (params.CHANGE_ID != null)  && ((targetBranch == 'main') || (targetBranch == 'staging') || (targetBranch == 'develop'))
                      }
                }
            steps {
              script {     
                      sh "docker build -t ${PROD_TAG} ."
                  }
              }  
        }
        stage('Docker Login'){
          steps{
            withCredentials([usernamePassword(credentialsId: 'Ala_dockerHub', usernameVariable: 'DOCKERHUB_USERNAME', passwordVariable: 'DOCKERHUB_PASSWORD')]) {
              sh "docker login -u ${DOCKERHUB_USERNAME} -p ${DOCKERHUB_PASSWORD}"
            }
          }
        }

        stage('Docker Push'){
            steps{
                sh 'docker push $DOCKERHUB_USERNAME/courzelo-course-attendance-prediction --all-tags'
            }
        }

        stage('Deploy to Prod') {
      when {
        expression {
          (params.CHANGE_ID != null) && (targetBranch == 'develop')
        }
      }
      steps {
        sh "sudo ansible-playbook ansible/k8s.yml -i ansible/inventory/host.yml"
      }
    }

        stage('Publish HTML Report') {
            steps {
                publishHTML([allowMissing: false,
                             alwaysLinkToLastBuild: true,
                             keepAll: true,
                             reportDir: '.',
                             reportFiles: 'output.html',
                             reportName: 'HTML Report',
                             reportTitles: 'course_attendance_report'])
            }
        }
    }
}
    