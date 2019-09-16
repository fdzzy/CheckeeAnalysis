import requests
import re
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

def norm_text(text):
    text = re.sub(r'\r', ' #R# ', text)
    text = re.sub(r'\n', ' #N# ', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

def parse_all_htmls():
    headers = ['Month', 'ID', 'VisaType', 'VisaEntry', 'USConsulate', 'Major', 'Status', 'CheckDate', 'CompleteDate', 'WaitingDays', 'DetailUrl', 'DetailText']
    with open('result.tsv', 'w', encoding='utf-8') as writer:
        writer.write('%s\n' % '\t'.join(headers))
        for month in get_all_months(end_month=date(2019, 9, 1)):
            html = 'htmls/page_{}.html'.format(month)
            print('Processing %s...' % html)
            all_data = parse_html(html)
            for data in all_data:
                items = []
                for i, header in enumerate(headers):
                    if i == 0:
                        items.append(month)
                    else:
                        items.append(norm_text(data[header]))
                writer.write('%s\n' % '\t'.join(items))

def parse_html(input_html):
    reader = open(input_html, 'r', encoding='utf-8')
    #doc = BeautifulSoup(reader, 'html5lib')
    doc = BeautifulSoup(reader, 'html.parser')
    #doc = BeautifulSoup(reader, 'lxml')
    all_data = []
    for table in doc.find_all('table'):
        if not table.text.strip().startswith('Update'):
            continue
        idx = 0
        headers = []
        for tr in table.find_all('tr'):
            if not tr.text.strip().startswith('Update'):
                continue
            data = {}
            j = 0
            for td in tr.find_all('td'):
                if idx == 0:
                    headers.append(re.sub(r'\W', '', td.text))
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
    for month in get_all_months():
        print(month.strftime('%Y-%m'))

if __name__ == '__main__':
    #scrape_checkee_pages()
    #test()
    parse_all_htmls()