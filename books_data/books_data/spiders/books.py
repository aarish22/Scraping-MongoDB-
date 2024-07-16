import scrapy
from pathlib import Path
from pymongo import MongoClient
import datetime


client = MongoClient("mongodb+srv://<username>:<password>@cluster_name.some_alpha_numeric_text.mongodb.net/")
db = client.scrapy
def insertToDb(page, title, rating, image, price, inStock):
    collection = db[page]
    doc = {
        "title":title,
        "rating":rating,
        "image":image,
        "price":price,
        "inStock":inStock,
        "date": datetime.datetime.now(tz=datetime.timezone.utc)
    }
    inserted = collection.insert_one(doc)
    return inserted.inserted_id

class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["toscrape.com"]
    start_urls = ["https://toscrape.com"]

    def start_requests(self):
        urls = [f"https://books.toscrape.com/catalogue/category/books_1/page-{page_no}.html" for page_no in range(1, 51)]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
    
    def parse(self, response):
        page = response.url.split("/")[-1].split(".")[0]
        filename = f"books-{page}.html"
        ##Path(filename).write_bytes(response.body) -- saves the file.html
        self.log(f"Saved file {filename}")
        books_info = response.css(".product_pod")
        for book in books_info:
            title = book.css("h3>a::text").get()
            #print(title)
            
            rating = book.css(".star-rating").attrib["class"].split(" ")[1]
            #print(rating)
            
            img_url = book.css(".image_container img")
            image = img_url.attrib["src"].replace("../../../media","https://books.toscrape.com/media")
            #print(img_url.attrib["src"])
            
            price = book.css(".price_color::text").get()
            #print(price)
            
            availability = book.css(".availability")
            if len(availability.css(".icon-ok")) > 0:
                inStock = True
            else:
                inStock = False            
            insertToDb(page, title, rating, image, price, inStock)