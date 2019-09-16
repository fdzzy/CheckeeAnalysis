import requests
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta

checkee_url = 'https://www.checkee.info/'
checkee_page_url = checkee_url + 'main.php?dispdate='

def get_all_months(end_month=date.today(), start_month=date(2008, 12, 1)):
    months = []
    current_month = start_month
    while current_month <= end_month:
        months.append(current_month.strftime('%Y-%m'))
        current_month = current_month + relativedelta(months=+1)
    return months

def scrape_checkee_pages():
    for month in get_all_months():
        url = checkee_page_url + month
        print('Scraping url {}...'.format(url))
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        with open('htmls/page_{}.html'.format(month), 'w', encoding='utf-8') as writer:
            writer.write(r.text)

def parse_html(input_html):
    #doc = BeautifulSoup(input_html, 'html5lib')
    doc = BeautifulSoup(input_html, 'html.parser')
    #doc = BeautifulSoup(input_html, 'lxml')
    for table in doc.find_all('table'):
        if not table.text.strip().startswith('Update'):
            continue
        idx = 0
        headers = []
        all_data = []
        for tr in table.find_all('tr'):
            if not tr.text.strip().startswith('Update'):
                continue
            data = {}
            j = 0
            for td in tr.find_all('td'):
                if idx == 0:
                    headers.append(td.text)
                else:
                    #data[headers[j]] = str(td)
                    data[headers[j]] = td.text
                    if headers[j] == 'Details':
                        data['DetailUrl'] = ''
                        data['DetailText'] = ''
                        anchors = td.find_all('a')
                        if anchors is not None or len(anchors) > 0:
                            anchor = anchors[0]
                            if 'href' in anchor.attrs:
                                data['DetailUrl'] = anchor.attrs['href'].replace('./', checkee_url)
                            if 'title' in anchor.attrs:
                                data['DetailText'] = anchor.attrs['title']
                    j += 1
            idx += 1
            if len(data) > 0:
                all_data.append(data)
    return all_data

def test():
    #parse_html(open('tmp.txt', 'r', encoding='utf-8'))
    for month in get_all_months():
        print(month.strftime('%Y-%m'))

if __name__ == '__main__':
    #scrape_checkee_pages()
    test()