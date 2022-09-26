import requests
import json
# import related models here
from .models import CarDealer,DealerReview
from requests.auth import HTTPBasicAuth
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # no authentication GET
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    print(kwargs)
    print(json_payload)
    print("POST to {} ".format(url))
    try:
        response = requests.post(url, params=kwargs, json=json_payload)
    except:
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    print(json_data)
    return json_data

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
        dealers = json_result["entries"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            #dealer_doc = dealer["doc"]
            dealer_doc = dealer
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_reviews_from_cf(url, dealerId):
    list = []
    # Call get_request with a URL parameter
    url = url + "?dealerId=" + str(dealerId)
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        results = json_result["entries"]
        # For each dealer object
        for result in results:
            # Get its content in `doc` object
            #dealer_doc = dealer["doc"]
            doc = result
            # Create a CarDealer object with values in `doc` object
            review_obj = DealerReview(car_make = doc["car_make"], car_model = doc["car_model"], car_year = doc["car_year"], dealership = doc["dealership"], id = doc["id"], name = doc["name"], purchase = doc["purchase"], purchase_date = doc["purchase_date"], review = doc["review"])
            review_obj.sentiment = analyze_review_sentiments(review_obj.review)
            list.append(review_obj)
    return list


# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_by_id_from_cf(url, dealerId):
    results = []
    # Call get_request with a URL parameter
    url = url + "?dealerId=" + dealerId
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["entries"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            #dealer_doc = dealer["doc"]
            dealer_doc = dealer
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results[0]

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
    print(text)
    authenticator = IAMAuthenticator(apikey="468RE-JuSO2AH_IYzFUOzuou1C7cr1FQQWkrcYM5j8vo")
    version = "2022-04-07"
    nlu = NaturalLanguageUnderstandingV1(version=version, authenticator=authenticator)
    print("NLU instance created")
    nlu.set_service_url("https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/3e51e9f8-1bc0-4acd-ad44-a326453c18f9")
    nlu.set_disable_ssl_verification(True)
    # print("Disabled")
    try:
        response = nlu.analyze(
            text=text,
            features=Features(sentiment=SentimentOptions(targets=[text]))
        ).get_result()
        label =  json.dumps(response, indent=2)
        print(label)
        label = response['sentiment']['document']['label']
    except:
        label = "neutral"
    print(label)
    return label
