from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import DealerReview,CarModel
from .restapis import get_dealers_from_cf,get_dealer_by_id_from_cf, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact_us.html', context)
# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['psw']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            return redirect('djangoapp:index')
        else:
            # If not, return to login page again
            return render(request, 'djangoapp/user_login.html', context)
    else:
        return render(request, 'djangoapp/user_login.html', context)

# ...

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    # Get the user object based on session id in request
    print("Log out the user `{}`".format(request.user.username))
    # Logout user in the request
    logout(request)
    # Redirect user back to course list view
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/user_registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        # Get user information from request.POST
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            # Login the user and redirect to course list page
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/user_registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        #url = "your-cloud-function-domain/dealerships/dealer-get"
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/ee41e38d-d2b2-4e90-8aa7-1057587fde97/dealership-package/get-dealership.json"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        #return HttpResponse(dealer_names)
        return render(request, 'djangoapp/index.html', {'dealership_list':dealerships})

def get_dealer_by_id(request,id):
    if request.method == "GET":
        #url = "your-cloud-function-domain/dealerships/dealer-get"
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/ee41e38d-d2b2-4e90-8aa7-1057587fde97/dealership-package/get-dealership.json"
        # Get dealers from the URL
        dealership = get_dealer_by_id_from_cf(url,id)        
        # Return a list of dealer short name
        return HttpResponse(dealership)

# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
def get_dealer_details(request,dealer_id):
    if request.method == "GET":
        #url = "your-cloud-function-domain/dealerships/dealer-get"
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/ee41e38d-d2b2-4e90-8aa7-1057587fde97/dealership-package/get-review.json"
        # Get dealers from the URL        
        reviews = get_dealer_reviews_from_cf(url,dealer_id)
        #reviews = ' '.join([review.review for review in reviews])
        print(reviews)
        # Return a list of dealer short name
        #return HttpResponse(reviews)
        context = {'dealerId':dealer_id,'reviews':reviews}

        return render(request,'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    if request.user.is_authenticated:        
        if request.method == "POST":
            review = {}
            review["name"] = request.user.first_name + " " + request.user.last_name
            form = request.POST
            review["dealership"] = dealer_id
            review["review"] = form["content"]
            if(form.get("purchasecheck") == "on"):
                review["purchase"] = True
            else:
                review["purchase"] = False
            if(review["purchase"]):
                review["purchase_date"] = datetime.strptime(form.get("purchasedate"), "%m/%d/%Y").isoformat()
                car = CarModel.objects.get(pk=form["car"])
                review["car_make"] = car.carMake.name
                review["car_model"] = car.name
                review["car_year"] = car.year.strftime("%Y") 
            post_url = "https://us-south.functions.appdomain.cloud/api/v1/web/ee41e38d-d2b2-4e90-8aa7-1057587fde97/dealership-package/post-review"
            json_payload = json.dumps({ "review": review })
            post_request(post_url, json_payload, dealer_id=dealer_id)
            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
        if request.method == 'GET':
            context = {}
            cars = CarModel.objects.filter(dealer_id=dealer_id)
            context['cars'] = cars

            url = "https://us-south.functions.appdomain.cloud/api/v1/web/ee41e38d-d2b2-4e90-8aa7-1057587fde97/dealership-package/get-dealership.json"
            # Get dealers from the URL
            dealership = get_dealer_by_id_from_cf(url,dealer_id)
            context['dealer'] = dealership
            return render(request,'djangoapp/add_review.html', context)

    else:
        return redirect("/djangoapp/login")
# ...

