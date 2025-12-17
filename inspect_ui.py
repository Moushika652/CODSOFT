import re
from titanic_survival_project.webapp import app

c = app.app.test_client()
# login
c.post('/login', data={'username':'admin','password':'admin'})
resp = c.get('/dashboard')
html = resp.data.decode('utf-8')

patterns = {
    'survived_male': r"Survived\s*—\s*Male\s*\((\d+)\)",
    'survived_female': r"Survived\s*—\s*Female\s*\((\d+)\)",
    'survived_child': r"Survived\s*—\s*Child\s*\((\d+)\)",
    'not_survived_male': r"Not survived\s*—\s*Male\s*\((\d+)\)",
    'not_survived_female': r"Not survived\s*—\s*Female\s*\((\d+)\)",
    'not_survived_child': r"Not survived\s*—\s*Child\s*\((\d+)\)",
}

results = {}
for k, p in patterns.items():
    m = re.search(p, html)
    results[k] = int(m.group(1)) if m else None

print('HTTP status:', resp.status_code)
for k, v in results.items():
    print(f'{k}:', v)

# print the 'By group' table snippet to verify HTML
m_table = re.search(r'By group:[\s\S]{0,400}', html)
if m_table:
    snippet = html[m_table.start():m_table.end()]
    print('\nSnippet around "By group":')
    print(snippet)
else:
    print('\nCould not find group table snippet in HTML.')
