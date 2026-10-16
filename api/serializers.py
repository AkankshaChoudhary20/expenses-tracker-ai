from rest_framework import serializers
from .models import Expense, CATEGORY_CHOICES


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ['id', 'amount', 'description', 'category', 'date', 'created', 'updated']

    def validate_category(self, value):
        if value and value not in CATEGORY_CHOICES:
            raise serializers.ValidationError('Choose one of the supported expense categories.')
        return value
