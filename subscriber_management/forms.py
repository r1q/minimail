from django.forms import ModelForm
from django import forms

from subscriber_management.models import List, Subscriber


class ListForm(ModelForm):
    class Meta:
        model = List
        localized_fields = ('image', 'from_email','name','title', 'description', 'url', 'success_template',)
        fields = ('image', 'from_email', 'name', 'title', 'description', 'url', 'success_template',)

    name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), required=True)
    from_email = forms.EmailField(widget=forms.TextInput(attrs={'class':'form-control'}), required=True)
    title = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), required=True)
    description = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control'}), required=True)
    url = forms.URLField(widget=forms.TextInput(attrs={'class':'form-control'}),max_length=4000, required=False)
    success_template = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control'}), required=False)


class SubscriberForm(ModelForm):
    class Meta:
        model = Subscriber
        localized_fields = ('email',)
        fields = ('email',)

    email = forms.EmailField(widget=forms.TextInput(attrs={'class':'form-control'}),
                             required=True)


class ListSettingsForm(ModelForm):
    class Meta:
        model = List
        localized_fields = ('name', 'utm_source', 'utm_medium', 'language')
        fields = ('name', 'utm_source', 'utm_medium', 'language')

    name = forms.CharField(required=True)
    utm_medium = forms.CharField(required=False)
    utm_source = forms.CharField(required=False)


class ListNewsletterHomepage(ModelForm):
    class Meta:
        model = List
        localized_fields = ('image', 'title', 'description', 'url',
                            'success_template',)
        fields = ('image', 'title', 'description', 'url', 'success_template',)

    title = forms.CharField(required=True)


class ListNewsletterImportCSV(forms.Form):
    csv_file = forms.FileField()
