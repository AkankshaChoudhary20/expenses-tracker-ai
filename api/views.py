from datetime import date, timedelta

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import ExpenseSerializer
from .models import Expense, CATEGORY_CHOICES
from . import ai


@api_view(['GET'])
def getRoutes(request):
    routes = [
        {'Endpoint': '/expenses/', 'method': 'GET', 'description': 'Returns an array of expenses'},
        {'Endpoint': '/expenses/id/', 'method': 'GET', 'description': 'Returns a single expense object'},
        {'Endpoint': '/expenses/create/', 'method': 'POST', 'body': {'amount': 0, 'description': '', 'category': '', 'date': 'YYYY-MM-DD'}, 'description': 'Creates a new expense'},
        {'Endpoint': '/expenses/quick-add/', 'method': 'POST', 'body': {'text': ''}, 'description': 'AI: parses free-form text into a structured expense and creates it'},
        {'Endpoint': '/expenses/id/update/', 'method': 'PUT', 'description': 'Updates an existing expense'},
        {'Endpoint': '/expenses/id/delete/', 'method': 'DELETE', 'description': 'Deletes an expense'},
        {'Endpoint': '/expenses/id/categorize/', 'method': 'POST', 'description': 'AI: (re)assigns a category based on the description'},
        {'Endpoint': '/expenses/ask/', 'method': 'POST', 'body': {'question': ''}, 'description': 'AI: natural-language Q&A over your expense history'},
        {'Endpoint': '/expenses/insights/', 'method': 'GET', 'params': {'period': 'week|month|all (default month)'}, 'description': 'AI: plain-English spending summary'},
        {'Endpoint': '/expenses/categories/', 'method': 'GET', 'description': 'Returns the fixed list of expense categories'},
    ]
    return Response(routes)


@api_view(['GET'])
def getCategories(request):
    return Response(CATEGORY_CHOICES)


@api_view(['GET'])
def getExpenses(request):
    expenses = Expense.objects.all()
    category = request.GET.get('category')
    if category:
        expenses = expenses.filter(category=category)
    serializer = ExpenseSerializer(expenses, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def getExpense(request, pk):
    try:
        expense = Expense.objects.get(id=pk)
    except Expense.DoesNotExist:
        return Response({'error': 'Expense not found'}, status=404)
    serializer = ExpenseSerializer(expense, many=False)
    return Response(serializer.data)


@api_view(['POST'])
def createExpense(request):
    serializer = ExpenseSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['PUT'])
def updateExpense(request, pk):
    try:
        expense = Expense.objects.get(id=pk)
    except Expense.DoesNotExist:
        return Response({'error': 'Expense not found'}, status=404)
    serializer = ExpenseSerializer(instance=expense, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


@api_view(['DELETE'])
def deleteExpense(request, pk):
    try:
        expense = Expense.objects.get(id=pk)
    except Expense.DoesNotExist:
        return Response({'error': 'Expense not found'}, status=404)
    expense.delete()
    return Response('Expense was deleted!')


@api_view(['POST'])
def quickAddExpense(request):
    text = request.data.get('text', '')
    parsed = ai.parse_expense_text(text)
    if parsed is None:
        return Response({'error': 'Quick-add unavailable — check ANTHROPIC_API_KEY, or enter the expense manually'}, status=503)
    serializer = ExpenseSerializer(data={
        'amount': parsed.amount, 'description': parsed.description,
        'category': parsed.category, 'date': parsed.date,
    })
    if not serializer.is_valid():
        return Response(serializer.errors, status=422)
    expense = serializer.save()
    return Response(ExpenseSerializer(expense).data, status=201)


@api_view(['POST'])
def categorizeExpense(request, pk):
    try:
        expense = Expense.objects.get(id=pk)
    except Expense.DoesNotExist:
        return Response({'error': 'Expense not found'}, status=404)
    category = ai.categorize_expense(expense.description)
    if category is None:
        return Response({'error': 'Auto-categorization unavailable'}, status=503)
    expense.category = category
    expense.save()
    return Response(ExpenseSerializer(expense).data)


@api_view(['POST'])
def askExpenses(request):
    question = request.data.get('question', '')
    expenses = list(Expense.objects.all())
    result = ai.ask_expenses(question, expenses)
    if result is None:
        return Response({'error': 'Ask unavailable'}, status=503)
    by_id = {e.id: e for e in expenses}
    cited = [by_id[i] for i in result.cited_expense_ids if i in by_id]
    return Response({
        'answer': result.answer,
        'cited_expenses': ExpenseSerializer(cited, many=True).data,
    })


PERIOD_DAYS = {'week': 7, 'month': 30, 'all': None}


@api_view(['GET'])
def insights(request):
    period = request.GET.get('period', 'month')
    days = PERIOD_DAYS.get(period, 30)
    expenses = Expense.objects.all()
    if days is not None:
        cutoff = date.today() - timedelta(days=days)
        expenses = expenses.filter(date__gte=cutoff)
    expenses = list(expenses)
    summary = ai.generate_insights(expenses, period_label=period)
    if summary is None:
        return Response({'error': 'Insights unavailable — no expenses in range, or AI is not configured'}, status=503)
    total = sum(float(e.amount) for e in expenses)
    return Response({'summary': summary, 'expense_count': len(expenses), 'total': total, 'period': period})
