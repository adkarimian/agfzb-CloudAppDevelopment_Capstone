import requests
import json
from .models import CarDealer,DealerReview
from requests.auth import HTTPBasicAuth


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs) 
        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)
        return json_data
    except Exception as ex:
        # If any error occurs
        print("Network exception occurred")
    
# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    print(kwargs)
    print("POST to{} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.post(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs,json=json_payload)
        status_code = response.status_code
        #print("With status {} ".format(status_code))
        #json_data = json.loads(response.text)
        return status_code
    except:
        # If any error occurs
        print("Network exception occurred")

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["dbs"]["rows"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url,dealerId=kwargs['dealerId'])
    if json_result:
        reviews = json_result["dbs"]["docs"]
        for review in reviews:
            review_doc = review
            review_obj = DealerReview(id=review_doc["_id"],
                                      name=review_doc["name"],
                                      dealership=review_doc["dealership"],
                                      purchase=review_doc["purchase"],
                                      review=review_doc["review"],
                                      purchase_date=review_doc["purchase_date"],
                                      car_make=review_doc["car_make"],
                                      car_model=review_doc["car_model"],
                                      car_year=review_doc["car_year"],
                                      sentiment=analyze_review_sentiments(review_doc["review"]))
            results.append(review_obj)
    return results


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(dealerreview):
    entities = dict()
    entities["sentiment"] = True
    entities["emotion"] = True
    #entities["limit"] = 2
    keywords = dict()
    keywords["sentiment"] = True
    keywords["emotion"] = True
    #keywords["limit"] = 2
    features = dict()
    features["entities"] = entities
    features["keywords"] = keywords
    params = dict()
    #params["text"] = dealerreview
    #params["language"] = "en"
    #params["version"] = "2022-04-07"
    #params["features"] = features
    #params["return_analyzed_text"] = ""
    api_key = "90RBelHoIIKpHL3qNidCEO0iHgccq6qtWC3sI_GFwY2T"
    url1 = "https://api.eu-de.natural-language-understanding.watson.cloud.ibm.com/instances/af82deaf-b6a4-4d5a-a6c7-617760c2f5b5/v1/analyze?version=2022-04-07"
    url2 = "&language=en"
    url3 = "&text="
    url4 = "&features=keywords,entities&entities.emotion=true&entities.sentiment=true&keywords.emotion=true&keywords.sentiment=true"
    url = url1 + url2 + url3 + dealerreview + url4
    try:
        response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
                                    auth=HTTPBasicAuth('apikey', api_key))
    except:
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data['keywords'][0]['sentiment']['label'] if json_data['keywords'] else "neutral"


