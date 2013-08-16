import django.shortcuts


def main(request):
    return django.shortcuts.render(request, 'index.html')
