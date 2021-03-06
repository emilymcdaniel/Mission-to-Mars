# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt

def scrape_all():
    # Initiate headless driver for deployment
    browser = Browser("chrome", executable_path="chromedriver", headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemispheres": mars_hemispheres(browser)
    }

    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):

    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one("ul.item_list li.slide")
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find("div", class_="content_title").get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find("div", class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None

    return news_title, news_p

def featured_image(browser):
    # Visit URL
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'

    return img_url

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

def mars_hemispheres(browser):
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    hemisphere_image_urls = []

    html = browser.html
    hemis_soup = soup(html, 'html.parser')

    hemis = hemis_soup.find_all('div', class_='item')

    title_list = []        
    rel_href_list = []

    for hemi in hemis:
        title = hemi.find('h3').get_text()
        link = hemi.find('a')
        href = link['href']
        img_urls = f'https://astrogeology.usgs.gov{href}' 
        title_list.append(title)
        
        browser.visit(img_urls)
        html2 = browser.html
        img_soup = soup(html2, 'html.parser')
        image_link = img_soup.find_all('div', class_="downloads")

        for image in image_link:
            rel_image_path = image.find('a')
            rel_image_href = rel_image_path['href']
            rel_href_list.append(rel_image_href)

    hemisphere_image_urls = [{'title': title_list, 'img_url': rel_href_list} for title_list,rel_href_list in zip(title_list,rel_href_list)]
    return hemisphere_image_urls


## ALTERNATE HEMI ATTEMPT
# 
# def mars_hemispheres(browser):
#     url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
#     browser.visit(url)

        # sample_element = hemi.find('a', text="Sample").get('href')

        # hemisphere = {'title': title, 'img_url': sample_element}

#     hemisphere_image_urls = []
#     for i in range(0,4):
#         browser.find_by_css("a.product-item h3")[i].click()
#         
        # hemi = soup(browser.html, "html.parser")
        # title = hemi.find('h2', class_="title").get_text()hemisphere = scrape_hemisphere(browser.html)
#         hemisphere_image_urls.append(hemisphere)
#         browser.back()

# def scrape_hemisphere(html_text):
#     # parse html text
#     hemi_soup = soup(html_text, "html.parser")
#     # adding try/except for error handling
#     try:
#         title_elem = hemi_soup.find("h2", class_="title").get_text()
#         sample_elem = hemi_soup.find("a", text="Sample").get("href")
#     except AttributeError:
#         # Image error will return None, for better front-end handling
#         title_elem = None
#         sample_elem = None
#     hemispheres = {
#         "title": title_elem,
#         "img_url": sample_elem
#     }
#     return hemispheres

if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())