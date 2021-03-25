import requests


resp = requests.get('http://127.0.0.1:5000/users/8/')
print(resp.status_code)
print(resp.json())


resp = requests.post(
    'http://127.0.0.1:5000/users/',
    json={
        'username': 'Vasya',
        'password': 'vasya12345',
        'email': 'vasya@yandex.ru'
    }
)
print(resp.status_code)
print(resp.json())


resp = requests.post(
    'http://127.0.0.1:5000/ads/',
    json={
        'title': 'sfasf',
        'description': 'sfasdfascxv',
        'user_id': 8
    }
)
print(resp.status_code)
print(resp.json())
