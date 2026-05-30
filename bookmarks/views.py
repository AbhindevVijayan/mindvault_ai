from django.shortcuts import render
from .forms import BookmarkForm
from .search_forms import SearchForm
from .utils import (
    extract_article,
    generate_summary,
    generate_embedding,
    cosine_similarity
)
from .models import Bookmark
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def add_bookmark(request):

    if request.method == "POST":

        form = BookmarkForm(request.POST)

        if form.is_valid():

            url = form.cleaned_data['url']

            data = extract_article(url)

            # AI Summary
            summary = generate_summary(
                data['content']
            )
            embedding = generate_embedding(
                 data['content'][:1000]
             )

            Bookmark.objects.create(
                user=request.user,
                title=data['title'],
                url=url,
                content=data['content'],
                summary=summary,
                embedding=embedding
            )

    else:
        form = BookmarkForm()
    
    return render(
        request,
        'add_bookmark.html',
        {'form': form}
    )

def semantic_search(request):

    results = []

    form = SearchForm(request.GET)

    if form.is_valid():

        query = form.cleaned_data['query']

        query_embedding = generate_embedding(query)

        bookmarks = Bookmark.objects.all()

        scored_results = []

        for bookmark in bookmarks:

            similarity = cosine_similarity(
                query_embedding,
                bookmark.embedding
            )

            scored_results.append(
                (similarity, bookmark)
            )

        scored_results.sort(
            reverse=True,
            key=lambda x: x[0]
        )

        results = scored_results[:5]

    return render(
        request,
        'search.html',
        {
            'form': form,
            'results': results
        }
    )
def signup(request):

    if request.method == 'POST':

        form = UserCreationForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect('/accounts/login/')

    else:

        form = UserCreationForm()

    return render(
        request,
        'signup.html',
        {'form': form}
    )
    

@login_required
def dashboard(request):

    bookmarks = Bookmark.objects.filter(
        user=request.user
    )

    return render(
        request,
        'dashboard.html',
        {'bookmarks': bookmarks}
    )
    
    