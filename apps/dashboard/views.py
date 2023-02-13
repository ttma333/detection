from django.shortcuts import render

def landing(request):
   return render(
       request,
       'dashboard/landing.html'
   )