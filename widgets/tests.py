from django.test import TestCase
from widgets.forms import WidgetForm
from .models import Widget


class WidgetFormTests(TestCase):

    def test_invalid_negative_weight(self):
        form = WidgetForm(data={"name": "Test Widget", "weight": -10})
        self.assertFalse(form.is_valid())
        self.assertIn("weight", form.errors)
        self.assertIn("Weight must be positive.", form.errors["weight"])

    def test_valid_form(self):
        form = WidgetForm(data={"name": "Test Widget", "weight": 50})
        self.assertTrue(form.is_valid())

    def test_invalid_greater_weight(self):
        form = WidgetForm(data={"name": "Test Widget", "weight": 150})
        self.assertFalse(form.is_valid())
        self.assertIn("weight", form.errors)
        self.assertIn("Weight must be 100 or less.", form.errors["weight"])


class WidgetModelTests(TestCase):
    def setUp(self):
        self.widget = WidgetForm(data={"name": "Test Widget", "weight": 50})
        self.widget.is_valid()
        self.widget.save()

    def test_widget_creation(self):
        self.assertTrue(Widget.objects.filter(name="Test Widget").exists())

    def test_widget_dunder_str(self):
        self.assertEqual(str(self.widget.instance), "Test Widget")
