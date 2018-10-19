from aip import AipOcr
import requests


app_id = '10656098'
api_key = 'sonjIaozGNv4IlDpp4MU7xhv'
api_secrect = 'Oahe42EUYEyGd2FNG1ET4KMGK5jGt9sD'


def baidu_word_ocr(url):
    aipOcr = AipOcr(app_id, api_key, api_secrect)
    response = requests.get(url, timeout=3)
    result = aipOcr.basicGeneral(response.content)
    all_words = result["words_result"]
    content = ''
    if all_words:
        for words in all_words:
            content += words['words']
        return True, content
    else:
        return None, None
