from django.http import HttpResponse
import json

from bs4 import BeautifulSoup
import requests

def video(request):
    page = request.GET.get('page', '1')
    cate = request.GET.get('c', '0')
    all = 'https://www.pornhub.com'
    if cate == '0':
        all = all + '/video'
    else:
        all = all + cate
    default = { "title": 'The Office',
        "img": 'https://ci.phncdn.com/videos/201704/10/112689871/original/(m=eGcEGgaaaa)(mh=n6ta7N7mmuoCxmVd)7.jpg',
        "src": 'https://www.pornhub.com/embed/ph58eb1cc594083' }
    qq = requests.get(all, params={'page': page})
    soup = BeautifulSoup(qq.text)
    videos = soup.find_all(class_='videoblock videoBox')
    results = []
    if page == '1' and cate == '0':
        results.append(default)
    for video in videos:
        vTitle = video.a['title']
        vURL = 'https://www.pornhub.com/embed/' + video.a['href'][24:]
        img = dict(video.img.attrs)
        vImg = ''
        for key in img:
            if key == 'data-mediumthumb':
                vImg = img[key]
        results.append({'title': vTitle, 'img': vImg, 'src': vURL})

    json_str = json.dumps(results)
    print(json_str)
    return HttpResponse(json_str, content_type="application/json")


def categories(request):
    cateUrl = 'https://www.pornhub.com/categories'
    cate = requests.get(cateUrl)
    soup = BeautifulSoup(cate.text)
    wrapper = soup.find_all(name='li', class_='cat_pic')
    results = []
    for wrap in wrapper:
        results.append({
            'category': wrap.div.a['alt'],
            'img': wrap.div.a.img['src'],
            'src': wrap.div.a['href']
        })
    json_str = json.dumps(results)
    print(json_str)
    return HttpResponse(json_str, content_type='application/json')

