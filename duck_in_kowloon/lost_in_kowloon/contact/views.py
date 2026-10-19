from django.shortcuts import render
# Create your views here.
from django.views import View
from django.shortcuts import render
# Create your views here.

class ContactView(View):
    def get(self, request, *args, **kwargs):
        context = dict()
        context['title'] = 'Contact us'
        return render(request = request, template_name='contact.html', context=context)