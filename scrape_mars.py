# #### Import all the dependencies

# In[148]:


# Dependencies
from bs4 import BeautifulSoup
import requests
from splinter import Browser
import pandas as pd
from pprint import pprint

def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "C:/UCB/chromedriver.exe"}
    return Browser("chrome", **executable_path, headless=True)   # headless - true - does not open the browser in a new window - silent scraping


def scrapemars_info():

        browser = init_browser()
  
        #Browse the URL to be scraped and create BeautifulSoup object
        # URL of page to be scraped
        url = 'https://mars.nasa.gov'

        # Retrieve page with the requests module
        response = requests.get(url)
        # Create BeautifulSoup object; parse with 'lxml'
        soup = BeautifulSoup(response.text, 'lxml')


        # ### NASA Mars News
        # Scrape the NASA Mars News Site and collect the latest News Title and Paragraph Text. Assign the text to variables that you can reference later.
        # Finding NASA Mars News - scraping and collecting news_title and news_p

        results = soup.find_all('ul', class_='item_list list_view')

        # Loop through returned results
        for result in results:
            # Error handling
            try:
                # Identify and return title of Latest news
                anchortag = result.find('div', class_='list_text').find('a')
                news_title = anchortag.text
              
                    
                # Identify and return link to Latest news item
                partiallink = anchortag['href']
                
                #Form the URL to the latest news 
                newsurl = url+partiallink
                
                # # use Splinter to browse to the news page
                browser.visit(newsurl)
                
                #obtain the html of the page
                newsresp = requests.get(newsurl)
                        
                # Create BeautifulSoup object; parse with 'lxml'
                news_soup = BeautifulSoup(newsresp.text, 'lxml')
                news_results = news_soup.find_all('div', class_="wysiwyg_content")
                for news in news_results:
                    
                    ptags = news.find_all('p')
                
                    for ptag in ptags:
                        
                        if ptag.text:
                            news_p = ptag.text
                            break
                        else:
                            continue
                    break
        
            except Exception as e:
                print(e)


        # ### JPL Mars Space Images - Featured Image
         
        # Visit the url for JPL Featured Space Image here.

        JPLurl = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'

        #Use splinter to navigate the site and find the image url for the current Featured Mars Image and 
        #assign the url string to a variable

        browser.visit(JPLurl)
        JPLresp = requests.get(JPLurl)  

        # Create BeautifulSoup object; parse with 'lxml'
        JPL_soup = BeautifulSoup(JPLresp.text, 'lxml')

        FullImgbuttontag= JPL_soup.find('a', class_="button fancybox")

        # Constructing the URL to the Image article
        spaceurl = (browser.url).split("?")[0]
        partialURL = FullImgbuttontag['data-link'].split("spaceimages/")[1]
        imgartURL = spaceurl+partialURL

        browser.visit(imgartURL)
        imgresp = requests.get(imgartURL)  

        # Create BeautifulSoup object; parse with 'lxml'
        img_soup = BeautifulSoup(imgresp.text, 'lxml')


        # #### JPL Mars Space Images - Featured Image

        figtag = img_soup.find('figure', class_="lede")
        imgtaghref = figtag.find('a')['href'].split("/spaceimages/")[1]

        featured_image_url = spaceurl+imgtaghref

        # #### Mars Weather

        marstwitterurl = "https://twitter.com/marswxreport?lang=en"
        tweetresp = requests.get(marstwitterurl)  

        tweet_soup = BeautifulSoup(tweetresp.text, 'lxml')


        for eachlitag in tweet_soup.find_all('li', class_="stream-item"):      # Loop through all tweets
            
            contentdiv = eachlitag.find('div', class_="content")                    # content div
            divstreamheader = contentdiv.find('div', class_="stream-item-header")   #finding stream-item-header to identify the user
            atagdivstream = divstreamheader.find('a')
        
            if atagdivstream['href'] =='/MarsWxReport':                                   # Filtering tweet from MarsWxReport
                ptagtweet = contentdiv.find('div', class_="js-tweet-text-container").find('p')  # find the ptag with the tweetcontent
                ptagtweet.a.decompose()                                     # remove the anchor tag with the <p> tag
                mars_weather = ptagtweet.text
                break
            else:
                continue
            
        
        # ### Mars Facts

        factsurl = "https://space-facts.com/mars/"

        #use Pandas to scrape the table containing facts about the planet including Diameter, Mass, etc.
        tables = pd.read_html(factsurl)

        factsdf = tables[0]
        factsdf.columns = ["Description" , "Values"]

        # display the content of the DataFrame
        factsdf.head()
        factsdf.reset_index(drop=True, inplace=True)

        marsfactsdesc = factsdf["Description"].tolist()
        marsfactsvalues= factsdf["Values"].tolist()

        #Use Pandas to convert the data to a HTML table string.
        # MarsFacts_table =factsdf.to_html()

        # ### Mars Hemispheres

        #Visit the USGS Astrogeology site here to obtain high resolution images for each of Mar's hemispheres.
        hemi_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"

        hemi_result = requests.get(hemi_url)
        hemi_soup = BeautifulSoup(hemi_result.text, "lxml")
    
        # scraping the data
        resultitems = hemi_soup.find('div' , class_="collapsible results").find_all('div', class_="item")

        hemisphere_image_urls =[]
        eachhemisphere = {}

        Astrourldomain = hemi_url.split("/search")[0]

        for item in resultitems:
            title = item.find('h3').text
            
            itempartialurl = item.find('a')['href']
            #url to browse
            itemurl = Astrourldomain+itempartialurl
            
            # browse to the url
            browser.visit(itemurl)
            hemi_item_result = requests.get(itemurl)
            hemi_item_soup = BeautifulSoup(hemi_item_result.text, "lxml")
            
            aimgtag = hemi_item_soup.find('div', class_="downloads").find('a')
            img_url = aimgtag['href']
        
            eachhemisphere = {"title":title, "img_url":img_url}
            hemisphere_image_urls.append(eachhemisphere)           


      #  Dictionary to be inserted as a MongoDB document
        mars_data = {
        'title': news_title ,
         'news_paragraph': news_p, 
         "featured_image_url" : featured_image_url,
         "mars_weather" :mars_weather, 
         "marsfactsdesc" : marsfactsdesc,
         "marsfactsvalues" : marsfactsvalues, 
         "hemisphere_image_urls" : hemisphere_image_urls
         }

    # Close the browser after scraping
        browser.quit()

        return mars_data

