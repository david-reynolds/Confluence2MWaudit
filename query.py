from bs4 import BeautifulSoup as bs
import urllib2
import pyodbc


def get_page_titles():
    dsn = 'dev-portal'
    database = 'Confluence_3.x'

    con_string = "Driver={SQL Server};"
    con_string += "Server={0};Database={1};Trusted_Connection=yes;CharacterSet=UTF-16LE;".format(dsn, database)
    conn = pyodbc.connect(con_string)
    cur = conn.cursor()

    query = """SELECT DISTINCT c.TITLE
                FROM content AS c
                WHERE c.CONTENT_STATUS = 'current' AND c.TITLE IS NOT null and c.spaceid is not null
            """
    q_results = cur.execute(query)
    tbl = [x[0] for x in q_results.fetchall()]
    return tbl


def pull_the_page(page_title):
    querystring = "http://standards.corp.dtiglobal.com/wiki/index.php?title=Special:Search&search={0}&fulltext=Search&profile=all"
    # <span class="mw-headline" id="Page_title_matches">
    pagedata = urllib2.urlopen(querystring.format(urllib2.quote(page_title.strip().encode('utf8'))))
    return pagedata


def find_the_page_title(page_data, search):
    soup = bs(page_data, 'html.parser')
    page_titles = soup.find("span", {"id": "Page_title_matches"})
    if page_titles:
        titles = [x for x in page_titles.find_all_next('a') if search in x.text]
        return titles
    else:
        return []


if __name__ == "__main__":
    confluence_page_titles = get_page_titles()
    with open(r"C:\c2m_audit.txt", 'w') as log:
        for confluence_page_title in confluence_page_titles:
            mediawiki_result = pull_the_page(confluence_page_title)
            pages = find_the_page_title(mediawiki_result, confluence_page_title)
            if not pages:
                log.write("{0}: {1}\n".format(confluence_page_title.strip().encode('utf8'), "404"))
            else:
                for page in pages:
                    try:
                        title = page['title']
                        href = page['href']
                        log.write("{0}: {1}\t{2}\n".format(confluence_page_title, title, href))
                    except KeyError as e:
                        log.write(repr(page))
            log.flush()
