from fridge_scraping_class import EuronicsScraper

# scrape first 1 pages
Scrapper = EuronicsScraper()
Extracted_data = Scrapper.scrape_all_pages(num_pages=1)

#Write the data to a CSV file:
Extracted_data.to_csv('extracted_data.csv', index=False)
