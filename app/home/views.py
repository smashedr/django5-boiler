import logging
import httpx
# import json
from django.conf import settings
# from django.core.exceptions import ObjectDoesNotExist
# from django.contrib import messages
from django.http import JsonResponse, HttpRequest
from django.shortcuts import render, get_object_or_404
# from django.views.decorators.cache import cache_page, cache_control
# from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
# from django.views.decorators.vary import vary_on_cookie
from .forms import MessageForm, ContactForm
from .models import Contact, Message, MyNews
from .tasks import send_discord_message, send_contact_email

logger = logging.getLogger('app')


def home_view(request):
    # View: /
    logger.debug('home_view: %s - %s', request.method, request.META['PATH_INFO'])
    # logger.debug('-'*20)
    # logger.debug(request.META)
    # logger.debug('-'*20)
    # logger.debug(request.body)
    # logger.debug('-'*20)
    # messages.info(request, 'Welcome Home.')
    return render(request, 'home.html')


# @cache_control(no_cache=True)
# @cache_page(120, key_prefix="news")
# @vary_on_cookie
def news_view(request):
    # View: /news/
    logger.debug('news_view: %s - %s', request.method, request.META['PATH_INFO'])
    q = MyNews.objects.get_active()
    return render(request, 'news.html', {'news': q})


@require_http_methods(['GET', 'POST'])
def message_view(request):
    # View: /message/
    logger.debug('message_view: %s - %s', request.method, request.META['PATH_INFO'])
    if request.method == 'GET':
        return render(request, 'message.html')

    try:
        logger.debug('request.POST: %s', request.POST)
        form = MessageForm(request.POST)
        if not form.is_valid():
            logger.debug('form.errors: %s', form.errors)
            return JsonResponse(form.errors, status=400)

        logger.debug('form.cleaned_data: %s', form.cleaned_data)

        if not request.user.is_authenticated and not google_verify(request):
            data = {'error': 'Google CAPTCHA not verified.'}
            return JsonResponse(data, status=400)

        data = form.cleaned_data.copy()
        del data['reason']
        message = Message.objects.create(**data)
        logger.debug('message: %s', message)
        send_discord_message.delay(message.pk)
        return JsonResponse({}, status=200)

    except Exception as error:
        logger.exception(error)
        return JsonResponse({'error': str(error)}, status=400)


@require_http_methods(['GET', 'POST'])
def contact_view(request):
    # View: /contact/
    logger.debug('contact_view: %s - %s', request.method, request.META['PATH_INFO'])
    if request.method != 'POST':
        return render(request, 'contact.html')

    try:
        logger.debug('request.POST: %s', request.POST)
        logger.debug(request.POST)
        form = ContactForm(request.POST)
        if not form.is_valid():
            logger.debug('form.errors: %s', form.errors)
            return JsonResponse(form.errors, status=400)

        logger.debug('form.cleaned_data: %s', form.cleaned_data)

        if not request.user.is_authenticated and not google_verify(request):
            data = {'error_message': 'Google CAPTCHA not verified.'}
            return JsonResponse(data, status=400)

        contact = Contact.objects.create(**form.cleaned_data)
        logger.debug('contact.pk: %s', contact.pk)
        send_contact_email.delay(contact.pk)
        return JsonResponse({}, status=200)

    except Exception as error:
        logger.exception(error)
        return JsonResponse({'error_message': str(error)}, status=400)


def contact_html_view(request, view, uuid):
    # View: /contact/{view}/{uuid}/
    logger.debug('contact_html_view: %s - %s', request.method, request.META['PATH_INFO'])
    logger.debug('view: %s - uuid: %s)', view, uuid)
    if view == 'browser':
        template = 'email/contact.html'
    else:
        template = 'contact/browser-view.html'

    q = get_object_or_404(Contact, uuid=uuid)
    context = {'contact': q, 'browser': True}
    return render(request, template, context)


def google_verify(request: HttpRequest) -> bool:
    if request.session.get('g_verified', False):
        return True
    try:
        url = 'https://www.google.com/recaptcha/api/siteverify'
        data = {
            'secret': settings.GOOGLE_SITE_SECRET,
            'response': request.POST['g-recaptcha-response']
        }
        logger.debug('data: %s', data)
        r = httpx.post(url, data=data, timeout=10)
        if r.is_success and r.json()['success']:
            request.session['g_verified'] = True
            return True
        return False
    except Exception as error:
        logger.exception(error)
        return False
