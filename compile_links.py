from selenium import webdriver
import json
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

options = {}
chrome_options = Options()
chrome_options.add_argument("--user-data-dir=hash")
chrome_options.add_argument("--disable-dev-shm-usage")
sort_by = "CAM%253D"  # sort by view count

def get_video_results(output_dir, search_query):
    driver = webdriver.Chrome(options=chrome_options)
    SEARCH_PATH = f"https://www.youtube.com/results?search_query={search_query}&sp={sort_by}"
    print(SEARCH_PATH)
    driver.get(SEARCH_PATH)

    youtube_data = []

    # scrolling to the end of the page
    # https://stackoverflow.com/a/57076690/15164646
    count = 0
    while True:
        # end_result = "No more results" string at the bottom of the page
        # this will be used to break out of the while loop
        # end_result = driver.find_element_by_css_selector('#message').is_displayed()
        end_result = driver.find_element(By.CSS_SELECTOR, "#message").is_displayed()
        driver.execute_script(
            "var scrollingElement = (document.scrollingElement || document.body);scrollingElement.scrollTop = scrollingElement.scrollHeight;"
        )
        # time.sleep(1) # could be removed
        print(end_result)
        count += 1
        # once element is located, break out of the loop
        if count == 10 or end_result:
            break

    print("Extracting results. It might take a while...")

    for result in driver.find_elements(By.CSS_SELECTOR, ".text-wrapper.style-scope.ytd-video-renderer"):
        print(result)
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

        youtube_data.append(
            {
                "title": title,
                "link": link,
                "views": views,
                "time_published": time_published,
                "snippet": snippet,
            }
        )

    # save the results to a json file
    output_path = os.path.join(output_dir, "output")
    with open(f"{}{search_query}.json", "w") as f:
        json.dump(youtube_data, f, indent=4)
    # properly stop the driver
    driver.quit()


