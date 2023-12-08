import sqlite3
import csv
import os


class Searcher:
    g_id_word_list = []
    g_url_list_unique = []
    def __init__(self, BDnime):
        self.dblink = sqlite3.connect(BDnime)
        print("База инициализирована")

    def __del__(self):
        self.dblink.close()

    # Получение идентификаторов для каждого слова в queryString
    def getWordsIds(self, queryString):
        queryWordsList = queryString.split(" ")
        if len(queryWordsList) == 0:
            raise Exception("передайте хоть одно слово!")

        cursor = self.dblink.cursor()
        # cursor.execute("SELECT a.rowid, a.word from wordList a WHERE a.word IN ({seq})".format(seq=','.join(['?']*len(queryWordsList))), [ tuple(queryWordsList)])
        cursor.execute(
            "SELECT a.rowid, a.word FROM wordList a WHERE a.word IN ({seq})".format(
                seq=','.join(['?'] * len(queryWordsList))),
            tuple(queryWordsList)
        )
        res = cursor.fetchall()
        if len(res) == 0:
            raise Exception("ни одного слова не нашлось, всё норм?")

        res_indexes = [item[0] for item in res]

        # заполняем слова и соответствующие им айдишники - пригодятся
        self.g_id_word_list = [item for item in res]
        return res_indexes

    def prepareDataBase (self):
        cursor = self.dblink.cursor()
        cursor.execute(""" DROP TABLE IF EXISTS pagerank """)
        cursor.execute("""CREATE TABLE  IF NOT EXISTS  pagerank(
                        rowid INTEGER PRIMARY KEY AUTOINCREMENT,
                        urlid INTEGER,
                        score double precision);""")
        cursor.execute(""" CREATE INDEX pagerank_urlid_idx ON pagerank(urlid) """)
        #примечание: оставшиеся индексы по методе были реализованы в рамках класса crawler
        cursor.close()

    # вернет ранг страницы
    def getRangPage(self, url_id):
        cursor = self.dblink.cursor()

        cursor.execute(""" select sum(res_final.rang) 
                             from (select res.*, res.score/res.count_url rang
                                   from (select a.*, b.score score, (select count(*)
                                                                       from linkBetweenURL c 
                                                                      where c.fk_from_url_id = a.fk_from_url_id) count_url
                                           from linkBetweenURL a, pagerank b
                                          where a.fk_to_url_id = ?
                                            and a.fk_from_url_id = b.urlid) res) res_final """, [url_id])
        res = cursor.fetchall()[0][0]
        if res == None:
            res = 0
        return res

    def getUrlNameByUrlId (self, id):
        cursor = self.dblink.cursor()
        cursor.execute(""" select a.url from URLList a where a.rowid = ?""", [id])
        res = cursor.fetchall()
        if len(res) == 0:
            return None
        else:
            return res[0][0]

    def calculatePageRank(self, iterations=3):
        self.prepareDataBase()
        #заполняем таблицу начальные значениями
        cursor = self.dblink.cursor()
        # на всякий случай чистим
        cursor.execute(""" delete from pagerank """)
        self.dblink.commit()
        cursor.execute(""" insert into pagerank (urlid, score)
                           select rowid, 1.0 from URLList""")
        self.dblink.commit()

        # вычисление ранга по всем итерациям
        coef_d = 0.15
        for i in range(iterations):
            # получаем все ссылки из бд
            cursor.execute(""" select * from URLList""")
            url_list = cursor.fetchall()

            for j in range(len(url_list)):
                url_id = url_list[j][0]
                rang = self.getRangPage(url_id)
                rang = (1-coef_d)+coef_d*rang
                # обновляем таблицу
                cursor.execute(""" update pagerank set score = ? where urlid = ?""", [rang, url_id])
                self.dblink.commit()

        # вычисляем ранг по нужным нам страницам
        # cursor.execute(""" select urlid, score from pagerank where urlid in ?""", (tuple(self.g_url_list_unique),))
        cursor.execute("SELECT urlid, score FROM pagerank WHERE urlid IN ({seq})".format(
            seq=','.join(['?'] * len(self.g_url_list_unique))), tuple(self.g_url_list_unique))
        listPageRank = cursor.fetchall()
        dictPageRank = dict()
        for i in range(len(listPageRank)):
            url_id = listPageRank[i][0]
            score = listPageRank[i][1]
            dictPageRank[url_id] = score
        # нормализация
        dictPageRank = self.normalizeScores(dictPageRank)
        return dictPageRank

    # нормализация значений метрик
    def normalizeScores(self, dictRank, smallIsBetter=0):
        resultDict = dict() # словарь с результатом
        vsmall = 0.00001  # создать переменную vsmall - малая величина, вместо деления на 0
        minscore = min(dictRank.values())  # получить минимум
        maxscore = max(dictRank.values())  # получить максимум

        for (key, val) in dictRank.items():
            if smallIsBetter:
                # Режим МЕНЬШЕ вх. значение => ЛУЧШЕ
                # ранг нормализованный = мин. / (тек.значение  или малую величину)
                resultDict[key] = float(minscore) / max(vsmall, val)
            else:
                # Режим БОЛЬШЕ  вх. значение => ЛУЧШЕ вычислить макс и разделить каждое на макс
                # вычисление ранга как доли от макс.
                # ранг нормализованный = тек. значения / макс.
                resultDict[key] = float(val) / maxscore
        return resultDict

    # выводит задержимое результата sql запроса для поиска в файл
    def writeMarchRowsToCsvFile(self, rows):
        data = []
        count_column = len(rows[0])
        # шапка
        row = ['URL_ID']
        for i in range(count_column-1):
            row.append(f"loc_query_world{i+1}")
        data.append(row)
        # значения
        for row_local in rows:
            row = []
            for i in range(count_column):
                row.append(f"{row_local[i]} ")
            data.append(row)
        # запись в файл
        with open('my_match_rows.csv', 'w') as f:
            writer = csv.writer(f)
            for row_local in data:
                writer.writerow(row_local)


    # лютый sql запрос который нам вернет результат поиска фактически
    def getMatchRows(self, queryString):
        # к нижнему регистру
        # queryString = queryString.lower()
        # переданные слова
        queryWordsList = queryString.split(" ")
        # айдишники преданных слов
        id_word_list = self.getWordsIds(queryString)
        # кол-во переданных слов (СЧИТАЕМ ПО ТОМУ СКОЛЬКО СОВПАЛО СЛОВ С ПРОИНДЕКСИРОВАННАМИ СЛОВАМИ)
        count_word = len(id_word_list)

        # части sql запроса (сразу юзаем строки потому что можем)
        sqlpart_Name = ""
        sqlpart_Join = ""
        sqlpart_Condition = ""

        sql = ""
        # формулируем sql запрос.
        for i in range(count_word):
            if i == 0:
                sqlpart_Name = sqlpart_Name + f" select w{i}.fk_URLid urlid, w{i}.location w{i}_loc "
                sqlpart_Join = sqlpart_Join + f" from wordLocation w{i} "
                sqlpart_Condition = sqlpart_Condition + f" where w{i}.fk_wordid = {id_word_list[i]} "
            else:
                sqlpart_Name = sqlpart_Name + f" , w{i}.location w{i}_loc "
                sqlpart_Join = sqlpart_Join + f" inner join wordLocation w{i} on w{i-1}.fk_URLid = w{i}.fk_URLid"
                sqlpart_Condition = sqlpart_Condition + f" and w{i}.fk_wordid = {id_word_list[i]} "
        sql = sqlpart_Name + sqlpart_Join + sqlpart_Condition

        cursor = self.dblink.cursor()
        cursor.execute(sql)
        res_search = [row for row in cursor.fetchall()]
        # выводим результат
        self.writeMarchRowsToCsvFile(res_search)
        # возврат списка найденых слов и списка айдишников слов
        return res_search, id_word_list

    def getAllTextByUrlId(self, url_id):
        cursor = self.dblink.cursor()
        cursor.execute("""  select a.location, b.word 
                               from wordLocation a, wordList b 
                              where a.fk_wordid = b.rowid 
                                and a.fk_urlid = ?""", [url_id])
        alltext = ""
        for item in cursor.fetchall():
            alltext = alltext + " " + item[1]
        return alltext

    def calculateFrequencyRank(self, res_search):
        dictFrequencyRank = dict()
        # цепляем частоту встречаемых слов
        for item in res_search:
            url_id = item[0]
            if not url_id in dictFrequencyRank:
                dictFrequencyRank[url_id] = 1
            else:
                dictFrequencyRank[url_id] = dictFrequencyRank[url_id] + 1
        # нормализация
        dictFrequencyRank = self.normalizeScores(dictFrequencyRank)
        return dictFrequencyRank

    def locationScore(self, rowsLoc):
        """
        Расчет минимального расстояния от начала страницы у комбинации искомых слов
        :param rowsLoc: Список вхождений: urlId, loc_q1, loc_q2, .. слов из поискового запроса "q1 q2 ..." (на основе результата getmatchrows ())
        :return: словарь {UrlId1: мин. расстояния от начала для комбинации, UrlId2: мин. расстояния от начала для комбинации, }
        """

        # Создать locationsDict - словарь с расположением от начала страницы упоминаний/комбинаций искомых слов
        locationsDict = {}

        # Переменная для хранения наилучшей позиции (наименьшей суммы расстояний) для каждой страницы
        best_positions = {}

        for row in rowsLoc:
            urlId = row[0]  # Получить urlId страницы
            loc_q = row[1:]  # Все позиции искомых слов кроме urlId

            # Вычислить сумму дистанций каждого слова от начала страницы
            total_distance = sum(loc_q)

            # Проверка, является ли найденная комбинация слов ближе к началу, чем предыдущие
            if urlId not in best_positions or total_distance < best_positions[urlId]:
                best_positions[urlId] = total_distance

        # Заполнить locationsDict
        for urlId, min_distance in best_positions.items():
            locationsDict[urlId] = min_distance

        # передать словарь дистанций в функцию нормализации, режим "чем больше, тем лучше"
        dictLocationScore = self.normalizeScores(locationsDict, smallIsBetter=1)
        return dictLocationScore



    # фактически функция main, будет вызывать всё остальное
    def getSortedList(self, queryString):
        res_search, id_word_list = self.getMatchRows(queryString)
        # считаем кол-во уникальных url где есть ссылки
        self.g_url_list_unique = []
        for item in res_search:
            if not item[0] in self.g_url_list_unique:
                self.g_url_list_unique.append(item[0])
        print(f"Количество уникальных url-адресов из БД содержащих слова поискового запроса  {len(self.g_url_list_unique)}\n")
        print("Уникальные идентификаторы для каждого слова из поискового запроса ", *self.g_id_word_list, sep="\n")

        PageRank = self.calculatePageRank()
        # FrequencyRank = self.calculateFrequencyRank(res_search)
        FrequencyRank = self.locationScore(res_search)


        result_table = [list([url, PageRank[url], FrequencyRank[url], (PageRank[url]+FrequencyRank[url])/2, self.getUrlNameByUrlId(url)]) for url in PageRank]
        result_table.sort(key = lambda item: item[3], reverse=True)
        result_table.insert(0, ["urlid", "M1", "M2", "M3", "url"])
        # запись в файл
        with open('my_result_table.csv', 'w') as f:
            writer = csv.writer(f)
            for row_local in result_table:
                writer.writerow(row_local)

        # удаляем старые файлы
        current_dit = os.getcwd()
        file_list = os.listdir(current_dit)
        for file in file_list:
            if file.find("my_html_out")!=-1:
                os.remove(current_dit + "/" + file)

        # для первых ТРЕХ страниц сгенерировать HTML
        for i in range(1,4):
            if i>=len(result_table):
                break
            self.createMarkedHtmlFile(f"my_html_out{i}.html", self.getAllTextByUrlId(result_table[i][0]), queryString)


    # сгенерировать HTML
    def getMarkedHTML(self, text, query_string):
        HTML = """<!DOCTYPE html>
                    <html lang="en">
                    <head>
                       <meta charset="UTF-8">
                       <title>Title</title>
                    </head>
                    <body>
                       <p> ##Your text## </p>
                    </body>
                    </html>"""
        HTML = HTML.replace("##Your text##", text)

        query_string_list = query_string.split()
        for word in query_string_list:
            HTML = HTML.replace(word, f"<span style=\"background-color:red\"> {word} </span>")

        return HTML

    # сфоормировать HTML для наглядной демонстрации
    def createMarkedHtmlFile(self, html_file_name, text, query_string):
        HTML = self.getMarkedHTML(text, query_string)
        # запись в файл
        with open(html_file_name, 'w',  encoding="utf-8") as f:
            f.write(HTML)

