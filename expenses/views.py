from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import Category, Expense
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
import json
from django.http import JsonResponse,HttpResponse
from userpreferences.models import UserPreference
import datetime
import csv

# Create your views here.
def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(
            name__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            date__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            description__icontains=search_str, owner=request.user) | Expense.objects.filter(
            category__icontains=search_str, owner=request.user)
        data = expenses.values()
        return JsonResponse(list(data), safe=False)


# index
@login_required(login_url='/authentication/login')
def index(request):
    categories = Category.objects.all()
    expenses=Expense.objects.all()
    # expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    currency = UserPreference.objects.get(user=request.user).currency
    context = {
        'expenses': expenses,
        'page_obj': page_obj,
        'currency': currency
    }
    return render(request,'expenses/index.html', context)




# add expense
@login_required(login_url='/authentication/login')
def add_expense(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'expenses/add_expense.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/add_expense.html', context)
        name = request.POST['name']
        receipt_no = request.POST['receipt_no']
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        if not name:
            messages.error(request, 'Name is required')
            return render(request, 'expenses/add_expense.html', context)

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'expenses/add_expense.html', context)

        Expense.objects.create(owner=request.user, amount=amount, date=date,name=name,receipt_no=receipt_no,
                               category=category, description=description)
        messages.success(request, 'Expense saved successfully')
        return redirect('expenses')

    # return render(request,'expenses/add_expense.html')

# edit expenses
def expense_edit(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()
    context = {
        'expense': expense,
        'values': expense,
        'categories': categories
    }
    if request.method == 'GET':
        return render(request, 'expenses/edit-expense.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/edit-expense.html', context)
        name = request.POST['name']
        receipt_no = request.POST['receipt_no']
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        if not name:
            messages.error(request, 'Name is required')
            return render(request, 'expenses/edit_expense.html', context)

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'expenses/edit-expense.html', context)

        expense.owner = request.user
        expense.name = name
        expense.receipt_no = receipt_no
        expense.amount = amount
        expense. date = date
        expense.category = category
        expense.description = description

        expense.save()
        messages.success(request, 'Expense updated  successfully')

        return redirect('expenses')


# delete expense
def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Expense removed')
    return redirect('expenses')

# expenses summary
def expense_category_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date-datetime.timedelta(days=30*6)
    expenses = Expense.objects.filter(date__gte=six_months_ago, date__lte=todays_date)
    finalrep = {}

    def get_category(expense):
        return expense.category
    category_list = list(set(map(get_category, expenses)))

    def get_expense_category_amount(category):
        amount = 0
        filtered_by_category = expenses.filter(category=category)

        for item in filtered_by_category:
            amount += item.amount
        return amount

    for x in expenses:
        for y in category_list:
            finalrep[y] = get_expense_category_amount(y)

    return JsonResponse({'expense_category_data': finalrep}, safe=False)

def stats_view(request):
    return render(request, 'expenses/stats.html')

def export(request):
    return render(request,'expenses/export.html')


def export_csv(request):
    response=HttpResponse(content_type='text/csv')
    response['Content-Disposition']='attachment; filename=Expenses'+str(datetime.datetime.now())+'.csv'

    writer=csv.writer(response)
    writer.writerow(['Name','Amount','Receipt_no','Description','Category','Owner','Date'])

    expenses= Expense.objects.all()

    for expense in expenses:
        writer.writerow([expense.name,expense.amount,expense.receipt_no,expense.description,expense.category,expense.owner,expense.date])
    return response

def export_pdf(request):
    response=HttpResponse(content_type='application/pdf')
    response['Content-Disposition']='attachment; filename=Expenses'+str(datetime.datetime.now())+'.pdf'