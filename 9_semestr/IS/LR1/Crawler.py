import sqlite3

import bs4
# import psycopg2
import re
import openpyxl
import requests
from bs4 import BeautifulSoup

# пригодится
# update pg_database set datcollate='ru_RU.UTF-8', datctype='ru_RU.UTF-8' where datname='spider';

wb = openpyxl.load_workbook('../name_list.xlsx')
sheet = wb['Лист1']
excluded_words = []
for i in range(1, 51529):
    cell_value = sheet.cell(row=i, column=1).value
    excluded_words.append(cell_value)
wb.close()
print(excluded_words)


class Crawler:
    urlCountList = []
    wordCountList = []
    ignoredWordList = ['и', 'также', 'тоже', 'что', 'чтобы', 'ни', 'а', 'но', 'или', 'либо', 'a', 'and', 'or', 'but',
                       'when', 'if', 'because', 'as', 'till', 'how', 'so', 'unless', 'until']

    # 0. Конструктор Инициализация паука с параметрами БД
    def __init__(self, dbFileName):
        self.dblink = sqlite3.connect(dbFileName)
        print("База инициализирована")
        self.count_words = 0  # Инициализация счетчика слов

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
        for tag in soup.find_all(['script', 'style', 'img']):
            tag.decompose()
        for tag in soup.find_all():
            tag_text = tag.string
            if tag_text is not None:
                text = text + tag_text + " "
        return text

    # 3. Разбиение текста на слова
    def separateWords(self, text):
        list_of_words = re.split("\s|\.|-|\(|\)|,|;|\"|\?|:", text)
        list_out = list(filter(lambda a: a != "", list_of_words))
        return list_out

    # 4. Проиндексирован ли URL (проверка наличия URL в БД)
    def isIndexed(self, url_id):
        cursor = self.dblink.cursor()
        cursor.execute("SELECT 1 FROM wordLocation WHERE fk_URLid = ?", (url_id,))
        res = cursor.fetchall()
        cursor.close()
        if (len(res) == 0):
            return False
        else:
            return True

    # 5. Добавление ссылки с одной страницы на другую
    def addLinkRef(self, urlFrom, urlTo, linkText):
        cursor = self.dblink.cursor()
        cursor.execute("INSERT INTO linkBetweenURL (fk_from_url_id, fk_to_url_id) VALUES (?, ?)", [urlFrom, urlTo])
        self.dblink.commit()
        cursor.execute("SELECT * FROM linkBetweenURL WHERE rowid = last_insert_rowid();")
        link_ref_id = cursor.fetchall()[0][0]

        # Связываем текст и ссылки
        text_list = self.separateWords(linkText)
        for word in text_list:
            if word.lower() in self.ignoredWordList:
                continue
            word_id = self.addWordToTableWord(word, 0)
            cursor.execute("INSERT INTO linkWord (fk_word_id, fk_link_id) VALUES (?, ?)", [word_id, link_ref_id])
            self.dblink.commit()
            cursor.execute("SELECT * FROM linkWord WHERE rowid = last_insert_rowid();")

        cursor.close()
        return

    def addUrlToTableUrl(self, url):
        cursor = self.dblink.cursor()
        cursor.execute("SELECT * FROM URLList a WHERE a.url = ?", [url])
        res = cursor.fetchall()
        if len(res) == 0:
            cursor.execute("INSERT INTO URLList (url) VALUES (?)", [url])
            self.dblink.commit()
            cursor.execute("SELECT * FROM URLList WHERE rowid = last_insert_rowid();")
            res = cursor.fetchall()
        cursor.close()
        return res[0][0]

    # Добавление url. вернет айди записи
    def addWorldToWorldLocation(self, fk_word_id, fk_url, location):
        cursor = self.dblink.cursor()
        cursor.execute("INSERT INTO wordLocation (fk_wordid, fk_URLid, location) VALUES (?, ?, ?)",
                       (int(fk_word_id), int(fk_url), int(location)))
        self.dblink.commit()
        cursor.close()
        return

    # Добавление слова в таблицу слов. вернет айди записи
    def addWordToTableWord(self, word, isFiltres=0):

        if self.count_words % 10 == 0:
            self.aggregateStat()  # Вызываем aggregateStat для обновления статистики

        # Если параметр для замены пробелом не предоставлен, создайте его по умолчанию None

        # Проверьте, не входит ли слово в список слов, которые нужно заменить пробелом
        cursor = self.dblink.cursor()
        if word.istitle() == True:
            if word.lower() in excluded_words or word in excluded_words:
                word = ' '  # Заменяем слово на пробел
                isFiltres = 1
        cursor.execute("SELECT * FROM wordList a WHERE a.word = lower(?)", [word])
        res = cursor.fetchall()
        if len(res) == 0:
            cursor.execute("INSERT INTO wordList (word, isFiltred) VALUES (lower(?), ?)", [word, isFiltres])
            self.dblink.commit()
            cursor.execute("SELECT * FROM wordList WHERE rowid = last_insert_rowid();")
            res = cursor.fetchall()
        cursor.close()
        return res[0][0]

    # 6. Непосредственно сам метод сбора данных.
    # Начиная с заданного списка страниц, выполняет поиск в ширину
    # до заданной глубины, индексируя все встречающиеся по пути страницы
    def crawl(self, urlList, maxDepth=2):
        count_of_visited = -1
        root_url = urlList[0]
        newUrlList = urlList.copy()
        # проходим по списку url адрессов в зависимости от заданной глубины
        for i in range(maxDepth + 1):
            print(f"Начало обхода ссылок на глубине {i}\n")
            count = 0
            urlList = newUrlList.copy()
            newUrlList = []
            for url in urlList:

                count = count + 1
                if count > 80:
                    break
                # Если ссылка на соц сети то пропускаем
                if (url.find("vk.com") != -1 or url.find("t.me") != -1 or url.find("twitter.com") != -1 or url.find(
                        "facebook") != -1 or url.find("youtube.com") != -1):
                    continue

                # Выправляем кривую ссылку
                if url.find("https://") == -1:
                    if url.find("//") != -1:
                        url = url.replace("//", "")
                        url = "https://" + url
                    if url.find(root_url) == -1:
                        url = url.replace("https://", "")
                        url = root_url + url

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

    def aggregateStat(self):
        cursor = self.dblink.cursor()
        cursor.execute("SELECT COUNT(*) FROM URLList UNION SELECT COUNT(*) FROM wordList")
        res = cursor.fetchall()
        self.urlCountList.append(res[0][0])
        if len(res) >= 2:
            self.wordCountList.append(res[1][0])

    # 7. Инициализация таблиц в БД
    def initDB(self):
        cursor = self.dblink.cursor()

        # удаляем таблицы если они есть
        cursor.execute(f"drop table if exists wordList")
        cursor.execute(f"drop table if exists URLList")
        cursor.execute(f"drop table if exists wordLocation")
        cursor.execute(f"drop table if exists linkBetweenURL")
        cursor.execute(f"drop table if exists linkWord")

        # создаем таблицы
        # 1
        cursor.execute("""CREATE TABLE IF NOT EXISTS wordList (
                                        rowid INTEGER PRIMARY KEY AUTOINCREMENT,
                                        word text,
                                        isFiltred integer check (isFiltred in (0,1)) );""")
        # 2
        cursor.execute("""CREATE TABLE IF NOT EXISTS URLList (
                                        rowid INTEGER PRIMARY KEY AUTOINCREMENT,
                                        url text);""")
        # 3
        cursor.execute("""CREATE TABLE IF NOT EXISTS wordLocation (
                                        rowid INTEGER PRIMARY KEY AUTOINCREMENT,
                                        fk_wordid integer references word(rowid),
                                        fk_URLid integer references url(rowid),
                                        location integer );""")
        # 4
        cursor.execute("""CREATE TABLE IF NOT EXISTS linkBetweenURL (
                                        rowid INTEGER PRIMARY KEY AUTOINCREMENT,
                                        fk_from_url_id INTEGER REFERENCES url(rowid),
                                        fk_to_url_id INTEGER REFERENCES url(rowid) );""")
        # 5
        cursor.execute("""CREATE TABLE IF NOT EXISTS linkWord (
                                        rowid INTEGER PRIMARY KEY AUTOINCREMENT,
                                        fk_word_id integer REFERENCES word(rowid),
                                        fk_link_id integer REFERENCES link_between_url(rowid) );""")
        cursor.close()
        print("Созданы пустые таблицы с необходимой структурой")

    # 8. Вспомогательная функция для получения идентификатора и добавления записи, если такой еще нет
    # def getEntryId(self, tableName, fieldName, value):
    #     return 1

    def getEntryId(self, tableName, fieldName, value):
        return 1


    def sql_request(self):
        conn = sqlite3.connect('DB.db')
        cursor = conn.cursor()

        # Запрос для получения топ 20 значений
        top_20_query = ("""
        SELECT
        SUBSTR(url, INSTR(url, '//') + 2)
        AS
        domain, COUNT(*)
        AS
        frequency
        FROM
        URLList
        GROUP
        BY
        domain
        ORDER
        BY
        frequency
        DESC
        LIMIT
        20;
        """)
        # SELECT fk_URLid, COUNT(fk_URLid) AS frequency FROM wordLocation GROUP BY fk_URLid ORDER BY frequency DESC LIMIT 20;

        # Выполнение запроса и вывод результата
        cursor.execute(top_20_query)
        top_20_results = cursor.fetchall()

        # Вывод результатов
        print("Топ 20 значений по частоте:")
        for row in top_20_results:
            print("Значение:", row[0], "Частота:", row[1])

        top_20_word = ("""SELECT wordList.word, COUNT(wordLocation.fk_wordid) AS frequency
           FROM wordLocation
           JOIN wordList ON wordLocation.fk_wordid = wordList.rowid
           GROUP BY wordLocation.fk_wordid, wordList.word
           ORDER BY frequency DESC
           LIMIT 20;""")

        # Выполнение запроса и вывод результата
        cursor.execute(top_20_word)
        top_20_results = cursor.fetchall()

        # Вывод результатов
        print("Топ 20 значений по частоте:")
        for row in top_20_results:
            print("Значение:", row[0], "Частота:", row[1])

        conn.close()
