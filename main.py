'''
Description: Editor's info in the top of the file
Author: p1ay8y3ar
Date: 2021-04-01 23:53:55
LastEditor: p1ay8y3ar
LastEditTime: 2021-04-06 11:55:42
Email: p1ay8y3ar@gmail.com
'''

from re import escape
import requests
from peewee import *
from datetime import datetime
import time
import random
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
        for _ in range(4):
            f.readline()

        old = f.read()
    new = new_contents + old
    with open("README.md", "w") as f:
        f.write(new)


def get_info(year):
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


def main():
    year = datetime.now().year
    sorted_list = []
    for i in range(year, 1999, -1):
        item = get_info(i)
        if item is None or len(item) == 0:
            continue
        print("{}年,获取原始数据:{}条".format(i, len(item)))
        sorted = db_match(item)
        if len(sorted) != 0:
            print("{}年,新更新{}条".format(i, len(sorted)))
            sorted_list.extend(sorted)
        count = random.randint(3, 10)
        time.sleep(count)
    # print(sorted_list)

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


if __name__ == "__main__":
    main()