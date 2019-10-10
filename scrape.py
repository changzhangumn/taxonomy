import sys
import pandas as pd
from bs4 import BeautifulSoup
import requests
import time
import nltk
import re

def scrape_csv(csv_file_name, processed_file_name):
    save_to_file = open(processed_file_name, 'w')
    save_to_file.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s \n' % ('UPC_code', 'title', 'brand', 'description+dimensions',"height", "width", "length", "weight", "color", "size"))

    def clean(text):
        # remove punctualtions and special characters and convert all letters into lower case
        text = text.lower()
        text = re.sub(r'[^A-Za-z0-9."]+',' ',text)
        return text

    def dimension_process(text):
        text = clean(text)
        text = text.split()
        
        dims =	{
            "height": 'NA',
            "width": 'NA',
            "length": 'NA',
            "weight": 'NA',
            "color": 'NA',
            "size": 'NA'
                        }
        n = len(text)
        for i in range(0,n):
            if text[i] in dims:
                if text[i] in ["weight","size"]:
                    value = text[min(i+1,n-1)]+text[min(i+2,n)]
                    dims[text[i]] = value
                else:
                    value = text[min(i+1,n-1)]
                    dims[text[i]] = value

        return dims

    with open(csv_file_name, 'r',encoding='utf-8') as csv:
        lines = csv.readlines()
        for i, line in enumerate(lines):
            try:
                UPC_code = str(line).replace('\n', '').replace('\r', '')
                page_link = 'https://www.barcodelookup.com/' + UPC_code
                page_response = requests.get(page_link, timeout=5)
                page_content = BeautifulSoup(page_response.content, "html.parser")
                title = clean(page_content.find('h4').get_text().replace('\n', ' ').replace('\r', ' ').replace(',', ' '))
                description = clean(page_content.find('ul', {'class': 'product-text'}).get_text().replace('\n', ' ').replace('\r', ' '))
                codes = page_content.find('span', {'class': 'product-text'}).get_text().replace('\n', ' ').replace('\r', ' ')
                if len(page_content.find_all('span', {'class': 'product-text'}))>2:
                    brand = page_content.find_all('span', {'class': 'product-text'})[2].text.replace('\n', ' ').replace('\r', ' ').replace(',', ' ')
                else:
                    brand = 'N/A'
                if len(page_content.find_all('ul', {'class': 'product-text'}))>1:
                    dimensions = clean(page_content.find_all('ul', {'class': 'product-text'})[1].text.replace('\n', ' ').replace('\r', ' ').replace(',', ' '))
                else:
                    dimensions = ''
                dims = dimension_process(str(description+dimensions))
                save_to_file.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s \n' % (codes[5:17], title, brand, description+dimensions, dims["height"], dims["width"], dims["length"], dims["weight"], dims["color"], dims["size"]))
                time.sleep(2.5) # prevent querying too frequently
            except:
                pass
            if i>5000: # set a threhold here
                break               
    save_to_file.close()
    return processed_file_name


if __name__ == '__main__':
    csv_file_name = sys.argv[1]
    processed_file_name = sys.argv[1][:-4] + '-scraped.csv'
    scrape_csv(csv_file_name, processed_file_name)

