from titanic_survival_project.webapp import app

c = app.app.test_client()
resp = c.get('/', follow_redirects=True)
print('Final URL status:', resp.status_code)
print('Final path snippet:', resp.request.path)
print('Content length:', len(resp.data))
