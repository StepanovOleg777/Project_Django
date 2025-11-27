from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import BlogPost


class BlogPostListView(ListView):
    """CBV для списка блоговых записей"""
    model = BlogPost
    template_name = 'blog/blogpost_list.html'

    def get_queryset(self):
        """Показываем только опубликованные статьи"""
        return BlogPost.objects.filter(is_published=True)


class BlogPostDetailView(DetailView):
    """CBV для детального просмотра блоговой записи"""
    model = BlogPost
    template_name = 'blog/blogpost_detail.html'

    def get_object(self, queryset=None):
        """Увеличиваем счетчик просмотров при каждом просмотре статьи"""
        obj = super().get_object(queryset)
        obj.views_count += 1
        obj.save()
        return obj


class BlogPostCreateView(CreateView):
    """CBV для создания блоговой записи"""
    model = BlogPost
    template_name = 'blog/blogpost_form.html'
    fields = ['title', 'content', 'preview', 'is_published']
    success_url = reverse_lazy('blog:blogpost_list')


class BlogPostUpdateView(UpdateView):
    """CBV для редактирования блоговой записи"""
    model = BlogPost
    template_name = 'blog/blogpost_form.html'
    fields = ['title', 'content', 'preview', 'is_published']

    def get_success_url(self):
        """Перенаправляем на страницу отредактированной статьи"""
        return reverse_lazy('blog:blogpost_detail', kwargs={'pk': self.object.pk})


class BlogPostDeleteView(DeleteView):
    """CBV для удаления блоговой записи"""
    model = BlogPost
    template_name = 'blog/blogpost_confirm_delete.html'
    success_url = reverse_lazy('blog:blogpost_list')