import requests
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import pandas as pd
import re 

class EuronicsScraper:
    def __init__(self):
        self.driver = None
        self.all_product_details = pd.DataFrame()
        
    def start_driver(self):
        options = webdriver.ChromeOptions()
        #options.add_argument('--headless') # run in headless mode
        self.driver = webdriver.Chrome(ChromeDriverManager().install(),  options=options)

        
    def close_driver(self):
        self.driver.quit()

    def scrape_page(self, url):
        response = requests.get(url)
        soup     = BeautifulSoup(response.content, "html.parser")

        product_list = soup.find_all("div", class_="details")

        for product in product_list:
            product_dict = {}
            link = product.find("h2", class_="product-title").find("a").get("href")
            product_url = "https://www.euronics.gr" + link

            try:
                self.driver.get(product_url)
                ribbon_picture = self.driver.find_element(By.ID, "ribbon-picture-6-7061-126")
                ribbon_picture_src = ribbon_picture.get_attribute("src")
                product_dict["Discount"] = ["Yes"]
            except NoSuchElementException:
                ribbon_picture_src = None
                product_dict["Discount"] = ["No"]

            response = requests.get(product_url)
            soup     = BeautifulSoup(response.text, 'lxml')

            product_dict["Price"] = [soup.find("div", class_="product-price").text.strip()]
            product_dict["short_description"] = [soup.find("div", class_="short-description").text.strip()]
            product_dict["full-description"]  = [soup.find("div", class_="full-description").text.strip()]

            text =  product_dict["full-description"][0]
            # use regular expression to find the pattern of the size
            size_pattern = r"(\d{3,4}(?:[,.]\d{1,2})?)\s*[xX/]\s*(\d{2,3}(?:[,.]\d{1,2})?)\s*[xX/]\s*(\d{2,3}(?:[,.]\d{1,2})?)"

            size_match = re.search(size_pattern, text)

            if size_match:
                product_dict["height"] = size_match.group(1)
                height = product_dict["height"]
                product_dict["width"]  = size_match.group(2)
                width = product_dict["width"] 
                product_dict["depth"]  = size_match.group(3)
                depth = product_dict["depth"]
                print(f"The fridge dimensions are {height} cm (height) x {width} cm (width) x {depth} cm (depth)")
            else:
                print("Could not find fridge dimensions")

            product_details = pd.DataFrame(product_dict)
            self.all_product_details = pd.concat([self.all_product_details, product_details])

    def scrape_all_pages(self, num_pages=10):
        self.start_driver()
        for i in range(1, num_pages+1):
            url = f"https://www.euronics.gr/%CF%88%CF%85%CE%B3%CE%B5%CE%B9%CE%BF%CE%BA%CE%B1%CF%84%CE%B1%CF%88%CF%8D%CE%BA%CF%84%CE%B5%CF%82#/pageSize/60/pageNumber/{i}"
            self.scrape_page(url)
        self.close_driver()
        return self.all_product_details
