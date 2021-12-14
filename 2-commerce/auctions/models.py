from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import ModelForm


class User(AbstractUser):
    pass

class Listing(models.Model):
    TOY = "TY"
    FASHION = "FS"
    ELECTRONICS = "ET"
    HOME = "HM"
    TOOLS = "TL"
    ART = "AR"
    SPORTS = "SP"
    CATEGORY_CHOICES = [
        (TOY, "Toy"),
        (FASHION, "Fashion"),
        (ELECTRONICS, "Electronics"),
        (HOME, "Home"),
        (TOOLS, "Tools"),
        (ART, "Art"),
        (SPORTS, "Sports")
    ]
    title = models.CharField(max_length=20)
    description = models.TextField(max_length=1000)
    starting_bid = models.PositiveIntegerField()
    image = models.URLField(blank=True)
    category = models.CharField(
        max_length=2,
        choices=CATEGORY_CHOICES, 
        blank=True
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner")
    winner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="winner")
    
    def __str__(self):
        return self.title

class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bidings")
    bid = models.PositiveIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Comment(models.Model):
    text = models.TextField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ManyToManyField(Listing, blank=True, related_name="watchlist")


class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ["title", "description", "starting_bid", "image", "category"]

