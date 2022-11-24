from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from .models import CarModel
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import uuid
import json
from .restapis import get_dealers_from_cf,get_dealer_reviews_from_cf,post_request

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
   return render(request, 'djangoapp/about.html')


# Create a `contact` view to return a static contact page
def contact(request):
    return render(request, 'djangoapp/contact.html')

def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/login.html', context)
    else:
        return render(request, 'djangoapp/login.html', context)


def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

def login_page(request):
    return render(request, 'djangoapp/login.html')

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        # Get dealers from the URL
        dealerships = get_dealership()
        # Concat all dealer's short name
        context = {
            'dealership_list' : dealerships
        }
        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', context)

def get_dealership():
    url = "https://eu-de.functions.appdomain.cloud/api/v1/web/07df66ba-d92d-4404-ac1d-29d3df41fb8d/default/get-all-dealerships.json"
    dealerships = get_dealers_from_cf(url)
    return dealerships
# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        url = "https://eu-de.functions.appdomain.cloud/api/v1/web/07df66ba-d92d-4404-ac1d-29d3df41fb8d/default/get-all-reviews-by-dealership.json"
        # Get dealers from the URL
        dealership_details = get_dealer_reviews_from_cf(url,dealerId=dealer_id)
        # Concat all dealer's short name
        dealerships = get_dealership()
        dealerships = filter(lambda e: e.id == dealer_id, dealerships)
        context = {
            'dealer_name':list(dealerships)[0].full_name,
            'dealerid':dealer_id,
            'dealership_details':dealership_details
        }
        # Return a list of dealer short name
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...
def add_review(request, dealer_id):
    if request.method == "POST":
        if request.user.is_authenticated:
            review = dict()
            review["name"] = request.user.username
            review["dealership"] = dealer_id
            review["review"] = request.POST["content"]
            review["purchase"] = True if request.POST["purchasecheck"] == "on" else False
            review["purchase_date"] = request.POST["purchasedate"]
            car_model = CarModel.objects.get(pk=request.POST["car"])
            review["car_make"] = car_model.car_make.name
            review["car_model"] = car_model.name
            review["car_year"] = car_model.year.year
            json_payload = dict()
            json_payload["id"] = str(uuid.uuid4())
            json_payload["review"] = review
            url = "https://eu-de.functions.appdomain.cloud/api/v1/web/07df66ba-d92d-4404-ac1d-29d3df41fb8d/default/post-review-by-dealership.json"
            response = post_request(url, json_payload, id=dealer_id)
            return HttpResponseRedirect(reverse(viewname='djangoapp:dealer_details', args=(dealer_id,)))
        else:
            return HttpResponse()
    elif request.method == "GET":
        car_models = CarModel.objects.all()
        dealerships = get_dealership()
        dealerships = filter(lambda e: e.id == dealer_id, dealerships)
        context = {
            'dealer_name':list(dealerships)[0].full_name,
            'cars':car_models
        }
        return render(request, 'djangoapp/add_review.html', context)