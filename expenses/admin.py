from django.contrib import admin
from .models import Expense, Category
# Register your models here.

class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('name','amount','receipt_no','description', 'owner', 'category', 'date',)
    search_fields = ('name','description', 'category','date',)

    list_per_page = 5


admin.site.register(Expense, ExpenseAdmin)
admin.site.register(Category)
