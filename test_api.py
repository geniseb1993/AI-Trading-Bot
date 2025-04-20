import requests

print('Testing API connection...')
try:
    r = requests.get('http://localhost:5000/api/test', timeout=2)
    print(f'API status: {r.status_code}, Response: {r.text}')
except Exception as e:
    print(f'API not running: {str(e)}') 