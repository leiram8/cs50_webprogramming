from django.shortcuts import render
from django.http import  HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django import forms
from django.contrib import messages
from random import randrange

from . import markdown2
from . import util


class NewEntryForm(forms.Form):
    title = forms.CharField(label="New Title")


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def wiki(request, entry):
    entries = util.list_entries()
    if entry in entries:
        text = markdown2.markdown_path(f'entries/{entry}.md')
        return render(request, "encyclopedia/wiki.html", {
            "entry": entry,
            "text": text
        })
    return render(request, "encyclopedia/notfound.html")
    
def search(request):
    if request.method == "POST":
        look = request.POST["q"]
        entries = util.list_entries()
        if look in entries:
            return HttpResponseRedirect(reverse(wiki, args=[look]))
        else:
            results = []
            for entry in entries:
                if look in entry:
                    results.append(entry)

            return render(request, "encyclopedia/search.html", {
                "results": results
            })

def new(request):
    if request.method == "POST":
        title = NewEntryForm(request.POST)
        text = request.POST["text"]
        entries = util.list_entries()

        if title.is_valid():
            titleClean = title.cleaned_data["title"]
            if titleClean in entries:
                messages.warning(request, 'That title already exists.')
                return render(request, "encyclopedia/new.html", {
                    "form": title,
                    "text": text
                })
            else:
                util.save_entry(titleClean, text)
                
                return HttpResponseRedirect(reverse(wiki, args=[titleClean]))
        else:
            return render(request, "encyclopedia/new.html", {
                "form": title,
                "text": text
            })
            
    return render(request, "encyclopedia/new.html", {
        "form": NewEntryForm(),
        "text": ''
    })

def edit(request, entry):
    if request.method == "POST":
        newText = request.POST["text"]
        util.save_entry(entry, newText)

        return HttpResponseRedirect(reverse(wiki, args=[entry]))

    if entry in util.list_entries():
        text = util.get_entry(entry)

        return render(request, "encyclopedia/edit.html", {
            "entry": entry,
            "text": text
        })
    else:
        return render(request, "encyclopedia/notfound.html")

def random(request):
    entries = util.list_entries()
    random = entries[randrange(len(entries))]
    return HttpResponseRedirect(reverse(wiki, args=[random]))
