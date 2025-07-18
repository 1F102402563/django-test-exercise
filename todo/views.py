from django.shortcuts import render, redirect, get_object_or_404 
from django.http import Http404
from django.utils.timezone import make_aware
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from todo.models import Task, Comment, ChecklistItem

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

    # エラーメッセージ用の変数
    comment_error = None 
    checklist_error = None

    if request.method == 'POST': # (2) POSTリクエストかどうかのチェック
        comment_text = request.POST.get('comment_text') # (3) コメントテキストの取得

        if comment_text: # (4) コメントが空でないかのバリデーション
            comment = Comment(task=task, text=comment_text) # (5) Commentオブジェクトの作成
            comment.save() # (6) データベースへの保存
            return redirect('detail', task_id=task.id) # (7) リダイレクト
        else:
            comment_error = "コメントを入力してください。" 

        # 1.チェックリスト項目
        if 'checklist_text' in request.POST:
            checklist_text = request.POST.get('checklist_text')
            if checklist_text:
                checklist_item = ChecklistItem(task=task, text=checklist_text)
                checklist_item.save()
                return redirect('detail', task_id=task.id)
            else:
                checklist_error = "チェックリスト項目を入力してください。"

        # 2.チェック状態変更
        if 'toggle_checklist' in request.POST:
            item_id = request.POST.get('item_id')
            try:
                item = ChecklistItem.objects.get(id=item_id, task=task)
                item.is_checked = not item.is_checked
                item.save()
                return redirect('detail', task_id=task.id)
            except ChecklistItem.DoesNotExist:
                pass

    comments = task.comments.all().order_by('posted_at')
    checklist_items = task.checklist_items.all().order_by('created_at')

    context = {
        'task': task,
        'comments': comments,
        'comment_error': comment_error,
        'checklist_items': checklist_items,
        'checklist_error': checklist_error,
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

        # ★チェックリスト用★
        # 1.削除機能
        delete_item_ids = request.POST.getlist('delete_items')
        if delete_item_ids:
            ChecklistItem.objects.filter(
                id__in=delete_item_ids,     # 削除対象として選択されたIDのリストを処理
                task=task
            ).delete()

        # 2.追加処理
        # 3つのテキストフィールドをチェック・空でないものだけを追加
        for i in range(1, 4): 
            field_name = f'new_item_{i}'    # new_item_1~3
            item_text = request.POST.get(field_name, '').strip()
            
            # 空文字列やスペースのみの入力は無視
            if item_text:
                ChecklistItem.objects.create(
                    task=task,
                    text=item_text  # is_checkedはデフォルトでFalseなので、明示的に指定する必要なし
                )

        return redirect(detail, task_id)

    checklist_items = task.checklist_items.all().order_by('created_at')
    
    context = {
        'task': task,
        'checklist_items': checklist_items,
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