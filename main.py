'''
Description: Editor's info in the top of the file
Author: p1ay8y3ar
Date: 2021-04-01 23:53:55
LastEditor: p1ay8y3ar
LastEditTime: 2021-04-07 13:26:50
Email: p1ay8y3ar@gmail.com
'''

import requests
from peewee import *
from datetime import datetime
import time
import random
import math
db = SqliteDatabase("cve.sqlite")


class CVE_DB(Model):
    id = IntegerField()
    full_name = CharField(max_length=1024)
    description = CharField(max_length=4098)
    url = CharField(max_length=1024)
    created_at = CharField(max_length=128)

    class Meta:
        database = db


db.connect()
db.create_tables([CVE_DB])


def write_file(new_contents):
    with open("README.md") as f:
        #去除标题
        for _ in range(7):
            f.readline()

        old = f.read()
    new = new_contents + old
    with open("README.md", "w") as f:
        f.write(new)


def craw_all():
    # 这是爬取所有的,github api限制每分钟请求最多30次
    api = "https://api.github.com/search/repositories?q=CVE-{}&sort=updated&per_page=100&page={}"
    item_list = []
    for i in range(1999, 2022, 1):
        try:
            reqtem = requests.get(api.format(i, 1)).json()
            total_count = reqtem["total_count"]
            print("{}年,共{}条".format(i, total_count))
            for_count = math.ceil(total_count / 100) + 1
            time.sleep(random.randint(3, 15))
        except Exception as e:
            print("请求数量的时候发生错误", e)
            continue

        for j in range(1, for_count, 1):
            try:
                req = requests.get(api.format(i, j)).json()
                items = req["items"]
                item_list.extend(items)
                print("{}年，第{}轮，爬取{}条".format(i, j, len(items)))
                time.sleep(random.randint(3, 15))
            except Exception as e:
                print("网络发生错误", e)
                continue

    return item_list


def get_info(year):
    # 监控用的
    try:

        api = "https://api.github.com/search/repositories?q=CVE-{}&sort=updated".format(
            year)
        # 请求API
        req = requests.get(api).json()
        items = req["items"]

        return items
    except Exception as e:
        print("网络请求发生错误", e)
        return None


def db_match(items):
    r_list = []
    for item in items:
        id = item["id"]
        if CVE_DB.select().where(CVE_DB.id == id).count() != 0:
            continue
        full_name = item["full_name"]
        description = item["description"]
        if description == "" or description == None:
            description = 'no description'
        else:
            description = description.strip()
        url = item["html_url"]
        created_at = item["created_at"]
        r_list.append({
            "id": id,
            "full_name": full_name,
            "description": description,
            "url": url,
            "created_at": created_at
        })
        CVE_DB.create(id=id,
                      full_name=full_name,
                      description=description,
                      url=url,
                      created_at=created_at)

    return sorted(r_list, key=lambda e: e.__getitem__('created_at'))


def update_all():
    sorted_list = craw_all()
    sorted = db_match(sorted_list)
    if len(sorted) != 0:
        print("更新{}条".format(len(sorted)))
        sorted_list.extend(sorted)
    newline = ""
    for s in sorted_list:
        line = "**{}** : [{}]({})  create time: {}\n\n".format(
            s["description"], s["full_name"], s["url"], s["created_at"])
        newline = line + newline
    print(newline)
    if newline != "":
        newline = "# Automatic monitor github cve using Github Actions \n\n > update time: {}  total: {} \n\n".format(
            datetime.now(),
            CVE_DB.select().where(CVE_DB.id != None).count()) + newline

        write_file(newline)


def main():
    # 下面是监控用的
    year = datetime.now().year
    sorted_list = []
    for i in range(year, 1999, -1):
        item = get_info(i)
        if item is None or len(item) == 0:
            continue
        print("{}年,获取原始数据:{}条".format(i, len(item)))
        sorted = db_match(item)
        if len(sorted) != 0:
            print("{}年,更新{}条".format(i, len(sorted)))
            sorted_list.extend(sorted)
        count = random.randint(3, 15)
        time.sleep(count)
    # print(sorted_list)

    newline = ""
    for s in sorted_list:
        line = "**{}** : [{}]({})  create time: {}\n\n".format(
            s["description"], s["full_name"], s["url"], s["created_at"])
        newline = line + newline
    print(newline)
    if newline != "":
        newline = "# Automatic monitor github cve using Github Actions \n\n > update time: {}  total: {} \n\n \n ![star me](https://img.shields.io/badge/star%20me-click%20--%3E-orange) [cve monitor](https://github.com/p1ay8y3ar/cve_monitor)  [Browsing through the web](https://p1ay8y3ar.github.io/cve_monitor/) \n\n".format(
            datetime.now(),
            CVE_DB.select().where(CVE_DB.id != None).count()) + newline

        write_file(newline)


if __name__ == "__main__":
    # update_all()
    main()