from django.conf import settings
from django.shortcuts import render
from django.views import View

class ContactView(View):
    def get(self, request, *args, **kwargs):
        context = dict()
        context['title'] = 'Contact Us | Duck In Kowloon, Copenhagen'
        context['recaptcha_site_key'] = settings.RECAPTCHA_SITE_KEY
        return render(request = request, template_name='contact.html', context=context)

