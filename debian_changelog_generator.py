# debian_changelog_generator.py
import requests
import os
import re
from datetime import datetime

def get_existing_entries():
    existing = {'commits': set(), 'prs': set()}
    if os.path.exists('debian/changelog'):
        with open('debian/changelog', 'r') as f:
            content = f.read()
            existing['commits'] = set(re.findall(r'\b[0-9a-f]{7}\b', content))
            existing['prs'] = set(re.findall(r'#(\d+)', content))
    return existing

def generate_debian_changelog():
    repo_owner = input("GitHub owner/organization: ")
    repo_name = input("Repository name: ")
    
    # Domyślne wartości
    package = repo_name
    version = "0.1.0"
    distribution = "unstable"
    urgency = "medium"
    maintainer = "Maintainer <maintainer@example.com>"
    
    # Pobierz istniejące wpisy
    existing = get_existing_entries()
    
    # Zbierz nowe zmiany
    changes = []
    
    try:
        # Pobierz commity
        commits = requests.get(
            f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits"
        ).json()
        
        for commit in commits:
            sha_short = commit['sha'][:7]
            if sha_short not in existing['commits']:
                msg = commit['commit']['message'].split('\n')[0]
                changes.append(f"  * [_{sha_short}_] {msg}")

        # Pobierz PR
        pulls = requests.get(
            f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls?state=closed"
        ).json()
        
        for pr in pulls:
            if str(pr['number']) not in existing['prs']:
                changes.append(f"  * #_{pr['number']}_ {pr['title']}")

        if not changes:
            print("Brak nowych zmian do dodania")
            return

        # Stwórz nagłówek
        date = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")
        header = f"{package} ({version}) {distribution}; urgency={urgency}\n"
        footer = f"\n -- {maintainer}  {date}\n"

        # Zapisz z zachowaniem istniejącej zawartości
        os.makedirs('debian', exist_ok=True)
        with open('debian/changelog', 'a+') as f:
            f.seek(0)
            content = f.read()
            f.seek(0, 0)
            f.write(header + '\n'.join(changes) + footer + '\n' + content)
            
        print("Zaktualizowano debian/changelog")

    except Exception as e:
        print(f"Błąd: {str(e)}")

if __name__ == "__main__":
    generate_debian_changelog()
