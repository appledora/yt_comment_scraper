# for each link, open the video and extract the comments
# save the comments to a csv file

from selenium import webdriver
import time
import pandas as pd
import time
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import json
import time

from selenium.webdriver.common.by import By
from selenium.common import exceptions
from selenium.webdriver.chrome.service import Service

options = {}
chrome_options = Options()
chrome_options.add_argument("--user-data-dir=hash")
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--incognito")
chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--headless")


def scrape(url):

    browser = webdriver.Chrome(options=chrome_options)

    browser.get(url)
    time.sleep(10)

    try:
        # Extract the elements storing the video title and
        # comment section.
        title = browser.find_element(By.XPATH, '//*[@id="title"]/h1/yt-formatted-string').text
        comment_section = browser.find_element(By.XPATH, '//*[@id="comments"]')
    except exceptions.NoSuchElementException:
        # Note: Youtube may have changed their HTML layouts for
        # videos, so raise an error for sanity sake in case the
        # elements provided cannot be found anymore.
        error = "Error: Double check selector OR "
        error += "element may not yet be on the screen at the time of the find operation"
        print(error)
        return []

    # Scroll into view the comment section, then allow some time
    # for everything to be loaded as necessary.
    browser.execute_script("arguments[0].scrollIntoView();", comment_section)
    time.sleep(7)

    # Scroll all the way down to the bottom in order to get all the
    # elements loaded (since Youtube dynamically loads them).
    last_height = browser.execute_script("return document.documentElement.scrollHeight")

    while True:
        # Scroll down 'til "next load".
        browser.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")

        # Wait to load everything thus far.
        time.sleep(2)

        # Calculate new scroll height and compare with last scroll height.
        new_height = browser.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # One last scroll just in case.
    browser.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")

    try:
        comment_elems = browser.find_elements(By.XPATH, '//*[@id="content-text"]')
    except exceptions.NoSuchElementException:
        error = "Error: Double check selector OR "
        error += "element may not yet be on the screen at the time of the find operation"
        print(error)
    url_comments = []
    print("> VIDEO TITLE: " + title + "\n")
    for comment in comment_elems:
        url_comments.append(comment.text)

    browser.close()
    return url_comments


# read all the json files and extract the links to a list
# then write the list to a csv file

import json
import glob

all_json_files = glob.glob("/home/appledora/Documents/bangla-ai/violens/comments/json/অত্যাচার  আদিবাসী.json")
print(len(all_json_files))

for json_file in all_json_files:
    file_comments = []
    with open(json_file) as f:
        data = json.load(f)
        for video in data:
            file_comments.extend(scrape(video["link"]))

    df = pd.DataFrame({"comments": file_comments})
    print(df.shape)
    filename = json_file.rstrip(".json")
    df.to_csv(f"{filename}.csv")
