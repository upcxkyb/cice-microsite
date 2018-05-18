from flask import Flask
from flask import render_template
from flask import request
import requests, re
from bs4 import BeautifulSoup

app = Flask(__name__)
source_url = 'http://auto.upc.edu.cn'
titles = []
hrefs = []
times = []
img_tag = '<p style="font-size: 14px; white-space: normal; background-color: rgb(255, 255, 255); text-align: center;"><img src="http://yfs01.fs.yiban.cn/web/5572667/catch/363d222917ce66f4f896ca52fc810cd5.jpg" style="float:none;opacity:1;" alt="upc_xkyb.jpg"/></p>'
img_title_tag = '<p style="font-size: 14px; white-space: normal; background-color: rgb(255, 255, 255); text-align: center;"><span style="font-family: 宋体, SimSun; font-size: 14px; color: rgb(0, 0, 0);">图片标题</span></p>'
content_tag = '<p style="font-size: 14px; white-space: normal; background-color: rgb(255, 255, 255); text-align: left; text-indent: 2em;"><span style="color: rgb(0, 0, 0); font-family: 宋体, SimSun; font-size: 16px;">信控易班工作站</span></p>'
autor_tag = '<p style="font-size: 14px; white-space: normal; background-color: rgb(255, 255, 255); text-align: right;"><span style="font-size: 16px; font-family: 宋体, SimSun; color: rgb(0, 0, 0);">【作者：信控易班工作站】</span><br/></p>'

def get_html(url):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}

    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        print('网页获取失败')

def get_titles(html, section):
    soup = BeautifulSoup(html, 'html.parser')
    divs = soup.find_all('div', style='white-space:nowrap')

    global times, titles, hrefs
    if times:
        times = []
    if titles:
        titles = []
    if hrefs:
        hrefs = []

    for div in divs:
        times.append(div.string)
        a = div.parent.previous_sibling.previous_sibling.a
        titles.append(a['title'])
        hrefs.append(source_url + a['href'])

    length = len(titles)

    return render_template('article-list.html', titles=titles, times=times, length=length, section=section)

def get_content(i):
    article_html = get_html(hrefs[i])
    article_soup = BeautifulSoup(article_html, 'html.parser')
    text = article_soup.find('div', 'Article_Content')
    ps = text.find_all('p')
    imgs = []
    img_titles = []
    contents = []
    author = ''

    for p in ps:
        if p.img != None:
            imgs.append(source_url + p.img['src'])
        elif re.search('text-align:center', str(p.get('style'))) != None:

            s = ''
            words = re.findall(r'>(.*?)<', str(p))
            for j in range(0, len(words)):
                s = s + words[j]
            if s != '':
                ss = s.strip()
                if ss != '':
                    img_titles.append(ss)
        elif re.search('text-align:right', str(p.get('style'))) != None:
            # 非标准编辑
            s = ''
            words = re.findall(r'>(.*?)<', str(p))
            for j in range(0, len(words)):
                s = s + words[j]
            if s != '':
                ss = s.strip()
                if ss != '':
                    author = ss    # 作者
        else:
            # 非标准编辑
            s = ''
            words = re.findall(r'>(.*?)<', str(p))
            for j in range(0, len(words)):
                s = s + words[j]
            if s != '':
                ss = s.strip()
                if ss != '':
                    contents.append(ss)
    
    img_tag_soup = BeautifulSoup(img_tag, 'html.parser')
    img_title_tag_soup = BeautifulSoup(img_title_tag, 'html.parser')
    content_tag_soup = BeautifulSoup(content_tag, 'html.parser')
    author_tag_soup = BeautifulSoup(autor_tag, 'html.parser')
    
    post_content = ''
    # 根据情况 图片 图片标题 内容需要循环 在此只是进行测试
    
    for j in range(0, len(imgs)):
        img_tag_soup.find('img')['src'] = imgs[j]
        post_content = post_content + str(img_tag_soup)
        try:
            img_title_tag_soup.find('span').string = img_titles[j]
            post_content = post_content + str(img_title_tag_soup)
        except:
            print('没有图片标题')
    for j in range(0, len(contents)):
        content_tag_soup.find('span').string = contents[j]
        post_content = post_content + str(content_tag_soup)

    author_tag_soup.find('span').string = author
    post_content = post_content + str(author_tag_soup)

    return render_template('article.html', content=post_content, title=titles[i])




@app.route('/')
def index():
    return render_template('index.html')

@app.route('/notice/')
def notice():
    html = get_html('http://auto.upc.edu.cn/_t140/4057/list.htm')
    return get_titles(html, '通知公告')

@app.route('/stu-news/')
def stu_news():
    html = get_html('http://auto.upc.edu.cn/_t140/4056/list1.htm')
    return get_titles(html, '学生新闻')

@app.route('/cice-news/')
def cice_news():
    return render_template('article-list.html')

@app.route('/notice/article')
@app.route('/stu-news/article')
@app.route('/cice-news/article')
def article():
    if request.method == 'GET':
        i = request.args.get('id')
        i = int(i)

        return get_content(i)

        

if __name__ == '__main__':
    app.run(debug=True, port=8000)