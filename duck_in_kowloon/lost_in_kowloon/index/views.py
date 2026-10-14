from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect, render
from django.views import View
from .forms import ContactForm
from .models import Dish

# Create your views here.
class IndexView(View):
    def get(self, request, *args, **kwargs):
        dishes = Dish.objects.filter(is_active=True).order_by("display_order", "name")[:15]
        context = {
            "title": "Duck In Kowloon | Hong Kong Roasted Duck in Copenhagen",
            "dishes": dishes,
        }
        return render(
            request=request,
            template_name="index.html",
            context=context,
        )


class ContactView(View):
    def get(self, request, *args, **kwargs):
        context = {
            "title": "Contact Duck In Kowloon",
            "form": ContactForm(),
        }
        return render(request, "contact.html", context)

    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if form.is_valid():
            sender_email = form.cleaned_data["email"]
            recipient_email = getattr(settings, "CONTACT_RECIPIENT_EMAIL", None)
            from_email = getattr(settings, "DEFAULT_FROM_EMAIL", sender_email)

            if not recipient_email:
                messages.error(request, "Contact email is not configured yet.")
                context = {
                    "title": "Contact Duck In Kowloon",
                    "form": form,
                }
                return render(request, "contact.html", context)
            else:
                subject = f"Duck In Kowloon contact from {form.cleaned_data['name']}"
                body = (
                    f"Name: {form.cleaned_data['name']}\n"
                    f"Email: {sender_email}\n"
                    f"Phone: {form.cleaned_data['phone']}\n\n"
                    f"Message:\n{form.cleaned_data['message']}"
                )
                try:
                    send_mail(
                        subject=subject,
                        message=body,
                        from_email=from_email,
                        recipient_list=[recipient_email],
                        fail_silently=False,
                    )
                except Exception:
                    messages.error(request, "We could not send your message right now. Please try again.")
                    context = {
                        "title": "Contact Duck In Kowloon",
                        "form": form,
                    }
                    return render(request, "contact.html", context)

                messages.success(request, "Thanks. Your message has been sent.")
                return redirect("contact")

        messages.error(request, "Please fix the form errors and try again.")
        context = {
            "title": "Contact Duck In Kowloon",
            "form": form,
        }
        return render(request, "contact.html", context)