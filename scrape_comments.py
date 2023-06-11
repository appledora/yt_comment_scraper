from selenium import webdriver
import time
import pandas as pd
import time
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import time
import os
import argparse
import json
import glob
from selenium.webdriver.common.by import By
from selenium.common import exceptions

options = {}
chrome_options = Options()
chrome_options.add_argument("--user-data-dir=hash")
chrome_options.add_argument("--disable-dev-shm-usage")


def scrape(url="", max_scroll=3, number_of_comments=10):

    browser = webdriver.Chrome(options=chrome_options)

    browser.get(url)
    time.sleep(5)

    try:
        # Extract the elements storing the comment section.
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
    scoll_count = 0
    while True:
        # Scroll down 'til "next load".
        browser.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        if scoll_count == max_scroll:
            break
        # Wait to load everything thus far.
        time.sleep(2)

        # Calculate new scroll height and compare with last scroll height.
        new_height = browser.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        scoll_count += 1

    # One last scroll just in case.
    browser.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")

    try:
        comment_elems = browser.find_elements(By.XPATH, '//*[@id="content-text"]')
    except exceptions.NoSuchElementException:
        error = "Error: Double check selector OR "
        error += "element may not yet be on the screen at the time of the find operation"
        print(error)

    if len(comment_elems) < number_of_comments:
        number_of_comments = len(comment_elems)
    url_comments = []
    # print("> VIDEO TITLE: " + title + "\n")
    for comment in comment_elems[:number_of_comments]:
        url_comments.append(comment.text)

    browser.close()
    return url_comments


if __name__ == "__main__":
    # scrape("https://www.youtube.com/watch?v=2lK4W6l7vO8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--json_directory", type=str, default="links", help="directory of json files containing links")
    parser.add_argument("--output_directory", type=str, default="comments", help="directory to save the csv files")
    parser.add_argument("--max_scroll", type=int, default=4, help="max number of scrolls to perform")
    parser.add_argument("--max_comments", type=int, default=100, help="max number of comments to scrape")
    args = parser.parse_args()
    json_file_dir = os.path.join(args.json_file_directory, "*.json")
    json_files = glob.glob(json_file_dir)
    print(f"{len(json_files)} json files found at {json_file_dir}")
    for json_file in json_files:
        file_comments = []
        file_ids = []
        with open(json_file) as f:

            data = json.load(f)
            for video in data:
                temp_comments = scrape(video["link"], args.max_scroll, args.max_comments)
                temp_ids = [video["video_id"]] * len(temp_comments)
                file_comments.extend(temp_comments)
                file_ids.extend(temp_ids)

        df = pd.DataFrame({"comments": file_comments, "video_id": file_ids})
        filename = json_file.split("/")[-1].rstrip(".json") + "_comments.csv"
        output_path = os.path.join(args.output_directory, filename)

        df.to_csv(output_path, index=False)
