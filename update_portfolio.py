import requests
import json
from datetime import datetime

# Configuration
GITHUB_USERNAME = "Erzan12"
OUTPUT_FILE = "index.html"

# Category mapping based on repository topics/names
CATEGORY_KEYWORDS = {
    'erp': ['erp', 'inventory', 'management-system'],
    'web': ['clinic', 'appointment', 'medical', 'qr', 'ltpms'],
    'games': ['game', 'unity', 'pygame'],
    'tools': ['api', 'restful', 'task-manager', 'expense', 'post-management', 'beginner']
}

def get_category(repo_name, topics, description):
    """Determine category based on repo name, topics, and description"""
    repo_lower = repo_name.lower()
    desc_lower = (description or '').lower()
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in repo_lower or keyword in desc_lower or keyword in topics:
                return category
    return 'tools'  # Default category

def get_tech_stack(languages, topics):
    """Extract tech stack from languages and topics"""
    tech_list = []
    
    # Add languages
    if languages:
        tech_list.extend(list(languages.keys())[:4])  # Limit to top 4 languages
    
    # Add relevant topics
    relevant_topics = [t for t in topics if t.lower() not in ['portfolio', 'project']]
    tech_list.extend(relevant_topics[:3])
    
    return ' &bull; '.join(tech_list[:5]) if tech_list else 'Code Repository'

def fetch_github_repos():
    """Fetch all public repositories from GitHub"""
    url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos"
    
    try:
        response = requests.get(url, params={'per_page': 100, 'sort': 'updated'})
        response.raise_for_status()
        repos = response.json()
        
        # Filter out forked repos and sort by updated date
        repos = [r for r in repos if not r['fork']]
        repos.sort(key=lambda x: x['updated_at'], reverse=True)
        
        return repos
    except Exception as e:
        print(f"Error fetching repos: {e}")
        return []

def generate_project_html(repos):
    """Generate HTML for project items"""
    project_html = []
    
    for repo in repos:
        # Fetch languages for the repo
        languages = {}
        try:
            lang_response = requests.get(repo['languages_url'])
            if lang_response.status_code == 200:
                languages = lang_response.json()
        except:
            pass
        
        # Get category and tech stack
        category = get_category(repo['name'], repo.get('topics', []), repo['description'])
        tech_stack = get_tech_stack(languages, repo.get('topics', []))
        
        # Determine link (homepage or repo URL)
        link_url = repo['homepage'] if repo['homepage'] else repo['html_url']
        link_text = "DEMO" if repo['homepage'] else "CODE"
        
        # Generate HTML - Updated to match enhanced template
        html = f'''
                <div class="project-item link-card bg-slate-800/30 border border-slate-700 hover:border-accent rounded-xl p-4" data-category="{category}">
                    <div class="flex justify-between items-start mb-2">
                        <div>
                            <h3 class="font-bold text-white text-sm uppercase">{repo['name'].replace('-', ' ')}</h3>
                            <span class="text-[10px] text-accent font-mono">{tech_stack}</span>
                        </div>
                        <a href="{link_url}" class="text-[10px] px-3 py-1.5 rounded-lg bg-gradient-to-r from-slate-700 to-slate-800 hover:from-accent hover:to-blue-500 hover:text-maritime transition-all font-bold border border-slate-600 hover:border-accent">{link_text}</a>
                    </div>
                    <p class="text-xs text-slate-400 leading-relaxed">{repo['description'] or 'No description provided'}</p>
                </div>
'''
        project_html.append(html)
    
    return '\n'.join(project_html)

def update_html_file(project_html):
    """Read the current HTML file and update the projects section"""
    try:
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Find the projects section - Updated markers for enhanced template
        start_marker = '<div class="grid grid-cols-1 gap-4">'
        end_marker = '</div>\n        </section>\n\n        <section class="w-full text-left pt-6 border-t border-slate-800 scroll-reveal">\n            <h2 class="text-2xl font-bold text-white mb-6 flex items-center gap-3">\n                <span class="text-accent"><i class="fas fa-code"></i></span>'
        
        start_idx = html_content.find(start_marker)
        end_idx = html_content.find(end_marker)
        
        if start_idx != -1 and end_idx != -1:
            # Replace the projects section
            new_content = (
                html_content[:start_idx + len(start_marker)] +
                '\n' + project_html + '\n            ' +
                html_content[end_idx:]
            )
            
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ Portfolio updated successfully at {datetime.now()}")
            return True
        else:
            print("❌ Could not find project section markers")
            print(f"Start marker found: {start_idx != -1}")
            print(f"End marker found: {end_idx != -1}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating HTML: {e}")
        return False

def main():
    print(f"🔄 Fetching repositories for {GITHUB_USERNAME}...")
    repos = fetch_github_repos()
    
    if repos:
        print(f"📦 Found {len(repos)} public repositories")
        print(f"📝 Repositories: {', '.join([r['name'] for r in repos[:5]])}{'...' if len(repos) > 5 else ''}")
        project_html = generate_project_html(repos)
        
        if update_html_file(project_html):
            print("✨ Done! Your portfolio has been updated.")
            print(f"📊 Updated with {len(repos)} projects")
        else:
            print("⚠️ Update failed - Check if index.html exists and has the correct structure")
    else:
        print("⚠️ No repositories found or API error occurred")

if __name__ == "__main__":
    main()