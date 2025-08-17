from .models import Widget
from django import forms


class WidgetForm(forms.ModelForm):
    class Meta:
        model = Widget
        fields = ["name", "weight"]

    def clean_weight(self):
        weight = self.cleaned_data.get("weight")
        if weight is not None and weight <= 0:
            raise forms.ValidationError("Weight must be positive.")
        elif weight > 100:
            raise forms.ValidationError("Weight must be 100 or less.")
        return weight
