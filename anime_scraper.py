"""
Something I learned from making this webscraper. If the layout of the page changes, the entire code breaks

This will quickly go out of date...

FAQ:
Q: Why am I getting X error. Nothing is working. This is a very bad scraper. Don't use it.
A: I dont know how much to stress on this, if gogoanime is ever down, or ever changes its layout, of course this program will stop working, because it is very specific.
It only works for gogoanime and clones, and will only work with the gogoanime site that existed during the time of this program's making. If gogoanime ever changes, or something else replaces, it will not work.
Please take note that web scrapers will always be very specific, and so you'll face these problems with all web scrapers. So calling this a bad scraper is mainly ambigous, since if you take it that way, all scrapers are bad.

Q: Why is the code so messy! I can't even make sense of it.
A: I'm not a professional developer, so it's definitely going to be a bit messy. I code for hobby, and this was code written for another one of my hobbies, Anime.
This is a personal project, and somewhat documented if anyone else wants to use it as an API. Please don't take it seriously. And please don't try to understand it, its very specific and even me, the author can't fully explain every single function call I make.

Q: Why did you do X instead of Y
A: Email me at rsa165.ali@gmail.com. If you really want to know, I will explain. Also I'm dumb, and maybe the way you suggest is better, more pythonic, etc.

Q: Why didn't you use class_ in beautiful soup?
A: After the time of writing thise entire program, I realized that I could've just done that. When I was making the program, I tried 'class=XY' but of course that gave me an error. I didn't throughly read through the docs and apparently you were supposed to type class_. I'm too lazy to right this program from scratch,
so I suppose I'll leave it as it is. In a way, it may be a bit better not depending on class names, but too specific. 


"""


from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


# Using Gogoanime, will only work with gogoanime and clones. WARNING: Changing base url to something that isnt gogoanime will break the entire scraper.
BASE_URL = "https://www1.gogoanime.ai"

class SearchResultNotFound(Exception):
    pass


