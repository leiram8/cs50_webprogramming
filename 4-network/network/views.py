import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from .models import User, Follow, Post


def index(request):

    if request.user.is_authenticated:

        # Create a post
        if request.method == "POST":
            user = request.user
            text = request.POST["text"]
            post = Post(user=user, text=text)
            post.save()
            
    # Get all posts
    posts = Post.objects.order_by("-date")

    # Create page
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.get_page(page_number)
    except:
        posts = paginator.page(1)

    return render(request, "network/index.html", {
        "posts": posts
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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required
def following(request):

    if request.user.is_authenticated:

        # Get following list
        try:
            follows = Follow.objects.get(user=request.user)
            follows = follows.following.all()
        except:
            return render(request, "network/following.html", {
                "message": "You are not following any user."
            })

        if not follows:
            return render(request, "network/following.html", {
                "message": "You are not following any user."
            })
        
        # Get posts for every user you are following
        posts = Post.objects.none()
        for follow in follows:
            posts = posts | Post.objects.filter(user=follow)
        posts = posts.order_by("-date")

         # Create page
        paginator = Paginator(posts, 10)
        page_number = request.GET.get('page', 1)
        try:
            posts = paginator.get_page(page_number)
        except:
            posts = paginator.page(1)

        return render(request, "network/following.html", {
            "posts": posts
        })
    else:
        return HttpResponseRedirect(reverse("login"))


def profile(request, username):

    if request.user.is_authenticated:
        # Get the posts for the user and paginate
        user = User.objects.get(username=username)
        posts = Post.objects.filter(user=user).order_by("-date")
        paginator = Paginator(posts, 10)

        # Create page
        page_number = request.GET.get('page', 1)
        try:
            posts = paginator.get_page(page_number)
        except:
            posts = paginator.page(1)

        # Toggle follow or unfollow
        if request.method == "POST":
            if 'follow' in request.POST:
                try:
                    follow = Follow.objects.get(user=request.user)
                    follow.following.add(user)
                except:
                    follow = Follow(user=request.user)
                    follow.save()
                    follow.following.add(user)
            elif 'unfollow' in request.POST:
                follow = Follow.objects.get(user=request.user)
                follow.following.remove(user)

        # Find number of followers the user has and is following
        followers = user.followee.all().count()
        
        try:
            following = Follow.objects.get(user=user)
            following = following.following.all().count()
        except:
            following = 0

        # Determine if session user follows the profile
        follows = Follow.objects.filter(user=request.user,following=user).exists()

        return render(request, "network/profile.html", {
            "username": username,
            "posts": posts,
            "followers": followers,
            "following": following,
            "follows": follows
        })
    
    else:
        return HttpResponseRedirect(reverse("login"))


@csrf_exempt
@login_required
def edit(request, post_id):
    
    # Only accept put method
    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)

    # Get post
    try:
        post = Post.objects.get(pk=post_id)
    except:
        return JsonResponse({"error": "Post not found."}, status=404)
    
    if post.user != request.user:
        return JsonResponse({"error": "Not your post."}, status=404)

    data = json.loads(request.body)
    
    # Edit text
    if data.get("text") is not None:
        post.text = data["text"]
        post.save()

    return HttpResponse(status=204)


@csrf_exempt
@login_required
def like(request, post_id):

    # Only accept put method
    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)

    # Get post
    try:
        post = Post.objects.get(pk=post_id)
    except:
        return JsonResponse({"error": "Post not found."}, status=404)

    data = json.loads(request.body)
    
    # Like or unlike
    if data.get("like") is not None:
        if data["like"]:
            post.likes.add(request.user)
        else:
            post.likes.remove(request.user)
        
        post.save()

    return HttpResponse(status=204)