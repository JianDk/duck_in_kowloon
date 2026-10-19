from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect, render
from django.views import View
from .forms import ContactForm
from .models import Dish
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# Create your views here.
class IndexView(View):
    @method_decorator(login_required(login_url='login'))
    def get(self, request, *args, **kwargs):
        context = {
            "title": "Duck In Kowloon | Hong Kong Roasted Duck in Copenhagen",
        }
        return render(
            request=request,
            template_name="index.html",
            context=context,
        )

