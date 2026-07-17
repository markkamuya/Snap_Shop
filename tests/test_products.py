import unittest
from unittest.mock import Mock, patch

from backend.products import search_products


EBAY_RESPONSE = """\
<findItemsByKeywordsResponse xmlns="http://www.ebay.com/marketplace/search/v1/services">
  <searchResult count="2">
    <item>
      <title>Budget Milk</title>
      <sellingStatus><currentPrice>2.50</currentPrice></sellingStatus>
      <sellerInfo><feedbackScore>90</feedbackScore></sellerInfo>
      <viewItemURL>https://example.com/ebay-budget</viewItemURL>
    </item>
    <item>
      <title>Popular Milk</title>
      <sellingStatus><currentPrice>4.00</currentPrice></sellingStatus>
      <sellerInfo><feedbackScore>250</feedbackScore></sellerInfo>
      <viewItemURL>https://example.com/ebay-popular</viewItemURL>
    </item>
  </searchResult>
</findItemsByKeywordsResponse>
"""


class SearchProductsTests(unittest.TestCase):
    @patch("backend.products.requests.get")
    def test_returns_cheapest_and_highest_rated_for_each_marketplace(self, get):
        ebay = Mock(status_code=200, text=EBAY_RESPONSE)
        amazon = Mock(status_code=200)
        amazon.json.return_value = {
            "data": {
                "products": [
                    {
                        "product_title": "Budget Milk",
                        "product_minimum_offer_price": "$3.25",
                        "product_star_rating": "4.1",
                        "product_url": "https://example.com/amazon-budget",
                        "is_prime": True,
                    },
                    {
                        "product_title": "Premium Milk",
                        "product_minimum_offer_price": "$5.50",
                        "product_star_rating": "4.9",
                        "product_url": "https://example.com/amazon-premium",
                    },
                ]
            }
        }
        get.side_effect = [ebay, amazon]

        result = search_products("milk")

        self.assertEqual(result["cheapest_ebay"]["title"], "Budget Milk")
        self.assertEqual(result["highest_rated_ebay"]["title"], "Popular Milk")
        self.assertEqual(result["cheapest_amazon"]["title"], "Budget Milk")
        self.assertEqual(result["highest_rated_amazon"]["title"], "Premium Milk")
        self.assertEqual(get.call_count, 2)

    @patch("backend.products.requests.get")
    def test_returns_empty_results_when_services_fail(self, get):
        get.return_value = Mock(status_code=503)

        result = search_products("milk")

        self.assertEqual(
            result,
            {
                "cheapest_ebay": None,
                "cheapest_amazon": None,
                "highest_rated_ebay": None,
                "highest_rated_amazon": None,
            },
        )


if __name__ == "__main__":
    unittest.main()
