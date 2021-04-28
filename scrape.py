#!/usr/bin/env python
"""This script downloads content from the NLA Staff Papers listing as json.

It supports a sensible default, along with optional arguments for url & outpath.

Usage:

    $ python scrape.py [--outpath] [./your/data/path/file.json]

Example:

    $ python scrape.py
    $ python scrape.py "~/Desktop/nla-staff-papers.json"

"""

import os
import sys
import json
import argparse
from datetime import datetime

import requests
from bs4 import BeautifulSoup


def collect_soup(url: str):
    """Take a url and return the BeautifulSoup representation of that page.

    Args:
        url (str): The url for the page we're collecting.

    Returns:
        A BeautifulSoup representation of the collected page content.

    """
    r = requests.get(url)
    return BeautifulSoup(r.content, features='lxml')


def extract_raw_search_results(soup):
    """Take a BeautifulSoup representation of a page; return all search results.

    Args:
        soup: A BeautifulSoup of the page.

    Returns:
        All 'li' elements within the first search-results elem of the page.

    """
    return soup.find(attrs={'class': 'search-results'}).find_all('li')


def get_author_list(item) -> list:
    """Take (BeautifulSoup) item, extract authors; return clean list of strings.

    Args:
        item: A BeautifulSoup of an item in the list of all search results.

    Returns:
        list: All author names found in a 'paper-author' div.

    """
    author_div = item.select("div[class*=paper-author]")[0]
    raw_authors = author_div.find('span', attrs={'class': 'field-content'}).text
    return [a.strip() for a in raw_authors.split(',')]


def get_topics_list(item) -> list:
    """Take (BeautifulSoup) item, extract topics; return clean list of strings.

    Args:
        item: A BeautifulSoup of an item in the list of all search results.

    Returns:
        list: All topics found in a 'paper-topics' div.

    """
    topic_div = item.select("div[class*=paper-topics]")[0]
    raw_topics = topic_div.find('span', attrs={'class': 'field-content'}).text
    return [t.strip() for t in raw_topics.split(',')]


def get_abstract(item) -> str:
    """Take a (BeautifulSoup) item; extract and return abstract.

    Args:
        item: A BeautifulSoup of an item in the list of all search results.

    Returns:
        list: The text contained in a 'paper-abstract' div.

    """
    return item.select("div[class*=paper-abstract]")[0].text.strip()


def get_date(item) -> str:
    """Take a (BeautifulSoup) item; get a (reformatted) datetime.

    Args:
        item: A BeautifulSoup of an item in the list of all search results.

    Returns:
        str: An ISO8601-formatted date.

    """
    date_div = item.select("div[class*=paper-pubdate]")[0]
    raw = date_div.find('span', attrs={'class': 'field-content'}).text.strip()
    iso = datetime.strptime(raw, '%d %B %Y').date().isoformat()
    return iso


def convert_raw_paper_to_dict(item) -> dict:
    """Take (BeautifulSoup) item from list of search results; return clean dict.

    Args:
        item: A BeautifulSoup of an item in the list of all search results.

    Returns:
        dict: A cleaned representation of all listed paper info in dict form.

    """
    paper = {'title': item.find('h3').text,
             'url': f"https://www.nla.gov.au{item.find('h3').find('a')['href']}",
             'authors': get_author_list(item),
             'date': get_date(item),
             'abstract': get_abstract(item),
             'topics': get_topics_list(item)}
    return paper


def scrape(url: str = 'https://www.nla.gov.au/our-publications/staff-papers'):
    """Take url to a staff-papers page; return all available as a list of dicts.

    Args:
        url (str): The url of the nla staff papers page.

    Returns:
        A list of dicts, where each dict is a clean representation of a paper.

    """
    page = collect_soup(url)
    search_results = extract_raw_search_results(page)
    processed_results = []
    for result in search_results:
        processed_results.append(convert_raw_paper_to_dict(result))
    return processed_results


def parse_args():
    """Use argparse to process available system arguments to a clean namespace.

    Returns:
        The processed arguments namespace.

    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--url",
            help = "the url to scrape",
            type = str,
            default = "https://www.nla.gov.au/our-publications/staff-papers")
    parser.add_argument("--outpath",
            help = "path to save json to",
            type = str,
            default = "./")
    parser.add_argument("--silent",
            help = "whether to silence the output to console",
            action = "store_true",
            default = False)
    args = parser.parse_args()
    args.outpath = os.path.abspath(args.outpath) # make the raw outpath sensible
    return args


def add_filename_default(outpath: str) -> str:
    """Take a raw outpath (directory) and add a sensible json filename.

    Args:
        outpath (str): The path we're planning on saving the data to.

    Returns:
        A path with a sensible file path with json filename added.

    """
    default_file_name = datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.json'
    if not outpath.endswith('.json'):
        return os.path.join(outpath, default_file_name)
    else:
        return outpath


def main():
    """Process system arguments, scrape publications, write result to file."""
    args = parse_args() # process system arguments
    papers = scrape(url = args.url) # scrape, using the arg default if necessary
    if not args.outpath.endswith('.json'): # add a default filename if necessary
        args.outpath = add_filename_default(args.outpath)
    try:
        with open(args.outpath, 'w+', encoding='utf8') as f:
            json.dump(papers, f, indent=2)
    except IOError as e: # The error we'll get if we can't write to path.
        print(e)
        sys.exit('Unable to write to provided file path ' + args.outpath)
    if not args.silent: # Print the json to console unless silenced
        print(json.dumps(papers, indent=2))


if __name__ == "__main__":
    main()
