from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def email_list_view(request):
    return render(request, 'emails/list.html')

@login_required
def add_email_view(request):
    return render(request, 'emails/add.html')

@login_required
def delete_email_view(request, pk):
    return render(request, 'emails/delete.html')