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
from .forms import AdminUserForm, AdminBookmarkForm
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404


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


@staff_member_required
def admin_panel(request):
    from django.utils import timezone
    from datetime import timedelta
    users = User.objects.all().order_by('-date_joined')
    user_stats = []
    for u in users:
        count = Bookmark.objects.filter(user=u).count()
        user_stats.append({'user': u, 'bookmark_count': count})

    # Site-wide metrics
    total_users = User.objects.count()
    total_bookmarks = Bookmark.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    staff_users = User.objects.filter(is_staff=True).count()

    # Last 7 days labels and counts
    labels = []
    signup_counts = []
    bookmark_counts = []
    today = timezone.now().date()
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        labels.append(day.strftime('%Y-%m-%d'))
        sc = User.objects.filter(date_joined__date=day).count()
        bc = Bookmark.objects.filter(created_at__date=day).count()
        signup_counts.append(sc)
        bookmark_counts.append(bc)

    # Top users by bookmark count
    top_users = []
    users_with_counts = []
    for u in User.objects.all():
        users_with_counts.append((Bookmark.objects.filter(user=u).count(), u))
    users_with_counts.sort(reverse=True, key=lambda x: x[0])
    for cnt, u in users_with_counts[:5]:
        top_users.append({'user': u, 'count': cnt})

    context = {
        'user_stats': user_stats,
        'total_users': total_users,
        'total_bookmarks': total_bookmarks,
        'active_users': active_users,
        'staff_users': staff_users,
        'labels': labels,
        'signup_counts': signup_counts,
        'bookmark_counts': bookmark_counts,
        'top_users': top_users,
    }

    return render(request, 'admin_panel.html', context)


@staff_member_required
def admin_users_list(request):
    users = User.objects.all().order_by('-date_joined')
    user_rows = []
    for u in users:
        cnt = Bookmark.objects.filter(user=u).count()
        user_rows.append({'user': u, 'bookmark_count': cnt})
    return render(request, 'admin_users.html', {'users': user_rows})


@staff_member_required
def admin_bookmarks_list(request):
    bookmarks = Bookmark.objects.select_related('user').order_by('-created_at')[:200]
    return render(request, 'admin_bookmarks.html', {'bookmarks': bookmarks})


@staff_member_required
def admin_user_detail(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    bookmarks = Bookmark.objects.filter(user=user).order_by('-created_at')

    if request.method == 'POST':
        if 'update_user' in request.POST:
            form = AdminUserForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                return redirect('admin_user_detail', user_id=user.id)
        elif 'delete_bookmark' in request.POST:
            bid = request.POST.get('delete_bookmark')
            b = get_object_or_404(Bookmark, pk=bid, user=user)
            b.delete()
            return redirect('admin_user_detail', user_id=user.id)
        elif 'edit_bookmark' in request.POST:
            bid = request.POST.get('edit_bookmark')
            b = get_object_or_404(Bookmark, pk=bid, user=user)
            form = AdminBookmarkForm(request.POST, instance=b)
            if form.is_valid():
                form.save()
                return redirect('admin_user_detail', user_id=user.id)

    user_form = AdminUserForm(instance=user)
    bookmark_forms = {b.id: AdminBookmarkForm(instance=b) for b in bookmarks}

    return render(request, 'admin_user.html', {
        'user_obj': user,
        'bookmarks': bookmarks,
        'user_form': user_form,
        'bookmark_forms': bookmark_forms
    })


@staff_member_required
def admin_edit_bookmark(request, bookmark_id):
    b = get_object_or_404(Bookmark, pk=bookmark_id)
    if request.method == 'POST':
        form = AdminBookmarkForm(request.POST, instance=b)
        if form.is_valid():
            form.save()
            return redirect('admin_user_detail', user_id=b.user.id)
    else:
        form = AdminBookmarkForm(instance=b)
    return render(request, 'admin_edit_bookmark.html', {'form': form, 'bookmark': b})


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
    