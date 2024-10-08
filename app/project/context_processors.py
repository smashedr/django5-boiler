# import zoneinfo
# from django.utils import timezone
# from django.core.cache import cache
# from django.forms.models import model_to_dict


def site(request):
    # try:
    #     time_zone = request.COOKIES.get("timezone")
    #     if time_zone:
    #         timezone.activate(zoneinfo.ZoneInfo(time_zone))
    #     else:
    #         timezone.deactivate()
    # except Exception:
    #     timezone.deactivate()

    meta = {
        'author': 'Shane',
        'title': 'My App',
        'description': 'My App is a good app...',
    }

    navigation = [
        {'name': 'Home', 'url': 'home:index', 'path': '/'},
        {'name': 'News', 'url': 'home:news', 'path': '/news/'},
        {'name': 'Message', 'url': 'home:message', 'path': '/message/'},
        {'name': 'Contact', 'url': 'home:contact', 'path': '/contact/'},
    ]

    return {
        "meta": meta,
        "navigation": navigation,
    }
