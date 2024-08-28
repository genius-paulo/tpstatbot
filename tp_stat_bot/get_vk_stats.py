from collections import defaultdict
from datetime import date
from dotenv import load_dotenv
from os import environ as env
import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import json

import requests
import time

load_dotenv()

USER_TOKEN = "vk1.a.GAb_DIxhbth_TaGXw-UsiObFyqaw9TgTKILpxr-BpRv4o8ZFzLJ0lhvIQbXz4iBdoyToM1d6zVEHNB5ZWwbPzIo4WnMnfBwi4saGiYK_Acr-HUmVyIov54VZVjMvK-ZMljX8WjMPSMq5hgvsaN5oygeYa5TJ7ZPN14ULfQ199YwDkiTwGMEw6-_ES_bYZXdwIpqzUrr6HxOetAfpwWbGaA"
API_VERSION = "5.199"
AD_STOPWORDS=["Реклама","партнерский","ивент","вакансии","рекламодатель"]

# Выделим записи за предыдущую неделю 
def previous_week_range(date):
    startDate = date + datetime.timedelta(-date.weekday(), weeks=-1) # Для сборки статы за месяц -4
    endDate = date + datetime.timedelta(-date.weekday() - 1)

    return startDate, endDate


def get_metrics(domain, ownerId):
    # Собираем посты за неделю с запасом
    response = requests.get('https://api.vk.com/method/wall.get',
            params={'access_token': USER_TOKEN,
                    'v': API_VERSION,
                    'domain': domain,
                    'count': 125,
                    'filter': 'owner'})

    
    data = response.json()['response']['items']

    output_file = 'output.json'

    # Запись данных в JSON-файл
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    # Заложим даты и ID постов в словарь
    posts = []

    for item in data:

        posts.append(
            {
                "id": item['id'],
                "date": item['date'],
                "likes": item['likes']['count'],
                "reposts": item['reposts']['count'],
                "comments": item['comments']['count'],
                "text": item["text"],
                "marked_as_ads": item["marked_as_ads"]
            })

    print(f"Постов с рекламой: {len(posts)}")

    # Уберем рекламные посты (где есть рекламный хэштег)
    noAdsPosts = []
    for item in posts:
        if any(x in item['text'] for x in AD_STOPWORDS):
            pass
        else:
            noAdsPosts.append(item)      

    # Уберем рекламные посты (где есть метка "Рекламная запись")
    noMarkedAdsPosts = []
    for item in noAdsPosts:
        if item['marked_as_ads'] == 1:
            pass
        else:
            noMarkedAdsPosts.append(item) 

    print(f"Постов без рекламы: {len(noMarkedAdsPosts)}")
    
    startDate, endDate = previous_week_range(date.today())
    print(f"Предыдущая неделя: {startDate} - {endDate}")

    startUnixDate = int(time.mktime(startDate.timetuple()))
    endUnixDate = int(time.mktime(endDate.timetuple())) + 86399 # 86399 + 1 секунд в дне

    # Для проверки исторического диапазона
    # startUnixDate = int(time.mktime(datetime.datetime(2024, 1, 8).timetuple()))
    # endUnixDate = int(time.mktime(datetime.datetime(2024, 1, 14).timetuple()))

    lastWeekPosts = [
        {
            "id": x["id"], 
            "date": x["date"],
            "likes": x["likes"], 
            "reposts": x["reposts"], 
            "comments": x["comments"]
        } for x in noMarkedAdsPosts if endUnixDate >= x['date'] >= startUnixDate]

    # Собираем ID постов за предыдущую неделю
    postIds = [d['id'] for d in lastWeekPosts]

    postIdsStr = ','.join(map(str, postIds))
    print("ID постов за предыдущую неделю: " + postIdsStr)

    # Получим стату об охвате постов
    response = requests.get('https://api.vk.com/method/stats.getPostReach',
            params={'access_token': USER_TOKEN,
                    'owner_id':f"-{ownerId}",
                    'post_ids': postIdsStr,
                    'v': API_VERSION})

    reachData = response.json()['response']
    
    reachDataPosts = []

    for item in reachData:
        reachDataPosts.append(
            {
                "id": item['post_id'],
                "reach_total": int(item['reach_total']) + int(item['links']),
                "links": item["links"]
            })

    # Объединим два списка словарей про посты по id
    d = defaultdict(dict)
    for l in (lastWeekPosts, reachDataPosts):
        for elem in l:
            d[elem['id']].update(elem)

    completePostsData = d.values()
    df = pd.DataFrame(completePostsData)

    # Выделим Медианный охват контентного поста
    reachMedian = df['reach_total'].median()
    text = "Медианный охват контентного поста: " + str(reachMedian) + "\n"

    df['likes'] = df['likes'].astype('int')
    df['reposts'] = df['reposts'].astype('int')
    df['comments'] = df['comments'].astype('int')
    df['links'] = df['links'].astype('int')

    df['reactions_total'] = df['likes'] + df['reposts'] + df['comments'] + df['links']

    # Выделим Медианное количество реакций 
    reactionsMedian = df['reactions_total'].median()
    text += "Медианное количество реакций: " + str(reactionsMedian) + "\n"

    # Получим Количество подписчиков
    response = requests.get('https://api.vk.com/method/groups.getMembers',
            params={'access_token': USER_TOKEN,
                    'group_id': ownerId,
                    'v': API_VERSION})

    # Подписчики
    subscribers = response.json()['response']['count']
    text += "Подписчиков: " + str(subscribers) + "\n"

    # Для проверки исторического диапазона
    # subscribers = 569340

    # Доля активной аудитории
    activeAudienceRate = reachMedian / subscribers * 100
    text += "Доля активной аудитории: " + str(activeAudienceRate) + "\n"

    # Доля вовлечённой аудитории
    engagedAudienceRate = reactionsMedian / reachMedian * 100
    text += "Доля вовлечённой аудитории: " + str(engagedAudienceRate) + "\n"

    text += "\n\n<b>Значения для вставки:</b>\n<code>" + str(subscribers) + "\n" + str(int(reachMedian)) + "\n" + str("%.2f" % activeAudienceRate) + "%" + "\n" + str(int(reactionsMedian)) + "\n" + ("%.2f" % engagedAudienceRate) + "%</code>" + "\n\n<i>Если бот помог вам, не забудьте мысленно отправить плюсик в карму Паше Ф. и Лене К.❤️</i>"

    return text
