from django.forms import ModelForm
from django import forms
from subscriber_management.models import List, Subscriber

class ListForm(ModelForm):
    class Meta:
        model = List
        localized_fields = ('name','title', 'description', 'url')
        fields = ('name','title', 'description', 'url')

    name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), required=True)
    title = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), required=True)
    description = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control'}), required=False)
    url = forms.URLField(widget=forms.TextInput(attrs={'class':'form-control'}),max_length=4000, required=False)

class SubscriberForm(ModelForm):
    class Meta:
        model = Subscriber
        localized_fields = ('email',)
        fields = ('email',)

    email = forms.EmailField(widget=forms.TextInput(attrs={'class':'form-control'}), required=True)
