import flask
from flask import Flask, request, url_for, send_file, redirect, render_template, jsonify, send_from_directory
import requests
from bs4 import BeautifulSoup
import json
import jieba
import wordcloud
import imageio
from jinja2 import Environment, PackageLoader
from imageio.core.functions import imread
from wordcloud import ImageColorGenerator, WordCloud
from matplotlib import pyplot as plt
from _datetime import timedelta

mask_path = "static/dou.jpg"
text_content = "static/content.txt"
stop_word = "static/baidu_stopwords.txt"

app = Flask(__name__)
gett = Environment(loader=PackageLoader(__name__, 'templates')).get_template


@app.route('/', methods=['GET', 'POST'])
def index():
    return gett("index.html").render(url_pic="/static/dou.jpg")


@app.route('/search', methods=['GET', 'POST'])
def search():
    text = []
    i = 0
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.56'}

    if request.method == 'POST':
        while True:
            url = request.form.get('website', '')
            url = url + "discussion?start=" + str(i)
            # print(url)
            resp = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(resp.text, 'html.parser')
            for td in soup.find_all("td", class_="title"):
                text.append(td.a.getText())
            i = i+25
            if i > 225:
                break
            # print(str(i))
            # print(1)

    ConvertStr = ''
    for i, item in enumerate(text):
        ConvertStr += item.strip()

    with open('static/content.txt', mode='w', encoding='utf-8') as f:
        f.write(ConvertStr)

    back_coloring = imread(mask_path)

    wc = WordCloud(background_color='white',
                   scale=5,
                   max_words=600,
                   mask=back_coloring,
                   stopwords=stop_word,
                   font_path='static/font.ttf',  # 设置中文字体
                   max_font_size=60,  # 设置字体最大值
                   random_state=30,  # 设置有多少种随机生成状态，即有多少种配色方案
                   width=600,
                   height=600).generate(jieba_processig(stop_word, text_content))
    pUrl = "static/wordcloud0.png"
    wc.to_file(pUrl)
    return gett("index.html").render(url_pic="/" + pUrl)


def jieba_processig(stop_word, text):
    '''jieba分词'''
    with open(stop_word, 'r', encoding='utf-8', errors='ignore') as f:
        stop_words = f.read().splitlines()

    with open(text, 'r', encoding='utf-8') as fi:

        jieba.add_word('细思极恐')
        jieba.add_word('快银')
        cut_str = '/'.join(jieba.cut(fi.read(), cut_all=False))

    cut_word = []
    for word in cut_str.split('/'):
        if word not in stop_words and len(word) > 1:
            cut_word.append(word)

    return ' '.join(cut_word)


if __name__ == "__main__":
    app.debug = True
    app.run()
