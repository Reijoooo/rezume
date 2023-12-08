from Semester9.IS.LR1.Crawler import Crawler
import matplotlib.pyplot as plt

def plotting():
    depths_URL = range(1, len(dblink.urlCountList) + 1)  # Глубины (или проиндексированные слова)
    depths_word = range(1, len(dblink.wordCountList) + 1)  # Глубины (или проиндексированные слова)
    print(depths_URL, depths_word)
    url_counts = dblink.urlCountList  # Количество URL
    word_counts = dblink.wordCountList  # Количество слов

    # Построение графиков
    plt.figure(figsize=(10, 6))
    plt.plot(depths_URL, url_counts, label='Количество URL')
    plt.plot(depths_word, word_counts, label='Количество слов')
    plt.xlabel('Глубина индексации (или количество проиндексированных слов)')
    plt.ylabel('Количество')
    plt.title('График количества URL и слов в зависимости от глубины индексации')
    plt.legend()
    plt.grid(True)
    plt.show()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    urlList = ["https://ru.wikipedia.org/"]

    dblink = Crawler('DB_final.db')
    dblink.initDB()
    dblink.crawl(urlList, 0)
    # dblink.sql_request()
    # print(dblink.count_words)
    # print(dblink.urlCountList)
    # print(dblink.wordCountList)

    # depths_URL = range(1, len(dblink.urlCountList) + 1)  # Глубины (или проиндексированные слова)
    # depths_word = range(1, len(dblink.wordCountList) + 1)  # Глубины (или проиндексированные слова)
    # print(depths_URL, depths_word)
    # url_counts = dblink.urlCountList  # Количество URL
    # word_counts = dblink.wordCountList  # Количество слов
    #
    # # Построение графиков
    # plt.figure(figsize=(10, 6))
    # plt.plot(depths_URL, url_counts, label='Количество URL')
    # plt.plot(depths_word, word_counts, label='Количество слов')
    # plt.xlabel('Глубина индексации (или количество проиндексированных слов)')
    # plt.ylabel('Количество')
    # plt.title('График количества URL и слов в зависимости от глубины индексации')
    # plt.legend()
    # plt.grid(True)
    # plt.show()

