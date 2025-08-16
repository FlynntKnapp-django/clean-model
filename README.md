# Django `ModelForm` Clean Method

- [ModelForm Field Cleaning - ChatGPT - Private](https://chatgpt.com/c/68a0522a-5da4-8324-ba6f-28cb80d95207)
- [ModelForm Field Cleaning - ChatGPT - Shared](https://chatgpt.com/share/68a0a636-f9c4-8002-9ac5-15e075238298)

I have a Django `forms.ModelForm`:

```python
class BodyWeightForm(forms.ModelForm):
    class Meta:
        model = BodyWeight
        fields = ["subject", "measurement"]
        widgets = {
            "subject": forms.Select(attrs={"class": "form-select"}),
            "measurement": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
        }

    def clean_measurement(self):
        val = self.cleaned_data["measurement"]
        if val <= 0:
            raise forms.ValidationError("Measurement must be greater than zero.")
        # Optional: add an upper bound sanity check (e.g., 1500 lb)
        if val > 1500:
            raise forms.ValidationError("That value seems unrealistically high.")
        return val
```

Is the `clean_measurement` method called automatically since it has the pattern `clean_<model name>`?

---

Yes — your `clean_measurement` method will be called automatically.

Here’s why:

### How Django Form Cleaning Works

* When you call `form.is_valid()` (or otherwise trigger form validation), Django runs through its cleaning process:

  1. **Field-level cleaning**
     For each field, Django looks for a method named `clean_<fieldname>()` in your form.

     * In your case, `clean_measurement` matches the field `measurement`, so it will automatically run.
     * Whatever value you return from this method replaces the raw input in `self.cleaned_data["measurement"]`.
  2. **Form-wide cleaning**
     After all fields are cleaned, Django runs the form’s `clean()` method if you’ve defined it. That’s where you can validate across multiple fields.

### Your Example

```python
def clean_measurement(self):
    val = self.cleaned_data["measurement"]
    if val <= 0:
        raise forms.ValidationError("Measurement must be greater than zero.")
    if val > 1500:
        raise forms.ValidationError("That value seems unrealistically high.")
    return val
```

* This will always be called when validating the `measurement` field.
* If validation fails, Django collects the `ValidationError` and associates it with the `measurement` field, so the error shows up next to that field in the form.

### TL;DR

✅ Yes, `clean_measurement` is automatically called during validation because it follows the `clean_<fieldname>` convention.
⚠️ If you want to validate using multiple fields at once, you’d use the form’s `clean()` method instead.

Do you want me to also show you **how to test this with a quick unit test** so you can see it firing in action?

---

Yes, provide a unit test for this.

---

Got you. Here are tight Django unit tests that prove `clean_measurement` runs and attaches errors to the **measurement** field. They also include a “happy path” test that passes when the value is reasonable.

```python
# tests/test_forms_bodyweight.py
from decimal import Decimal
from django.test import TestCase

# Adjust the import paths to match your project layout
from vitals.forms import BodyWeightForm


class BodyWeightFormTests(TestCase):
    def test_rejects_zero_or_negative_measurement(self):
        """clean_measurement should flag 0 and negative values."""
        for bad in [0, -1, -0.5]:
            with self.subTest(bad=bad):
                form = BodyWeightForm(data={"measurement": bad})
                # We don't care about subject here; we're isolating the measurement errors.
                if "subject" in form.fields:
                    form.fields["subject"].required = False

                self.assertFalse(form.is_valid())
                self.assertIn("measurement", form.errors)
                # One of the errors should be our custom message for <= 0
                self.assertTrue(
                    any("greater than zero" in e for e in form.errors["measurement"]),
                    msg=form.errors["measurement"],
                )

    def test_rejects_unrealistically_high_measurement(self):
        """clean_measurement should flag unrealistically high values (>1500)."""
        form = BodyWeightForm(data={"measurement": 2000})
        if "subject" in form.fields:
            form.fields["subject"].required = False

        self.assertFalse(form.is_valid())
        self.assertIn("measurement", form.errors)
        self.assertTrue(
            any("unrealistically high" in e for e in form.errors["measurement"]),
            msg=form.errors["measurement"],
        )

    def test_accepts_reasonable_measurement(self):
        """
        A reasonable value should pass field validation and land in cleaned_data.
        If your 'subject' field is required (e.g., a FK), we relax it to keep
        this test focused on measurement validation only.
        """
        form = BodyWeightForm(data={"measurement": "180"})
        if "subject" in form.fields:
            form.fields["subject"].required = False

        self.assertTrue(form.is_valid(), msg=form.errors)
        # The cleaned value should be a Decimal if your model uses DecimalField
        self.assertEqual(form.cleaned_data["measurement"], Decimal("180"))
```

### Notes

* These tests deliberately **relax `subject`** to avoid coupling to your Subject/relations when the goal is verifying `clean_measurement`. If you prefer a full integration test, create a valid `subject` instance and pass its primary key in `data` instead of toggling `required`.
* If your `BodyWeight.measurement` is a `FloatField`, change the final assertion to `float(form.cleaned_data["measurement"]) == 180.0`.

---
