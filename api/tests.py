from types import SimpleNamespace
from unittest.mock import patch
from django.test import TestCase
from rest_framework.test import APIClient
from .models import Expense


class ExpenseValidationTests(TestCase):
    def setUp(self): self.client=APIClient()
    def test_manual_create_rejects_unknown_category(self):
        response=self.client.post('/api/expenses/create/',{'amount':'12.00','description':'Lunch','category':'Not a category','date':'2026-10-01'},format='json')
        self.assertEqual(response.status_code,400)
        self.assertFalse(Expense.objects.exists())
    @patch('api.views.ai.parse_expense_text')
    def test_quick_add_validates_ai_output_before_saving(self,parse):
        base={'amount':'12.00','description':'Lunch','category':'Food & Dining','date':'2026-10-01'}
        for invalid in [{'date':'not-a-date'},{'amount':'9999999999999999'},{'description':'x'*401},{'category':'Unknown'}]:
            parse.return_value=SimpleNamespace(**{**base,**invalid})
            response=self.client.post('/api/expenses/quick-add/',{'text':'lunch'},format='json')
            self.assertEqual(response.status_code,422)
            self.assertFalse(Expense.objects.exists())
        parse.return_value=SimpleNamespace(**base)
        response=self.client.post('/api/expenses/quick-add/',{'text':'lunch'},format='json')
        self.assertEqual(response.status_code,201)
        self.assertEqual(Expense.objects.count(),1)
