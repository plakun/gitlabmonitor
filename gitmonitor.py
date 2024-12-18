from flask import Flask
import os
import requests
from git import Repo
import urllib3
import logging

app = Flask(__name__)
#private_token = os.environ["GITLAB_TOKEN"]
private_token = 'token'
gitlab_url = 'gitlab.example.com'
repo_path = 'devops/example.git'
repo_url = f"https://oauth2:{private_token}@{gitlab_url}/{repo_path}"
project_id = '105'  # ID проекта в GitLab
branch='master'

def git_clone():
    local_repo_path = f'./{os.path.basename(repo_url).split(".")[0]}'
    print(local_repo_path)
    if not os.path.exists(local_repo_path):
            print(f"Клонирование репозитория {repo_url}")
            Repo.clone_from(repo_url, local_repo_path, branch=branch, allow_unsafe_options=True)
            
        # Получаем объект репозитория
    repo = Repo(local_repo_path)
    return(repo)

def get_latest_commit_sha():
    """Получение SHA последнего коммита в удаленном репозитории"""
    headers = {
        'PRIVATE-TOKEN': private_token,
    }
    url = f'https://{gitlab_url}/api/v4/projects/{project_id}/repository/commits?ref_name={branch}'
    response = requests.get(url, headers=headers, verify=False)
    if response.status_code == 200:
        commits = response.json()
        if len(commits) > 0:
            return commits[0]['id']
        else:
            raise ValueError("Не удалось получить последние коммиты")
    else:
        raise RuntimeError(f"Ошибка при получении последних коммитов: статус-код {response.status_code}")

@app.route('/webhook', methods=['GET', 'POST', 'PUSH'])
def webhook():
    latest_remote_commit=get_latest_commit_sha()
    print('latest_remote_commit ', latest_remote_commit)
    try:
        local_head_commit = str(repo.head.commit.hexsha)
        print('local_head_commit ', local_head_commit)
        if latest_remote_commit != local_head_commit:
                print("Обнаружены новые изменения! Выполняем git pull...")
                repo.remotes.origin.pull()
                print("git pull выполнен")
        else:
            print("Нет новых изменений.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


    response = "hello"
    return response    


if __name__ == '__main__':
    urllib3.disable_warnings()
    repo=git_clone()
    logging.basicConfig(level=logging.DEBUG, filename="py_log.log",filemode="w", format="%(asctime)s %(levelname)s %(message)s")
    logging.debug("A DEBUG Message")
    logging.info("An INFO")
    logging.warning("A WARNING")
    logging.error("An ERROR")
    logging.critical("A message of CRITICAL severity")
    app.run(host='0.0.0.0', debug=True)
