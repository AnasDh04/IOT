from django.shortcuts import render # pour la reponce en html
from django.http import HttpResponse 
# cette fonction fait reference a ce qui doit etre afficher au sein d elle ok 
def say_hello(request): 
#la nature de reponce envoyer
    return HttpResponse('hello world')