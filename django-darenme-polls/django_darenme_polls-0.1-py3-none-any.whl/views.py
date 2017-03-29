from django.http import HttpResponse
from django.template import loader

from django.shortcuts import render, get_object_or_404
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import Question, Choice

'''这是前几步用到的代码
def index(request):
    # 这一步执行数据库查询
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {
        'latest_question_list': latest_question_list,
    }
    # 这一步为什么还要在新建一个polls文件夹呢?
    # By convention DjangoTemplates looks for a “templates” subdirectory in each of the INSTALLED_APPS.
    return render(request, 'polls/index.html', context)

def detail(request, question_id):
    q = get_object_or_404(Question, pk = question_id)
    return render(request, 'polls/detail.html', {'question': q})

def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/result.html', {'question': question})
'''
# 接下来使用generic view


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

# 这里的question_id是在url模块正则表达式里的?P<question_id>中定义的


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
    # Always return an HttpResponseRedirect after successfully dealing
    # with POST data. This prevents data from being posted twice if a
    # user hits the Back button.
    # 还是看不懂这里的question_id? 这么理解:我们当前提交的url都不是层层递进的
    # 而都是相对于127.0.0.1:8000/polls/这个总地址而言的
    # 其实reverse这个函数所做的就是把正则表达式当做格式化字符串然后往里面填东西
    return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
