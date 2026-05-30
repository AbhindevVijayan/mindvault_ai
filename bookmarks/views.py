from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from .forms import BookmarkForm, LoginForm
from .search_forms import SearchForm
from .models import Bookmark


def index(request):
    return render(request, 'index.html')


@require_http_methods(["POST"])
def login_user(request):
    email = request.POST.get('loginEmail')
    password = request.POST.get('loginPass')
    
    try:
        user = User.objects.get(email=email)
        user = authenticate(request, username=user.username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return redirect('index')
    except User.DoesNotExist:
        return redirect('index')


def signup(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')

        if not username or not email or not password1:
            return render(request, 'index.html', {'error': 'Please fill all fields'})
        
        if len(password1) < 8:
            return render(request, 'index.html', {'error': 'Password must be at least 8 characters'})
        
        if User.objects.filter(username=username).exists():
            return render(request, 'index.html', {'error': 'Username already exists'})
        
        if User.objects.filter(email=email).exists():
            return render(request, 'index.html', {'error': 'Email already registered'})
        
        user = User.objects.create_user(username=username, email=email, password=password1)
        user = authenticate(request, username=username, password=password1)
        if user:
            login(request, user)
            return redirect('dashboard')
        
        return redirect('index')

    return render(request, 'index.html')


@login_required
def add_bookmark(request):
    # Import here to avoid import errors when not needed
    from .utils import (
        extract_article,
        generate_summary,
        generate_embedding,
    )

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

@require_http_methods(["POST"])
def summarize(request):
    from .utils import (
        extract_article,
        generate_summary,
        generate_embedding,
    )

    form = BookmarkForm(request.POST)
    context = {}

    if form.is_valid():
        url = form.cleaned_data['url']
        try:
            data = extract_article(url)
            summary = generate_summary(data['content'])

            if request.user.is_authenticated:
                embedding = generate_embedding(data['content'][:1000])
                Bookmark.objects.create(
                    user=request.user,
                    title=data['title'],
                    url=url,
                    content=data['content'],
                    summary=summary,
                    embedding=embedding
                )
                context['saved_message'] = 'Saved to your library.'

            context.update({
                'summary_result': summary,
                'source_title': data['title'],
                'summary_url': url,
            })
        except Exception:
            context['summary_error'] = 'Could not summarize that URL. Please check the link and try again.'
    else:
        context['summary_error'] = 'Enter a valid URL before summarizing.'

    return render(request, 'index.html', context)


def semantic_search(request):
    # Import here to avoid import errors when not needed
    from .utils import (
        generate_embedding,
        cosine_similarity
    )

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
    