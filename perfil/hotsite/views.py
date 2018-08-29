from django.shortcuts import render


def hotsite(request):
    return render(request, 'hotsite/index.html')
