import requests
import json
import time

if __name__ == '__main__':
    db = {}
    token = requests.get('https://opentdb.com/api_token.php?command=request').json()['token']
    while True:
        r = requests.get(f'https://opentdb.com/api.php?amount=50&token={token}')
        r_json = r.json()
        if 'results' not in r_json or len(r_json['results']) == 0:
            print('finished or rate limited', r.status_code)
            break
        results = r.json()['results']
        for result in results:
            db[result['question']] = result
        len_db = len(list(db.values()))
        # Heavy rate limiting in place: https://forums.pixeltailgames.com/t/download-rate-limited/49325
        time.sleep(5)
        print(f'Num questions fecthed: {len_db}')
    with open('db.json', 'w') as f:
        json.dump(list(db.values()), f)