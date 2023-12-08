from Semester9.IS.LR1.Crawler_PG import Crawler_PG
from Semester9.IS.LR1.OLD_Crawler import OLD_Crawler
from Semester9.IS.LR2.Searcher import Searcher
from Semester9.IS.LR1.Crawler import Crawler
from Semester9.IS.LR2.Search_PG import Search_PG

if __name__ == '__main__':

    # urlList = ["https://example.com/"]
    urlList = ["https://ru.wikipedia.org/"]
    # # #

    #----------------------------------------
    dblink = Crawler('DB_final.db')
    dblink.initDB()
    dblink.crawl(urlList, 1)
    #
    # dblink = Crawler_PG()
    # dblink.initDB()
    # dblink.crawl(urlList, 2)
    #----------------------------------------

    #----------------------------------------
    # dblink = Crawler('DB_3_new.db')
    # dblink.initDB()
    # dblink.crawl(urlList, 2)

    # dblink2 = OLD_Crawler('DB_3_old.db')
    # dblink2.initDB()
    # dblink2.crawl(urlList, 3)
    #----------------------------------------

    #----------------------------------------
    # mySeacherPG = Search_PG()
    # mySeacherPG.getSortedList("domain example")

    mySeacher = Searcher("../LR2/DB_final.db")
    mySeacher.getSortedList("Википедия свободная")
    # mySeacher.getSortedList("свободная энциклопедия")
    #----------------------------------------
