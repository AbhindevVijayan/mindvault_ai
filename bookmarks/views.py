from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .forms import BookmarkForm, LoginForm, SignupForm
from .search_forms import SearchForm
from .models import Bookmark
from .utils import chat_response


def index(request):
    return render(request, 'index.html')


@require_http_methods(["POST"])
def login_user(request):
    form = LoginForm(request.POST, request=request)
    if form.is_valid():
        login(request, form.get_user())
        return redirect('dashboard')

    return render(request, 'index.html', {
        'login_error': ' '.join(form.non_field_errors()),
        'login_email': request.POST.get('email', ''),
    })


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            user = authenticate(request, username=user.username, password=form.cleaned_data['password1'])
            if user:
                login(request, user)
                return redirect('dashboard')

        return render(request, 'index.html', {
            'signup_error': ' '.join(form.non_field_errors() or form.errors.get('email') or form.errors.get('password1') or []),
            'signup_email': request.POST.get('email', ''),
        })

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
    if not request.user.is_authenticated:
        return render(request, 'index.html', {'show_signup_modal': True})
    
    from .utils import (
        extract_article,
        generate_summary,
        generate_embedding,
    )

    form = BookmarkForm(request.POST)
    context = {}
    next_page = request.POST.get('next_page')

    if form.is_valid():
        url = form.cleaned_data['url']
        try:
            data = extract_article(url)
            summary = generate_summary(data['content'])

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

    if next_page == 'dashboard':
        bookmarks = Bookmark.objects.filter(user=request.user)
        context['bookmarks'] = bookmarks
        return render(request, 'dashboard.html', context)

    return render(request, 'index.html', context)


def chat(request):
    if request.method != 'POST':
        return JsonResponse({'reply': 'Send your question with a POST request to receive a chat response.'})

    question = request.POST.get('question', '').strip()
    if not question:
        return JsonResponse({'reply': 'Ask me anything and I will answer.'})

    reply = chat_response(question)
    return JsonResponse({'reply': reply})


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
    