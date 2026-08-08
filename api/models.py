from django.db import models

CATEGORY_CHOICES = [
    "Food & Dining",
    "Transportation",
    "Housing",
    "Utilities",
    "Shopping",
    "Entertainment",
    "Health & Fitness",
    "Travel",
    "Education",
    "Personal Care",
    "Other",
]


class Expense(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=400)
    category = models.CharField(max_length=50, blank=True)
    date = models.DateField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created']

    def __str__(self):
        return f"{self.date} - {self.description[:40]} (${self.amount})"
