import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import random as rd
import json

def scrape_jobspider(job_title, state):
    page_no = rd.randint(1,30)
    url = f"https://www.jobspider.com/job/resume-search-results.asp/state_{state.replace(' ', '+')}/word_{job_title.replace(' ', '+')}/page_{page_no}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    title_tags = soup.find_all('td', attrs={'class': 'StandardRow'})

    with ThreadPoolExecutor() as executor:
        links = list(executor.map(lambda title_tag: "https://www.jobspider.com/" + title_tag.a['href'] if title_tag.a else None, title_tags))

    links = [link for link in links if link is not None]

    return links

def scrape_postjobfree(job_title, state):
    url = f"https://www.postjobfree.com/resumes?q=&n=&t={job_title.replace(' ', '+')}&d=&l={state.replace(' ', '+')}&radius=25&r=100"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    title_tags = soup.find_all('h3', attrs={'class': 'itemTitle'})

    links = ["https://www.postjobfree.com" + title_tag.a['href'] for title_tag in title_tags]

    return links

def scrape_and_get_links(data):
    
    all_links_list = []

    for idx, condition in enumerate(data, start=1):
        job_title = condition.get('job_title', '') if condition.get('job_title') else condition.get('must_have')[0] or condition.get('must_have')
        state = condition.get('locations', [''])[0] if condition.get('locations') else 'US'

        
        links_postfree = scrape_postjobfree(job_title, state)
        links_jobspider = scrape_jobspider(job_title, state)

        links_df_postfree = pd.DataFrame({'ID': [idx] * len(links_postfree), 'links': links_postfree})
        links_df_jobspider = pd.DataFrame({'ID': [idx] * len(links_jobspider), 'links': links_jobspider})


        all_links_list.append(links_df_postfree)
        all_links_list.append(links_df_jobspider)


    all_links = pd.concat(all_links_list, ignore_index=True)
    return all_links
