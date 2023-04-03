from .models import Customer
from django import forms

# from phonenumber_field.phonenumber import PhoneNumber

# Create your forms here.

class CustomerForm(forms.ModelForm):
    class Meta:
        model  = Customer
        fields = [
            'name',
            'phone'
        ]
    
    def clean_name(self, *args, **kwargs):
        name = self.cleaned_data.get('name')
        invalidChars = ['&', '!', '@', '#', '$', '%', '^', '*', '(', ')', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
        for char in invalidChars:
            if char in name:
                raise forms.ValidationError("This is not a valid name!")
        return name
    
    def clean_phone(self, *args, **kwargs):
        phone = self.cleaned_data.get('phone') # object of type "PhoneNumber"
        # if not len(str(phone.national_number)) == 9:
        #     print(phone.national_number)
        #     raise forms.ValidationError("This is not a valid phone number!")
        if not str(phone).startswith("+9639"):
            raise forms.ValidationError("This is not a valid syrian phone number!")
        return phone
