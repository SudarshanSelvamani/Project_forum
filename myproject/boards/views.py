from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import UpdateView, ListView
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import View
from .forms import NewTopicForm, PostForm
from .models import Board, Post, Topic
from django.urls import reverse


class BoardListView(ListView):
    model = Board
    context_object_name = 'boards'
    template_name = 'home.html'


class TopicListView(ListView):
    model = Topic
    context_object_name = 'topics'
    template_name = 'topics.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        kwargs['board'] = self.board
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.board = get_object_or_404(Board, pk=self.kwargs.get('pk'))
        queryset = self.board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
        return queryset 


class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'topic_posts.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        session_key = 'viewed_topic_{}'.format(self.topic.pk)
        if not self.request.session.get(session_key, False):
            self.topic.views += 1
            self.topic.save()
            self.request.session[session_key] = True    
        kwargs['topic'] = self.topic
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.topic = get_object_or_404(Topic, board__pk=self.kwargs.get('pk'), pk=self.kwargs.get('topic_pk'))
        queryset = self.topic.posts.order_by('created_at')
        return queryset


@login_required
def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)
    form = NewTopicForm(request.POST or None)
    if form.is_valid():
        topic = topic_and_first_post_save(request,form,board)
        return redirect('topic_posts', pk=pk, topic_pk=topic.pk)
    return render(request, 'new_topic.html', {'board': board, 'form': form})

def topic_and_first_post_save(request, form, board):
        topic = form.save(commit=False)
        topic.board = board
        topic.starter = request.user
        topic.save()
        Post.objects.create(
            message=form.cleaned_data.get('message'),
            topic=topic,
            created_by=request.user
        )
        return topic


@login_required
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    form = PostForm(request.POST or None)
    data_for_reply_save_dict = {'form':form, 'user':request.user, 
                                'topic':topic}
    if form.is_valid():
        post = reply_form_save(data_for_reply_save_dict)
        topic_post_url = generate_paginated_url_for_posts(topic,post)
        return redirect(topic_post_url)
    return render(request, 'reply_topic.html', {'topic': topic, 'form': form})


def generate_paginated_url_for_posts(topic, post):
    board_pk = topic.board.pk
    topic_url = reverse('topic_posts', kwargs={'pk': board_pk, 'topic_pk': topic.pk})
    topic_post_url = '{url}?page={page}#{id}'.format(url=topic_url, id=post.pk,
                                                    page=topic.get_page_count()
                                                    )
    return topic_post_url

def reply_form_save(data_for_reply_save_dict):
    form = data_for_reply_save_dict['form']
    user = data_for_reply_save_dict['user']
    topic = data_for_reply_save_dict['topic']
    post = form.save(commit=False)
    post.topic = topic
    post.created_by = user
    post.save()
    update_topic_last_updated(topic)
    return post
    
def update_topic_last_updated(topic):
    topic.last_updated = timezone.now()
    topic.save()



@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ('message', )
    template_name = 'edit_post.html'
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)


class NewPostView(View):
    def post(self, request):
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('post_list')
        return render(request, 'new_post.html', {'form': form})

    def get(self, request):
        form = PostForm()
        return render(request, 'new_post.html', {'form': form})

    def get(self, request):
        self.form = PostForm()
        return self.render(request)