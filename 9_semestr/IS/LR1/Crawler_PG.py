import bs4
import psycopg2
import re

import matplotlib.pyplot as plt

import requests
from bs4 import BeautifulSoup

# пригодится
# update pg_database set datcollate='ru_RU.UTF-8', datctype='ru_RU.UTF-8' where datname='spider';

# в word и url смотреть чтобы отследить стаститику.
# кол-во посещеннный урл - Х

# графики надо

class Crawler_PG:
    urlCountList = []
    wordCountList = []
    ignoredWordList = ['и', 'также', 'тоже', 'что', 'чтобы', 'ни', 'а', 'но', 'или', 'либо', 'a', 'and', 'or', 'but',
                       'when', 'if', 'because', 'as', 'till', 'how', 'so', 'unless', 'until']
    # 0. Конструктор Инициализация паука с параметрами БД
    def __init__(self):
        self.dblink = psycopg2.connect(dbname="spider", host="127.0.0.1", user="blinomes", password="", port="5433")
        self.dblink.autocommit = True
        print("База инициализирована")

    # 0. Деструктор
    def __del__(self):
        self.dblink.close()

    # 1. Индексирование одной страницы
    def addIndex(self, soup, url):
        count = 0
        # получаем url_id стараницы
        url_id = self.addUrlToTableUrl(url)
        # далее проверяем не проиндексирована ли уже наша страница
        if (self.isIndexed(url_id) == True):
            return
        # приступаем к индексации
        print(f"Индексирование URL: {url}\n")

        text = self.getTextOnly(soup)
        text_list = self.separateWords(text)


        for word in text_list:
            if word == "" or word is None or word == "\x00" or word.lower() in self.ignoredWordList:
                continue
            id_word = self.addWordToTableWord(word, 0)
            self.addWorldToWorldLocation(id_word, url_id, count)
            count += 1


    # 2. Получение текста страницы без ссылок
    def getTextOnly(self, soup):
        text = ""
        for tag in soup.find_all(['a', 'script', 'style']):
            tag.decompose()
        for tag in soup.find_all():
            tag_text = tag.string
            if tag_text is not None:
                text = text + tag_text + " "
        return text



    # 3. Разбиение текста на слова
    def separateWords(self, text):
        list_of_words = re.split("\s|\.|-|\(|\)|,|;|\"|\?|:|«|»|\–", text)
        list_out = list(filter(lambda a: a != "", list_of_words))
        return list_out

    # 4. Проиндексирован ли URL (проверка наличия URL в БД)
    def isIndexed(self, url_id):
        # будем проверять по наличию в таблице word_location ибо в таблице url уже энивей есть запись
        cursor = self.dblink.cursor()
        cursor.execute(""" select 1 from word_location a where a.fk_URLid = %s """, [url_id])
        res = cursor.fetchall()
        cursor.close()
        if (len(res) == 0):
            return False
        else:
            return True

    # 5. Добавление ссылки с одной страницы на другую
    def addLinkRef(self, urlFrom, urlTo, linkText):
        cursor = self.dblink.cursor()
        # связываем ссылки
        cursor.execute(""" insert into link_between_url (fk_from_url_id, fk_to_url_id) values (%s, %s) returning *""",
                       [urlFrom, urlTo])
        link_ref_id = cursor.fetchall()[0][0]

        # связываем текст и ссылки
        text_list = self.separateWords(linkText)
        for word in text_list:
            if word.lower() in self.ignoredWordList:
                continue
            word_id = self.addWordToTableWord(word, 0)
            cursor.execute(""" insert into link_word (fk_word_id, fk_link_id) values (%s, %s) returning *""",
                          [word_id, link_ref_id])

        cursor.close()
        return

    # Добавление url. вернет айди записи.
    def addUrlToTableUrl(self, url):
        cursor = self.dblink.cursor()
        cursor.execute(""" select * from url a where a.url = %s""", [url])
        res = cursor.fetchall()
        if len(res) == 0:
            cursor.execute(""" insert into url (url) values (%s) returning *""", [url])
            res = cursor.fetchall()
        cursor.close()
        return res[0][0]

    # Добавление url. вернет айди записи.
    def addWorldToWorldLocation(self, fk_world_id, fk_url, location):
        cursor = self.dblink.cursor()
        cursor.execute(""" insert into word_location (fk_wordid, fk_URLid, location) values (%s, %s, %s)""", [int(fk_world_id), int(fk_url), int(location)])
        cursor.close()
        return

    # Добавление слова в таблицу слов. вернет айди записи
    def addWordToTableWord(self, word, isFiltres=0):

        cursor = self.dblink.cursor()
        cursor.execute(""" select * from word a where a.word = lower(%s)""", [word])
        res = cursor.fetchall()
        if len(res) == 0:
            cursor.execute(""" insert into word (word, isFiltred) values (lower(%s), %s) returning *""", [word, isFiltres])
            res = cursor.fetchall()
        cursor.close()
        return res[0][0]

    def aggregateStat(self):
        cursor = self.dblink.cursor()
        cursor.execute(""" select count(a.*) from url a
                           union
                           select count(b.*) from word b""")
        res = cursor.fetchall()
        self.urlCountList.append(res[0][0])
        self.wordCountList.append(res[1][0])
    # 6. Непосредственно сам метод сбора данных.
    # Начиная с заданного списка страниц, выполняет поиск в ширину
    # до заданной глубины, индексируя все встречающиеся по пути страницы
    def crawl(self, urlList, maxDepth=2):
        count_of_visited = -1
        root_url = urlList[0]
        newUrlList = urlList.copy()
        # проходим по списку url адрессов в зависимости от заданной глубины
        for i in range(maxDepth+1):
            print(f"Начало обхода ссылок на глубине {i}\n")
            count = 0
            urlList = newUrlList.copy()
            newUrlList = []
            # print(urlList)
            for url in urlList:

                count = count + 1
                if count > 80:
                    break
                # Если ссылка на соц сети то пропускаем
                if (url.find("vk.com") != -1 or url.find("t.me") != -1 or url.find("twitter.com") != -1 or url.find("facebook") != -1 or url.find("youtube.com") != -1):
                    continue

                # Выправляем кривую ссылку
                if url.find("https://") == -1:
                    if url.find("//") != -1:
                        url=url.replace("//","")
                        url="https://" + url
                    if url.find(root_url) == -1:
                        url = url.replace("https://", "")
                        url=root_url+url

                id_source_url = self.addUrlToTableUrl(url)

                # если не получилось - едем дальше
                try:
                  html_doc = requests.get(url).text
                  count_of_visited = count_of_visited + 1
                  if count_of_visited % 2 == 0:
                      self.aggregateStat()
                #   тут двигаем счетчик посещенных сайтов
                except Exception as a:
                    print(a)
                    continue

                # парсим html
                soup = bs4.BeautifulSoup(html_doc, "html.parser")
                for link in soup.find_all('a'):
                    href = link.get("href")
                    text_href = link.text
                    if (href is not None and href != "/" and href.find("#") == -1 and href != "" and text_href != ""):
                        newUrlList.append(href)
                        id_target_url = self.addUrlToTableUrl(href)
                        # связываем ссылки друг с другом
                        self.addLinkRef(id_source_url, id_target_url, text_href)
                # индексируем страницу
                self.addIndex(soup, url)
        #вывод графиков
        plt.plot([i*2 for i in range(len(self.wordCountList))], self.wordCountList, color='red')
        plt.plot([i*2 for i in range(len(self.urlCountList))], self.urlCountList, color='green')
        plt.show()




    # 7. Инициализация таблиц в БД
    def initDB(self):
        cursor = self.dblink.cursor()

        # удаляем таблицы если они есть
        cursor.execute(f"drop table if exists link_word")
        cursor.execute(f"drop table if exists link_between_url")
        cursor.execute(f"drop table if exists word_location")
        cursor.execute(f"drop table if exists url")
        cursor.execute(f"drop table if exists word")

        # создаем таблицы
        cursor.execute("""create table url (
                          rowid serial primary key,
                          url text);""")
        cursor.execute("""create table word (
                          rowid serial primary key,
                          word text,
                          isFiltred integer check (isFiltred in (0,1)) );""")
        cursor.execute("""create table word_location (
                          rowid serial primary key,
                          fk_wordid integer references word(rowid),
                          fk_URLid integer references url(rowid),
                          location integer );""")
        cursor.execute("""create table link_between_url (
                          rowid serial primary key,
                          fk_from_url_id integer REFERENCES url(rowid),
                          fk_to_url_id integer REFERENCES url(rowid) );""")
        cursor.execute("""create table link_word (
                          rowid serial primary key,
                          fk_word_id integer REFERENCES word(rowid),
                          fk_link_id integer REFERENCES link_between_url(rowid) );""")

        cursor.execute("""create index url_url_idx on url(url);""")
        cursor.execute("""create index word_wors_idx on word(word);""")

        # новые индексы для лр 3-4.
        cursor.execute("""create index word_location_fk_wordid_idx on word_location(fk_wordid);""")
        cursor.execute("""create index link_between_url_fk_from_url_id_idx on link_between_url(fk_from_url_id);""")
        cursor.execute("""create index link_between_url_fk_to_url_id_idx on link_between_url(fk_to_url_id);""")
        cursor.close()
        print("Созданы пустые таблицы с необходимой структурой")

    # 8. Вспомогательная функция для получения идентификатора и добавления записи, если такой еще нет
    def getEntryId(self, tableName, fieldName, value):
        return 1


