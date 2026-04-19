import requests

BASE_URL = 'http://localhost:8000'
URL = 'https://en.wikipedia.org/wiki/Artificial_intelligence'

print('Testing health...')
r = requests.get(f'{BASE_URL}/')
print(f'Health: {r.status_code} {r.json()}')

print('\nTesting /analyze...')
payload = {'url': URL}
r = requests.post(f'{BASE_URL}/analyze', json=payload)
print(f'Analyze setup: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    print(f"Title: {data['title']}")
    print(f"Summary: {data['summary'][:100]}...")
    
    print('\nTesting /ask...')
    ask_payload = {'article_text': data['text'], 'question': 'What is the main topic?'}
    r2 = requests.post(f'{BASE_URL}/ask', json=ask_payload)
    print(f'Ask status: {r2.status_code}')
    if r2.status_code == 200:
        print(f"Answer: {r2.json()['answer']}")
    else:
        print(f'Ask failed: {r2.text}')
else:
    print(f'Analyze failed: {r.text}')
