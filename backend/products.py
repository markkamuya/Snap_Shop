import requests
import xml.etree.ElementTree as ET
from config import EBAY_APP_ID, AMAZON_RAPIDAPI_KEY  # import private keys

# Correct sandbox App ID
app_id = EBAY_APP_ID  # Make sure this is the correct sandbox App ID
production_url = 'https://svcs.ebay.com/services/search/FindingService/v1'  # Production URL
sandbox_url = 'https://svcs.sandbox.ebay.com/services/search/FindingService/v1'  # Sandbox URL

# Define the base API URL based on your environment
api_url = production_url  # Use sandbox during testing, change to production when ready

def search_products(keywords, entries_per_page=5, page_number=1):
    """
    Searches for products on both eBay and Amazon based on the given keywords.
    Returns both the product with the lowest price and the highest rating from each platform (eBay and Amazon).

    :param keywords: Search term(s) for products
    :param entries_per_page: Number of items per page (for eBay, default: 5)
    :param page_number: Page number for pagination (for eBay, default: 1)
    :return: Dictionary containing the cheapest and highest-rated product from eBay and Amazon.
    """
    
    # eBay search logic
    ebay_results = []
    ebay_api_url = 'https://svcs.ebay.com/services/search/FindingService/v1'
    ebay_params = {
        'OPERATION-NAME': 'findItemsByKeywords',
        'SERVICE-VERSION': '1.0.0',
        'SECURITY-APPNAME': EBAY_APP_ID,  # Use imported private App ID
        'keywords': keywords,
        'paginationInput.entriesPerPage': str(entries_per_page),
        'paginationInput.pageNumber': str(page_number),
    }
    
    ebay_response = requests.get(ebay_api_url, params=ebay_params)
    
    if ebay_response.status_code == 200:
        try:
            ebay_root = ET.fromstring(ebay_response.text)
            search_result = ebay_root.find('.//{http://www.ebay.com/marketplace/search/v1/services}searchResult')
            if search_result is not None:
                ebay_items = search_result.findall('{http://www.ebay.com/marketplace/search/v1/services}item')
                for item in ebay_items:
                    title = item.find('{http://www.ebay.com/marketplace/search/v1/services}title').text
                    price = float(item.find('.//{http://www.ebay.com/marketplace/search/v1/services}currentPrice').text)
                    rating = item.find('.//{http://www.ebay.com/marketplace/search/v1/services}feedbackScore')
                    rating_value = float(rating.text) if rating is not None else 0.0  # Default to 0 if no rating
                    url = item.find('{http://www.ebay.com/marketplace/search/v1/services}viewItemURL').text
                    ebay_results.append({
                        'title': title,
                        'price': price,
                        'rating': rating_value,
                        'url': url
                    })
        except ET.ParseError as e:
            print("Error parsing eBay response:", e)

    # Amazon search logic
    amazon_results = []
    amazon_url = "https://real-time-amazon-data.p.rapidapi.com/search"
    amazon_headers = {
        "X-RapidAPI-Host": "real-time-amazon-data.p.rapidapi.com",
        "X-RapidAPI-Key": AMAZON_RAPIDAPI_KEY  # Use imported RapidAPI key
    }
    amazon_params = {
        "query": keywords,
        "country": "US",
        "limit": 10
    }
    
    amazon_response = requests.get(amazon_url, headers=amazon_headers, params=amazon_params)
    
    if amazon_response.status_code == 200:
        try:
            amazon_data = amazon_response.json()
            if isinstance(amazon_data, dict) and 'data' in amazon_data:
                products_data = amazon_data['data']
                if 'products' in products_data and isinstance(products_data['products'], list):
                    for product in products_data['products']:
                        title = product.get('product_title', 'N/A')
                        price = float(product.get('product_minimum_offer_price', '0').replace('$', '').replace(',', ''))
                        rating = product.get('product_star_rating', None)
                        rating_value = float(rating) if rating else 0.0  # Default to 0 if no rating
                        url = product.get('product_url', 'N/A')
                        amazon_results.append({
                            'title': title,
                            'price': price,
                            'rating': rating_value,
                            'url': url,
                            'is_prime': product.get('is_prime', False)
                        })
        except Exception as e:
            print(f"Error processing Amazon response: {e}")
    
    # Get the cheapest product from eBay and Amazon
    cheapest_ebay = min(ebay_results, key=lambda x: x['price'], default=None) if ebay_results else None
    cheapest_amazon = min(amazon_results, key=lambda x: x['price'], default=None) if amazon_results else None
    
    # Get the highest-rated product from eBay and Amazon
    highest_rated_ebay = max(ebay_results, key=lambda x: x['rating'], default=None) if ebay_results else None
    highest_rated_amazon = max(amazon_results, key=lambda x: x['rating'], default=None) if amazon_results else None
    result = {
        'cheapest_ebay': cheapest_ebay,
        'cheapest_amazon': cheapest_amazon,
        'highest_rated_ebay': highest_rated_ebay,
        'highest_rated_amazon': highest_rated_amazon
    }
    print(result)
    return result