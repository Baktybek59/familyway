from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.db.models import Count
from .models import BlogPost, BlogComment, BlogLike, BlogDislike
from .forms import BlogCommentForm


class BlogListView(ListView):
    model = BlogPost
    template_name = 'blog/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = BlogPost.objects.filter(is_published=True)
        
        # Filter by category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Filter by language
        language = self.request.GET.get('language')
        if language:
            queryset = queryset.filter(language=language)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = BlogPost.CATEGORY_CHOICES
        context['languages'] = BlogPost.LANGUAGE_CHOICES
        context['current_category'] = self.request.GET.get('category')
        context['current_language'] = self.request.GET.get('language')
        return context


class BlogDetailView(DetailView):
    model = BlogPost
    template_name = 'blog/blog_detail.html'
    context_object_name = 'post'
    
    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        
        # Увеличиваем счетчик просмотров
        post.views += 1
        post.save(update_fields=['views'])
        
        # Получаем комментарии
        context['comments'] = post.comments.filter(is_approved=True).order_by('-created_at')
        context['comment_form'] = BlogCommentForm()
        context['likes_count'] = post.get_likes_count()
        context['dislikes_count'] = post.get_dislikes_count()
        context['is_liked'] = post.is_liked_by(self.request.user) if self.request.user.is_authenticated else False
        context['is_disliked'] = post.is_disliked_by(self.request.user) if self.request.user.is_authenticated else False
        
        return context
    
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, _('Для добавления комментария необходимо войти в систему.'))
            return redirect('accounts:login')
        
        post = self.get_object()
        form = BlogCommentForm(request.POST)
        
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, _('Комментарий добавлен!'))
            return redirect('blog:post_detail', pk=post.pk)
        
        # Если форма невалидна, показываем ошибки
        context = self.get_context_data()
        context['comment_form'] = form
        return render(request, self.template_name, context)


@login_required
def like_post(request, pk):
    """Лайк/анлайк статьи"""
    post = get_object_or_404(BlogPost, pk=pk, is_published=True)
    
    # Удаляем дизлайк, если он есть
    BlogDislike.objects.filter(post=post, user=request.user).delete()
    
    like, created = BlogLike.objects.get_or_create(
        post=post,
        user=request.user
    )
    
    if not created:
        # Если лайк уже существует, удаляем его
        like.delete()
        liked = False
    else:
        liked = True
    
    likes_count = post.get_likes_count()
    dislikes_count = post.get_dislikes_count()
    
    return JsonResponse({
        'liked': liked,
        'disliked': False,
        'likes_count': likes_count,
        'dislikes_count': dislikes_count
    })


@login_required
def dislike_post(request, pk):
    """Дизлайк/андизлайк статьи"""
    post = get_object_or_404(BlogPost, pk=pk, is_published=True)
    
    # Удаляем лайк, если он есть
    BlogLike.objects.filter(post=post, user=request.user).delete()
    
    dislike, created = BlogDislike.objects.get_or_create(
        post=post,
        user=request.user
    )
    
    if not created:
        # Если дизлайк уже существует, удаляем его
        dislike.delete()
        disliked = False
    else:
        disliked = True
    
    likes_count = post.get_likes_count()
    dislikes_count = post.get_dislikes_count()
    
    return JsonResponse({
        'liked': False,
        'disliked': disliked,
        'likes_count': likes_count,
        'dislikes_count': dislikes_count
    })


@login_required
def delete_comment(request, pk):
    """Удаление комментария"""
    comment = get_object_or_404(BlogComment, pk=pk)
    
    # Проверяем, что пользователь является автором комментария
    if comment.author != request.user:
        return JsonResponse({'error': 'У вас нет прав для удаления этого комментария'}, status=403)
    
    comment.delete()
    return JsonResponse({'success': True})
