from django.http import HttpResponse
import json

from bs4 import BeautifulSoup
import requests


# page=1
def pages(request):
    print(request)
    all = 'https://www.pornhub.com/video?page=' + request.GET['page']
    qq = requests.get(all)
    soup = BeautifulSoup(qq.text)
    videos = soup.find_all(class_='videoblock videoBox')
    results = []
    for video in videos:
        vTitle = video.a['title']
        vURL = 'https://www.pornhub.com/embed/' + video.a['href'][24:]
        img = dict(video.img.attrs)
        vImg = ''
        for key in img:
            if key == 'data-mediumthumb':
                vImg = img[key]
        results.append({'title': vTitle, 'img': vImg, 'src': vURL})
        print("##################################")

    json_str = json.dumps(results)
    print(json_str)
    return HttpResponse(json_str, content_type="application/json")