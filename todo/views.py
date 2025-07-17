from django.shortcuts import render, redirect, get_object_or_404 
from django.http import Http404
from django.utils.timezone import make_aware
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from todo.models import Task, Comment

# Create your views here.
def index(request):
    if request.method == 'POST':
        priority = int(request.POST.get('priority', 3))
        task= Task(title=request.POST['title'], 
                   due_at=make_aware(parse_datetime(request.POST['due_at'])),
                   priority=priority
        )            
        task.save()

    order_by = request.GET.get('order')
    if request.GET.get('order') == 'due':
        tasks = Task.objects.order_by('due_at')
    elif order_by == 'priority':
        tasks = Task.objects.order_by('priority')
    else:
        tasks = Task.objects.order_by('-posted_at')

    context = {
    'tasks': tasks
    }
    return render(request, 'todo/index.html', context)

def detail(request, task_id):
    task = get_object_or_404(Task, pk=task_id) # (1) タスクの取得

    comment_error = None 

    if request.method == 'POST': # (2) POSTリクエストかどうかのチェック
        comment_text = request.POST.get('comment_text') # (3) コメントテキストの取得

        if comment_text: # (4) コメントが空でないかのバリデーション
            comment = Comment(task=task, text=comment_text) # (5) Commentオブジェクトの作成
            comment.save() # (6) データベースへの保存
            return redirect('detail', task_id=task.id) # (7) リダイレクト
        else:
            comment_error = "コメントを入力してください。" 

    comments = task.comments.all().order_by('posted_at')
    context = {
        'task': task,
        'comments': comments,
        'comment_error': comment_error,
    }
    return render(request, 'todo/detail.html', context)

def update(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    if request.method == 'POST':
        task.title = request.POST['title']
        task.due_at = make_aware(parse_datetime(request.POST['due_at']))

        task.priority = int(request.POST.get('priority', 3))

        task.edit_at = timezone.now()

        task.save()
        return redirect(detail, task_id)

    context = {
        'task': task
    }
    return render(request, 'todo/edit.html', context)

def delete(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    task.delete()
    return redirect(index)

def log(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    context = {
        'task': task,
    }
    return render(request, 'todo/detail.html', context)

def close(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    task.completed = True
    task.save()
    return redirect(index)