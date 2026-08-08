from django.urls import path
from .views import *

urlpatterns = [
    path('', getRoutes, name="routes"),
    path('expenses/', getExpenses, name="expenses"),
    # Single-segment literal routes must come before the expenses/<pk>/ catch-all below,
    # or e.g. GET /expenses/ask/ would resolve as getExpense(pk="ask").
    path('expenses/categories/', getCategories, name="categories"),
    path('expenses/ask/', askExpenses, name="ask-expenses"),
    path('expenses/insights/', insights, name="insights"),
    path('expenses/create/', createExpense, name="create-expense"),
    path('expenses/quick-add/', quickAddExpense, name="quick-add-expense"),
    path('expenses/<str:pk>/update/', updateExpense, name="update-expense"),
    path('expenses/<str:pk>/delete/', deleteExpense, name="delete-expense"),
    path('expenses/<str:pk>/categorize/', categorizeExpense, name="categorize-expense"),
    path('expenses/<str:pk>/', getExpense, name="expense"),
]
