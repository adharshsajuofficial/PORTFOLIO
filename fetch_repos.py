import json
import os
import urllib.request

# Define your GitHub target config
GITHUB_USERNAME = "adharshsajuofficial"  # Replace with your exact GitHub Username

def fetch_github_repositories():
    url = f"https://api.github.com/users/adharshsajuofficial/repos?sort=updated&per_page=100"
    
    # Set up Request with proper Headers to avoid API rate limits
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Python-Urllib-Automation')
    
    # If working inside GitHub Actions runner environments, use safe tokens
    token = os.getenv('GITHUB_TOKEN')
    if token:
        req.add_header('Authorization', f'token {token}')

    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                return json.loads(response.read().decode())
            else:
                print(f"API Error: Status code {response.status}")
                return []
    except Exception as e:
        print(f"Error connecting to GitHub API: {e}")
        return []

def categorize_repo(repo):
    """
    Intelligently assigns categories ('web', 'code', 'design') 
    based on project names, descriptions, or primary languages.
    """
    name = repo.get('name', '').lower()
    desc = (repo.get('description') or '').lower()
    lang = (repo.get('language') or '').lower()
    
    # Categorization matching conditions
    if 'design' in name or 'prototype' in name or 'figma' in desc:
        return 'design'
    elif lang in ['html', 'css', 'javascript', 'typescript'] or 'nextrack' in name or 'web' in name:
        return 'web'
    else:
        return 'code' # Default fallback for Python, C, C++, backend logic scripts

def main():
    print(f"Starting repository sweep for user: {GITHUB_USERNAME}...")
    raw_repos = fetch_github_repositories()
    
    if not raw_repos:
        print("No repository data retrieved. Process aborted.")
        return

    processed_projects = []
    
    for repo in raw_repos:
        # Ignore forked repositories to keep your portfolio focused purely on your source code
        if repo.get('fork', False):
            continue
            
        project_data = {
            "name": repo.get('name'),
            "description": repo.get('description'),
            "html_url": repo.get('html_url'),
            "language": repo.get('language'),
            "category": categorize_repo(repo),
            "updated_at": repo.get('updated_at')
        }
        processed_projects.append(project_data)

    # Output data directly onto static production file layer
    output_path = 'projects.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(processed_projects, f, indent=4, ensure_ascii=False)
        
    print(f"Success! Compiled {len(processed_projects)} repos into '{output_path}'.")

if __name__ == '__main__':
    main()