from selenium import webdriver
import json
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import argparse
from tqdm import tqdm

# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

chrome_options = Options()
chrome_options.add_argument("--user-data-dir=hash")
chrome_options.add_argument("--disable-dev-shm-usage")
sort_by = "CAM%253D"  # sort by view count


def get_video_results(output_dir=".", search_query="python", max_scroll=3, number_of_videos=10):
    """
    A utility function to get the video results from a search query.
    The results are sorted by view count and saved to a json file.
    """
    driver = webdriver.Chrome(options=chrome_options)
    SEARCH_PATH = f"https://www.youtube.com/results?search_query={search_query}&sp={sort_by}"
    driver.get(SEARCH_PATH)
    time.sleep(2)
    youtube_data = []
    print(f"Scraping videos for {search_query} ...")
    # scrolling to the end of the page
    # https://stackoverflow.com/a/57076690/15164646
    count = 0
    last_video = None  # Track the last video in the youtube_data list
    while True:
        # Check if the last video is already in the youtube_data list
        if last_video in youtube_data:
            break

        # Scroll to the bottom of the page
        driver.execute_script(
            "var scrollingElement = (document.scrollingElement || document.body);scrollingElement.scrollTop = scrollingElement.scrollHeight;"
        )
        time.sleep(1)  # Add a small delay for the new videos to load

        # Update the last_video variable with the last video in the youtube_data list
        last_video = youtube_data[-1]["link"] if youtube_data else None

        count += 1
        # once the desired number of videos is reached, break out of the loop
        # for infinite scroll, set max_scroll -1
        if count == max_scroll:
            break
    results = driver.find_elements(By.CSS_SELECTOR, ".text-wrapper.style-scope.ytd-video-renderer")
    for result in tqdm(results, total=number_of_videos, colour="green", desc="Extracting video data"):
        if len(youtube_data) == number_of_videos:
            break
        title = result.find_element(By.CSS_SELECTOR, ".title-and-badge.style-scope.ytd-video-renderer").text
        link = result.find_element(By.CSS_SELECTOR, ".title-and-badge.style-scope.ytd-video-renderer a").get_attribute(
            "href"
        )
        views = result.find_element(By.CSS_SELECTOR, ".style-scope ytd-video-meta-block").text.split("\n")[0]

        try:
            time_published = result.find_element(By.CSS_SELECTOR, ".style-scope ytd-video-meta-block").text.split(
                "\n"
            )[1]
        except:
            time_published = None

        try:
            snippet = result.find_element(By.CSS_SELECTOR, ".metadata-snippet-container").text
        except:
            snippet = None

        # get the video id from the link
        id = link.split("=")[-1]

        youtube_data.append(
            {
                "video_id": id,
                "title": title,
                "link": link,
                "views": views,
                "time_published": time_published,
                "snippet": snippet,
            }
        )

    # save the results to a json file
    output_path = os.path.join(output_dir, f"{search_query}.json")
    with open(output_path, "w") as f:
        json.dump(youtube_data, f, indent=4)
    # properly stop the driver
    # driver.quit()


if __name__ == "__main__":
    # get parameters from the command line

    parser = argparse.ArgumentParser()

    parser.add_argument("--query_file", type=str, default="query.txt", help="Path to the search query file")
    parser.add_argument("--output_dir", type=str, default="links", help="Path to the output directory")
    parser.add_argument("--max_scroll", type=int, default=3, help="Max number of times to scroll the page")
    parser.add_argument("--number_of_videos", type=int, default=10, help="Number of videos to scrape per query")

    args = parser.parse_args()
    query_list = []
    with open(args.query_file, "r") as f:
        for line in f:
            query_list.append(line.strip())

    print(f"Found {len(query_list)} queries in {args.search_query_file}")
    for query in tqdm(query_list, colour="blue", desc="Queries"):
        get_video_results(
            output_dir=args.output_dir,
            search_query=query,
            max_scroll=args.max_scroll,
            number_of_videos=args.number_of_videos,
        )

    print("Done!")
