from requests_html import HTMLSession
from pandas import DataFrame
from numpy import NaN


class Product:

    def __init__(self, asin: str) -> None:
        self.asin = asin
        self.session = HTMLSession()

        self.headers = {
                        "authority": "www.amazon.nl",
                        "pragma": "no-cache",
                        "cache-control": "no-cache",
                        "dnt": "1",
                        "upgrade-insecure-requests": "1",
                        "user-agent": "Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36",
                        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                        "sec-fetch-site": "none",
                        "sec-fetch-mode": "navigate",
                        "sec-fetch-dest": "document"
                    }
        
        self.url = f'https://www.amazon.nl/product-reviews/{self.asin}/ref=cm_cr_arp_d_paging_btm_next_'

        # saving title, price, and stars
        resp = self.session.get(f'https://www.amazon.nl/dp/{self.asin}/ref=cm_cr_arp_d_product_top?ie=UTF8', headers=self.headers)

        self.title = resp.html.find('div[id=titleSection]', first=True).find('span[id=productTitle]', first=True).text
        self.price = resp.html.find('span[class=a-offscreen]', first=True).text
        self.stars = resp.html.find('div[id=averageCustomerReviews]', first=True).find('span[class=a-icon-alt]', first=True).text[:3]



    def page(self, page: int):
        resp = self.session.get(self.url + str(page) + '?pageNumber=' + str(page) + '&sortBy=recent', headers=self.headers)
        # resp.html.render(sleep=1)

        rev = resp.html

        if not rev.find('div[data-hook=review]'):
            return False
        else:
            return rev.find('div[data-hook=review]')
        

    def parse(self, reviews):
        total = []

        for review in reviews:
            try:
                title = review.find('span[data-hook=review-title]', first=True).text
            except:
                try:
                    title = review.find('a[data-hook=review-title]', first=True).text
                except:
                    title = ''

            try:
                rating = review.find('i[data-hook=cmps-review-star-rating] span', first=True).text[:3]
            except:
                try:
                    rating = review.find('i[data-hook=review-star-rating] span', first=True).text[:3]
                except:
                    rating = NaN

            try:
                body = review.find('span[data-hook=review-body] span', first=True).text.replace('\n','').strip()[:200]
            except:
                body = ''

            try:
                date_raw = review.find('span[data-hook=review-date]', first=True).text[14:].split(' op ')
                country = date_raw[0]
                date = date_raw[1]
            except:
                country = NaN
                date = NaN
            

            data = {'title': title, 'rating': rating, 'body': body, 'date': date, 'country': country}

            total.append(data)

        return total
    
    def reviews_byPage(self, page=1):
        return self.parse(self.page(page))
    
    def reviews(self):
        reviews = []

        x = 0

        while True:
            x += 1
            product_reviews = self.page(x)
            # print(x)
            # print(product_reviews)
            if product_reviews is not False:
                reviews.extend(self.parse(product_reviews))
            else:
                print('no more pages')
                break
        
        return reviews
    
    def save_reviews(self):
        df = DataFrame(self.reviews())
        df.to_csv(f'{self.asin}-reviews.csv')

    
if __name__ == '__main__':
    amz = Product('B00JEXZ6NA')
    print(amz.title)
    print(amz.price)
    print(amz.stars)

    # reviews = []
    # x=0
    # while True:
    #     x += 1
    #     product_reviews = amz.page(x)
    #     print(x)
    #     # print(product_reviews)
    #     if product_reviews is not False:
    #         reviews.append(amz.parse(product_reviews))
    #     else:
    #         print('no more pages')
    #         break
    # print(reviews)

    # print(amz.reviews())

    amz.save_reviews()

    