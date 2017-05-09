from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .models import Question, Choice
from django.core.urlresolvers import reverse

# Create your views here.

def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    # latest_question_list = get_list_or_404(Question.objects.order_by('-pub_date')[:5])
    return render(request, 'polls/index.html', {'latest_question_list': latest_question_list})

def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/detail.html', {'question': question})

def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {"question": question})

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': '没有选择问题'
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))