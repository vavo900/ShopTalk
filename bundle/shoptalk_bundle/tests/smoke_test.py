import requests, os
API=os.getenv('API','http://localhost:8000/search')
def test():
    r=requests.post(API,json={'query':'red shirt under 20 dollars'})
    assert r.status_code==200
    d=r.json(); assert 'answer' in d
    print('✓',d['answer'][:60],'...')
if __name__=='__main__': test()
