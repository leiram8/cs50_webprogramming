from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Bid, Comment, Listing, ListingForm, Watchlist


def index(request):
    listings = Listing.objects.filter(winner=None)

    # get highest bid
    highest = {}
    for listing in listings:
        bids = listing.bidings.all()

        if not bids:
            highest[listing.id] = listing.starting_bid
        else:
            highest[listing.id] = bids.order_by("-bid").first().bid
    
    return render(request, "auctions/index.html", {
        "listings": listings,
        "highest": highest
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def add_listing(request):
    if request.method == "POST":

        # create new listing
        title = request.POST["title"]
        description = request.POST["description"]
        starting_bid = request.POST["starting_bid"]
        image = request.POST["image"]
        if not image:
            image = "https://st4.depositphotos.com/17828278/24401/v/600/depositphotos_244011872-stock-illustration-image-vector-symbol-missing-available.jpg"
        category = request.POST["category"]
        owner = request.user
        listing = Listing(title=title, description=description, starting_bid=starting_bid, image=image, category=category, owner=owner, winner=None)
        listing.save()
        return HttpResponseRedirect(reverse("index"))
    
    else:
        return render(request, "auctions/add_listing.html", {
            "form": ListingForm()
        })


def listing(request, listing_id):
    user = request.user

    try:
        listing = Listing.objects.get(pk=listing_id)
    except Listing.DoesNotExist:
        raise Http404("Listing does not exist")

    bids = listing.bidings.all()
    comments = listing.comments.all()

    if not bids:
        highest = listing.starting_bid
    else:
        highest = bids.order_by("-bid")[0].bid

    try:
        watchlist = Watchlist.objects.get(user=user)
        watchlist = watchlist.listing.all()
    except:
        watchlist = []
    
    if request.method == "POST":
        if "amount" in request.POST:
            amount = int(request.POST["amount"])

            # check amount is the highest
            if amount <= highest:
                return render(request, "auctions/listing.html", {
                    "user": user,
                    "listing": listing,
                    "comments": comments,
                    "watchlist": watchlist,
                    "message": "That amount is not enough",
                    "highest": highest
                })
            else:
                # create new bid
                bid = Bid(listing=listing, user=user, bid=amount)
                bid.save()
                highest = bid.bid
                return render(request, "auctions/listing.html", {
                    "user": user,
                    "listing": listing,
                    "comments": comments,
                    "watchlist": watchlist,
                    "message": "Bid accepted",
                    "highest": highest
                })

        elif "text" in request.POST:

            # create new comment
            text = request.POST["text"]
            comment = Comment(text=text, user=user, listing=listing)
            comment.save()
            comments = listing.comments.all()

            return render(request, "auctions/listing.html", {
                    "user": user,
                    "listing": listing,
                    "comments": comments,
                    "watchlist": watchlist,
                    "highest": highest
                })
        
        elif "Close" in request.POST:

            # Close auction
            listing.winner = bids.order_by("-bid")[0].user
            listing.save()

            return render(request, "auctions/listing.html", {
            "user": user,
            "listing": listing,
            "comments": comments,
            "watchlist": watchlist,
            "highest": highest
        })

    else:

        return render(request, "auctions/listing.html", {
            "user": user,
            "listing": listing,
            "comments": comments,
            "watchlist": watchlist,
            "highest": highest
        })

@login_required
def add(request, listing_id):
    user = request.user
    listing = Listing.objects.get(pk=listing_id)

    if request.method == "POST":

        # add to watchlist
        if "Add" in request.POST:
            try:
                watchlist = Watchlist.objects.get(user=user)
                watchlist.listing.add(listing)
            except:
                watchlist = Watchlist(user=user)
                watchlist.save()
                watchlist.listing.add(listing)

        # remove from watchlist
        elif "Remove" in request.POST:
            watchlist = Watchlist.objects.get(user=user)
            watchlist.listing.remove(listing)

        return HttpResponseRedirect(reverse("watchlist"))

@login_required
def watchlist(request):
    user = request.user

    # get listings in watchlist 
    try:
        watchlist = Watchlist.objects.get(user=user)
        watchlist = watchlist.listing.all()
    except:
        watchlist = None
    return render(request, "auctions/watchlist.html", {
            "watchlist": watchlist
        })

def categories(request):

    # get all categories
    categories = [ i[1] for i in Listing.CATEGORY_CHOICES ]
    return render(request, "auctions/categories.html", {
        "categories": categories
    })

def category(request, category):
    categories = [ i[1] for i in Listing.CATEGORY_CHOICES ]
    ct = getattr(Listing, category.upper())

    # get all listings for a category
    if category not in categories:
        raise Http404("Category does not exist")
    else:
        listings = Listing.objects.filter(category=ct, winner=None)
        return render(request, "auctions/category.html", {
            "category": category,
            "listings": listings
        })