# Main API
class AnimeScraper:
    def get_search_results(self, text: str, unformatted=False):
        # Get search page, anime name will be passed as ?keyword=[anime_name]
        r = requests.get(f"{BASE_URL}/search.html", params={"keyword": text})
        soup = BeautifulSoup(r.text, 'html.parser')

        # Scraping (Very specific, will most likely break if Gogoanime Layout changes
        results = soup.findAll("ul")[3].findAll("a")
        results = [str(result) for result in results]
        results = [result for result in results if not 'img' in result]
        if not unformatted:
            try:
                results = [result.split("title=")[1].split(">")[0].replace('"', '') for result in results]
            except:
                results = soup.findAll("ul")[4].findAll("a")
                results = [str(result) for result in results]
                results = [result for result in results if not 'img' in result]
                if not unformatted:
                    results = [result.split("title=")[1].split(">")[0].replace('"', '') for result in results]
                    
        if 'data-page' in results[0]:
            results = soup.findAll("ul")[4].findAll("a")
            results = [str(result) for result in results]
            results = [result for result in results if not 'img' in result]
            if not unformatted:
                results = [result.split("title=")[1].split(">")[0].replace('"', '') for result in result]

        if results == []:
            results = soup.findAll("ul")[4].findAll("a")
            results = [str(result) for result in results]
            results = [result for result in results if not 'img' in result]
            if not unformatted:
                results = [result.split("title=")[1].split(">")[0].replace('"', '') for result in results]
            if results == []:
                raise SearchResultNotFound("Sorry, Result Was Not Found")
        return results

    def get_image_results(self, text: str):
        r = requests.get(f"{BASE_URL}/search.html", params={"keyword": text})
        soup = BeautifulSoup(r.text, 'html.parser')
        results = soup.findAll("ul")[4].find_all("a")
        results = [str(result) for result in results]
        results = [result.splitlines()[1].split("src=")[1].split("/>")[0].replace('"', '') for result in results if 'img' in result]

        if results == []:
            results = soup.findAll("ul")[3].find_all("a")
            results = [str(result) for result in results]
            results = [result.splitlines()[1].split("src=")[1].split("/>")[0].replace('"', '') for result in results if 'img' in result]
            if results == []:
                raise SearchResultNotFound("Sorry, Result Was Not Found")

        return results

    def get_page_links(self, text:str):
        results = self.get_search_results(text, True)
        results = [BASE_URL + result.split("href=")[1].split("title")[0].replace(" ", "").replace('"', '') for result in results]
        results = sorted(set(results))
        return results

    def get_video_link(self, anime_name: str, episode_number: int, anime_index: int):
        # Reason i use selenium is to load video stream and actually play it in order to capture video url.
        results = self.get_page_links(anime_name)
        anime_page = results[anime_index]
        anime_ep_page = BASE_URL + anime_page.split("category")[1] + f"-episode-{episode_number}"
        r = requests.get(anime_ep_page)
        soup = BeautifulSoup(r.text, 'html.parser')
        print(anime_ep_page)
        ep_page = "https://" + str(soup.iframe).split("src=")[1].split('>')[0].replace('"', '')
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('--ignore-certificate-errors-spki-list')
        options.add_argument('--ignore-ssl-errors')
        driver = webdriver.Chrome(options=options)
        driver.get(ep_page)
        elem = driver.find_element_by_tag_name("video")
        elem.send_keys(Keys.SPACE)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()
        return str(soup.video).split("src=")[1].split(" ")[0].replace('"', '')

    def get_anime_info(self, anime_name:str, anime_index: int):
        page_links = self.get_page_links(anime_name)
        print(anime_index)
        print(page_links)
        print(anime_name)
        page = page_links[anime_index]
        r = requests.get(page)
        soup = BeautifulSoup(r.content, "html.parser")
        # Nicely format anime info into a dictionary
        results = {}
        results.update({
            "type": str(soup.find_all("p")[1].a).split(">")[1].split("<")[0],
            "plot_summary": str(soup.find_all("p")[2]).split("span>")[2].split("</p>")[0].replace("\n", ""),
            "genres": [str(a).replace(", ", "").split(">")[1].split("<")[0] if ', ' in str(a) else str(a).split(">")[1].split("<")[0] for a in soup.find_all("p")[3].find_all("a")],
            "release_date": str(soup.find_all("p")[4]).split(">")[3].split("<")[0],
            "status": str(soup.find_all("p")[5].a).split(">")[1].split("<")[0],
            "other_name": str(soup.find_all("p")[6]).split(">")[3].split("</p")[0]
            })
        return results
        
        

# Example demonstrating api use. 
if __name__ == "__main__":
    scraper = AnimeScraper()
    s = input("[+] What anime are you looking for?\n> ")
    look = input("[+] Looking for image links, anime page links, episode links, search results of anime, or anime info? (I/C/E/S/A)\n>").lower()
    if look == "i":
        results = scraper.get_image_results(s)
        print(results)
        print("Search Results:")
        for result in results:
            print(result)
    if look == "s":
        results = scraper.get_search_results(s)
        print("Search Results:\n---------------------------------")
        for result in results:
            print(result)
    if look == "c":
        results = scraper.get_page_links(s)
        print("Search Results:\n---------------------------------")
        for result in results:
            print(result)
    if look == "e":
        ep_num = input("[+] Episode Number?: \n>")
        index = input("[+] Anime Index?: \n>")
        results = scraper.get_video_link(s, int(ep_num), int(index))
        print(results)
    if look == "a":
        index = input("[+] Anime Index?: \n>")
        results = scraper.get_anime_info(s, int(index))
        print(f"""
RESULTS
==============================

Type: {results['type']}

Summary: {results['plot_summary']}

Genres: {', '.join(results['genres'])}

Released: {results['release_date']}

Status: {results['status']}

Other Name(s): {results['other_name']}

""")
    
