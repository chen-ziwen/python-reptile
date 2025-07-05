import os
import re

import requests


# 目标网站： https://lol.qq.com/main.shtml
# 目标： 爬取英雄联盟所有皮肤 （可以拿到最新的皮肤）

class LOLThemeScraper(object):

    def __init__(self):
        """ 获取英雄联盟所有皮肤 """
        self.role_url = "https://game.gtimg.cn/images/lol/act/img/js/heroList/hero_list.js"
        self.skin_url_base = "https://game.gtimg.cn/images/lol/act/img/js/hero/"
        self.skin_folder = "skin"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
        }

    @staticmethod
    def format_skin_name(name):
        """ 处理皮肤名称 """
        return re.sub(r'[\\/:*?"<>|]', '', name.strip())

    def get_role_data(self):
        req = requests.get(self.role_url, headers=self.headers).json()

        return [{
            "name": role["name"],
            "alias": role["alias"],
            "keywords": role["keywords"],
            "heroId": role["heroId"]
        } for role in req.get("hero", [])]

    def get_skin_data(self, url):
        """ 获取皮肤信息 """
        req = requests.get(url, headers=self.headers).json()

        skin_list = []

        for skin in req["skins"]:
            img_url = skin["centerImg"] or skin["mainImg"]
            if img_url:
                skin_list.append({"img_url": img_url, "name": skin["name"]})

        return skin_list

    def download_skin(self, skin):
        """ 下载皮肤 """
        img_name = self.format_skin_name(skin["name"])
        try:
            request = requests.get(skin["img_url"], headers=self.headers)
            img_path = os.path.join(self.skin_folder, f'{img_name}.jpg')
            with open(img_path, "wb") as img:
                img.write(request.content)
                print(f"已下载 {img_name}")
        except Exception as e:
            print(f"图片下载失败 {img_name}:{e}")

    def mk_folder(self):
        """ 创建一个保存图片的文件夹 """
        if not os.path.exists(self.skin_folder):
            os.mkdir(self.skin_folder)

    def get_all_skin(self):
        # 创建文件夹
        scraper.mk_folder()
        # 获取角色信息
        roles = self.get_role_data()

        for role in roles:
            skin_url = self.skin_url_base + f"{role['heroId']}.js"
            skins = self.get_skin_data(skin_url)
            for skin in skins:
                self.download_skin(skin)
        print("皮肤下载完成！")


if __name__ == "__main__":
    # 实例化爬虫
    scraper = LOLThemeScraper()
    # 下载获取所有皮肤
    scraper.get_all_skin()
