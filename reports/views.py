from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def reports_list_view(request):
    return render(request, 'reports/list.html')

@login_required
def create_report_view(request):
    return render(request, 'reports/create.html')

@login_required
def report_detail_view(request, pk):
    return render(request, 'reports/detail.html')

@login_required
def resend_report_view(request, pk):
    return render(request, 'reports/resend.html')