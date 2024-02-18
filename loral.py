import os
import requests
import json

HEADERS = {
    "Content-Type": "application/json",
}

BASE_URL = "api.loral.dev/kroger"
# BASE_URL = "api.kroger.com"

def error_message(prefix, response):
    return f"ERROR: {prefix}. Status Code: {response.status_code}.\n\tError Message: {response.text}"

def product_search(search_term: str) -> str:
    """
    product_search(search_term: str) -> str
    Performs a search for products in the store based on the given search term.
    Inputs:
        search_term: str - The search term to use for the product search.
    Output: str - A JSON string containing the search results. 
        Should be an array of objects, each containing the following fields:
        - upc: str - The UPC of the product.
        - brand: str - The brand of the product.
        - description: str - A description of the product.
    """
    route = f"https://{BASE_URL}/v1/products"
    # route = f"https://{BASE_URL}/kroger/products/search"
    params = {
        "filter.term": search_term,
        "filter.limit": 10,
    }
    # print("Pinging the route: {route} ...".format(route=route))
    # add headers

    response = requests.get(route, params=params, headers=HEADERS)
    if response.status_code > 299:
        return error_message("Failed to search for products", response)
    response_data = response.json()
    result = [
        {
            "upc": item["upc"],
            "brand": item.get("brand", "Unknown Brand"),
            # "imageUrl": [sizeInfo["url"] for sizeInfo in item["images"][0]["sizes"] if sizeInfo["size"] == 'medium'],
            "description": item["description"],
        } for item in response_data["data"][:10]
    ]

    return json.dumps(result)

def add_to_cart(upc: str, quantity: str) -> str:
    """
    add_to_cart(upc: str, quantity: int) -> str
    Adds the quantity of the product with the given UPC to the user's cart.
    Make sure you have the user has explicitly asked you to add the product to the cart.
    Inputs:
        upc: str - The UPC of the product.
        quantity: int - The quantity of the product to add to the cart.
    Output: str - A message indicating the success or failure of the operation.
    """
    # Assuming success for demonstration purposes
    # print("Adding {num_items} to the cart ...".format(num_items=len(items)))
    route = f"https://{BASE_URL}/v1/cart/add"
    # route = f"https://{BASE_URL}/kroger/cart/add"

    request_body = {
        "items": [
            {
                "upc": upc,
                "quantity": int(quantity),
                "modality": "PICKUP"
            }
        ]
    }
    
    # print("Pinging the route: {route} ...".format(route=route))
    response = requests.put(route, json=request_body, headers=HEADERS)
    if response.status_code > 299:
        return error_message("Failed to add items to cart", response)
    return "SUCCESS"

def checkout() -> str:
    """
    checkout() -> str
    Completes the checkout process for the user's cart.
    Output: str - A message indicating the success or failure of the operation.
    """
    return "https://www.kroger.com/cart"



METHODS = [product_search, add_to_cart, checkout]

class Loral:
    def __init__(self, methods=METHODS):
        self.methods = {
            method.__name__: method
            for method in methods
        }
        self.descriptions = {
            method.__name__: method.__doc__
            for method in methods
        }
        self.initialized = False
        self.initialize("manual")

    def initialize(self, user_credentials: str) -> str:
        HEADERS["Authorization"] = f"Bearer {os.environ['LORAL_ACCESS_TOKEN']}"
        self.initialized = True
            
    def library_search(self, search_term: str) -> dict:
        if (not self.initialized):
            return "ERROR: Loral client not initialized. You must first call the `loral_initialize` method to initialize the Loral client."
        return_value = self.descriptions
        return return_value
    
    def execute_method(self, method_name: str, method_arguments: str) -> str:
        if (not self.initialized):
            return "ERROR: Loral client not initialized. You must first call the `loral_initialize` method to initialize the Loral client."
        if (method_arguments == ""):
            method_arguments = "{}"
        try:
            method_arguments = json.loads(method_arguments)
        except json.JSONDecodeError:
            return "Invalid JSON string provided for method arguments."
        if method_name not in self.methods:
            return f"Method {method_name} not found in Loral Library."
        return_value = self.methods[method_name](
            **{
                k: v for k, v in method_arguments.items() if k in self.methods[method_name].__code__.co_varnames
            }
        )
        return return_value
