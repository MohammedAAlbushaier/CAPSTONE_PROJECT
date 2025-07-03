from django import forms
from .models import TrainingOpportunity, City, Major


class TrainingOpportunityForm(forms.ModelForm):
    # Define choices for the duration dropdown
    DURATION_CHOICES = [
        ('1_month', 'شهر'),
        ('2_months', 'شهرين'),
        ('3_months', '٣ شهور'),
        ('6_months', '٦ شهور'),
        ('other', 'أخرى (بالأسابيع)'),
    ]

    # Use a CharField for the dropdown selection
    # This field will not directly map to the model's 'duration'
    duration_selection = forms.ChoiceField(
        choices=DURATION_CHOICES,
        label="المدة",
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # A separate field for custom duration in weeks, not required by default
    other_duration_weeks = forms.IntegerField(
        label="المدة بالأسابيع",
        required=False, # Make it optional, as it's only needed if 'other' is selected
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'أدخل المدة بالأسابيع'}))

    city = forms.ModelChoiceField(
        queryset=City.objects.filter(status=True),
        label="المدينة", # Changed label to Arabic
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    majors_needed = forms.ModelMultipleChoiceField(
        queryset=Major.objects.all(),
        label="التخصصات المطلوبة", # Changed label to Arabic
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'multiple': 'multiple'})
    )
    start_date = forms.DateField(
        label="تاريخ البدء", # Changed label to Arabic
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    application_deadline = forms.DateField(
        label="آخر موعد للتقديم", # Changed label to Arabic
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    description = forms.CharField(
        label="وصف الفرصة", # Changed label to Arabic
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    requirements = forms.CharField(
        label="متطلبات الفرصة", # Changed label to Arabic
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    benefits = forms.CharField(
        label="مميزات الفرصة", # Changed label to Arabic
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False  # Make benefits optional
    )
    # The original 'duration' field is managed by the clean method now.
    status = forms.ChoiceField(
        label="حالة الفرصة", # Changed label to Arabic
        choices=TrainingOpportunity.Status.choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, skip_required=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.skip_required = skip_required
        if skip_required:
            for field in self.fields.values():
                field.required = False

        # Initialize the form with existing instance data for editing
        if self.instance and self.instance.pk:
            # If editing an existing instance, set the initial value of duration_selection
            # based on the stored 'duration' (in weeks)
            duration_in_weeks = self.instance.duration

            if duration_in_weeks == 4:
                self.initial['duration_selection'] = '1_month'
            elif duration_in_weeks == 8:
                self.initial['duration_selection'] = '2_months'
            elif duration_in_weeks == 12:
                self.initial['duration_selection'] = '3_months'
            elif duration_in_weeks == 24:
                self.initial['duration_selection'] = '6_months'
            else:
                # If it's not one of the predefined options, set to 'other'
                self.initial['duration_selection'] = 'other'
                self.initial['other_duration_weeks'] = duration_in_weeks
        else:
            # For new forms, ensure default selection is set if needed, or leave blank
            self.initial['duration_selection'] = '1_month' # Default to 1 month for new forms


    # Custom clean method to handle the duration logic
    def clean(self):
        cleaned_data = super().clean()
        duration_selection = cleaned_data.get('duration_selection')
        other_duration_weeks = cleaned_data.get('other_duration_weeks')

        if duration_selection == 'other':
            if not other_duration_weeks:
                self.add_error('other_duration_weeks', 'الرجاء إدخال المدة بالأسابيع.')
            elif other_duration_weeks < 1:
                self.add_error('other_duration_weeks', 'يجب أن تكون المدة بالأسابيع رقمًا موجبًا.')
            else:
                # Set the actual 'duration' field of the model instance
                # This will be stored in the model's 'duration' field (in weeks)
                self.instance.duration = other_duration_weeks
        else:
            # Convert predefined choices to weeks
            if duration_selection == '1_month':
                self.instance.duration = 4  # Approximately 4 weeks
            elif duration_selection == '2_months':
                self.instance.duration = 8
            elif duration_selection == '3_months':
                self.instance.duration = 12
            elif duration_selection == '6_months':
                self.instance.duration = 24
            # If no selection or invalid, it might be handled by model defaults or validation

        # Keep original skip_required logic
        if not self.skip_required:
            # Additional validation logic if necessary
            pass
        return cleaned_data

    class Meta:
        model = TrainingOpportunity
        # Exclude the original 'duration' field from the Meta.fields,
        # as we're handling it via custom form fields and clean method.
        # Include all other fields you need.
        fields = [
            'title', 'city', 'majors_needed', 'description', 'requirements',
            'benefits', 'start_date', 'application_deadline', 'status'
        ]
        # Widgets are already defined in the field definitions above,
        # so this Meta.widgets block is no longer strictly necessary if all are defined above.
        # However, keeping it for clarity or if there are other fields not explicitly defined.
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.Select(attrs={'class': 'form-select'}), # Removed select-search here as Choices.js handles it
            'majors_needed': forms.SelectMultiple(attrs={'class': 'form-select', 'multiple': 'multiple'}), # Removed select-major here
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'benefits': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'application_deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            # 'duration' is excluded
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

