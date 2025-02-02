from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .restapis import get_dealers_from_cf, get_dealer_reviews_by_id_from_cf, post_request, get_car_models_and_makes_for_dealer, get_dealer_by_id_from_cf
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
# def about(request):
# ...
def about(request):
    context = {}
    return render(request, 'djangoapp/about.html', context)

# Create a `contact` view to return a static contact page
#def contact(request):
def contact(request):
    context = {}
    return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
# def login_request(request):
# ...
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
            return render(request, 'djangoapp/user_login_bootstrap.html', context)
    else:
        return render(request, 'djangoapp/user_login_bootstrap.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
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

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        context = dict()
        url = "https://82521961.us-south.apigw.appdomain.cloud/api/dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        context["dealerships"] = dealerships
        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', context)

# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context = dict()
    if request.method == "GET":
        url = "https://82521961.us-south.apigw.appdomain.cloud/api/reviews"
        # Get dealers from the URL
        reviews = get_dealer_reviews_by_id_from_cf(url,dealerId=dealer_id)
        context["review_list"] = reviews        
        context["dealer_id"] = dealer_id
        
        # Return a list of dealer short name
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    context = {}
    car_models = get_car_models_and_makes_for_dealer(dealer_id)
    if request.method == 'GET':
        url = "https://82521961.us-south.apigw.appdomain.cloud/api/get-dealership"
        # Get dealers from the URL
        dealers = get_dealer_by_id_from_cf(url,dealerId=dealer_id)
        context["dealer_name"] = dealers[0].full_name
        context["dealer_id"] = dealer_id
        context["car_models"] = car_models
        return render(request, 'djangoapp/add_review.html', context)

    if request.method == "POST":
        review = dict()        
        review["dealership"] = dealer_id        
        review["name"] = request.user.username
        review["purchase"] = request.POST.get('purchasecheck', 'false')
        review["review"] = request.POST.get('review', '')
        review["purchase_date"] = request.POST.get('purchase_date', '')

        if(review["purchase"] == "on"):
            review["purchase"] = "true"
        else:
            review["purchase"] = "false"

        car_id = request.POST.get("car", 1)
        for car in car_models:
            if(car.id == int(car_id)):
                review["car_make"] = car.make.name
                review["car_model"] = car.name
                review["car_year"] = car.year.year

        review["id"] = 1
        
        json_payload = dict()
        json_payload["doc"] = review
        url = "https://82521961.us-south.apigw.appdomain.cloud/api/add-review"
        post_request(url, json_payload)
        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)

