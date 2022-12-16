import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import re
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Document
from .models import Dictionary
from .models import Website
from .forms import DocumentForm
from django.conf import settings
import cv2
import nltk
import os
nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords

import base64
import io
import os
import urllib.parse
from typing import Any, List, Optional, Union
import matplotlib.pyplot as plt
import pandas as pd
from django.core.files.uploadedfile import UploadedFile
from PIL import Image
from wordcloud import STOPWORDS, WordCloud



#dir_to_parse = os.path.join('.\.','to_parse')

base_dir = settings.BASE_DIR
media_dir = os.path.join(base_dir, 'media')

fileobj = open(os.path.join(base_dir, 'media')+'/frStopwords.txt', 'rt', encoding='utf8')
frStopwords = []
for line in fileobj:
    frStopwords.append(line.strip())
    
stp = list(STOPWORDS) + frStopwords

def home(request):
    return render(request, 'home.html', {})

def html_parser(data, fileName):
    
    
    soup = BeautifulSoup(data,"html.parser")

    desc = soup.find('meta', attrs={'name': 'description'})
    
        
    paragraphs = soup.findAll('p')
    
    text_paragraphs = desc["content"]+" "
    for paragraph in paragraphs:
        text_paragraphs += paragraph.text
    
    path = show_wordcloud(text_paragraphs,fileName)
    
    if not desc:
        desc = text_paragraphs[0:50]
    else:
        desc = desc["content"]

        
    split_tup = os.path.splitext(fileName)
    newdoc = Document(docfile = fileName, image = path, description = desc, extension = split_tup[1])
    newdoc.save()
        
    list_paragraphs = re.findall(r"\b[a-zA-Zà-ú]+\b", text_paragraphs)
    
    token_list2 = list(filter(lambda token: nltk.tokenize.punkt.PunktToken(token).is_non_punct, list_paragraphs))
            
    token_list3=[word.lower() for word in token_list2 ]
            
    token_list4 = list(filter(lambda token: token not in stp, token_list3))
    
    token_df = pd.value_counts(np.array(token_list4))
    
    for i in range(len(token_df)):
        newWebsite = Dictionary(word= token_df.index[i], occurence = token_df.values[i], file = newdoc)
        newWebsite.save()

def txt_parser(data,fileName):
    
    path = show_wordcloud(data,fileName)
    desc = data[0:50]
    split_tup = os.path.splitext(fileName)
    newdoc = Document(docfile = fileName, image = path, description = desc, extension = split_tup[1])
    newdoc.save()
    
    token_list = nltk.word_tokenize(data, language="french")
            
    token_list2 = list(filter(lambda token: nltk.tokenize.punkt.PunktToken(token).is_non_punct, token_list))
            
    token_list3=[word.lower() for word in token_list2 ]
            
    token_list4 = list(filter(lambda token: token not in stp, token_list3))
            
    token_df = pd.value_counts(np.array(token_list4))
    
    for i in range(len(token_df)):
                newdict = Dictionary(word= token_df.index[i], occurence = token_df.values[i], file = newdoc)
                newdict.save()
                                              
# login_required(login_url='login-view')                      
def my_view(request):
    message = 'Upload as many files as you want!'
        
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            files  = request.POST['files']
            # newdoc = Document(docfile=request.FILES['docfile'])
            # newdoc.save()
            
            # filename = newdoc.docfile.name
            # split_tup = os.path.splitext(filename)
            # Doc = Document.objects.get(docfile=filename)
            # Doc.extension =  split_tup[1]
            context = {'message': files}
            return render(request, 'list.html', context)
        else:
            message = 'The form is not valid. Fix the following error:'
    else:
        form = DocumentForm()  # An empty, unbound form

    # Load documents for the list page
    documents = Document.objects.all()
   
    # Render list page with the documents and the form
    context = {'documents': documents, 'form': form, 'message': message}
    return render(request, 'list.html', context)

def show_wordcloud(data,filename):

    try:
        wordcloud = WordCloud(
            background_color="white",max_words=200,max_font_size=40,
            scale=3,random_state=0,stopwords=stp)
        wordcloud.generate(data)
        
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        
        path = 'media/'+filename+'.png'
        plt.savefig(path,bbox_inches='tight',pad_inches=0,format='png',dpi=300)
        
        return path
    
    except ValueError:
        return None

def fileReader(file):
    base_file = open(file, 'rt', encoding='utf8')
    raw_text = base_file.read()
    base_file.close()
    return raw_text
    
def directoryCrawler(path):
            
            for root,d_names,f_names in os.walk(path):
        
                for file in f_names:
                        # HTML PARSER
                        if file.endswith('.html'):
                            html_parser(fileReader(os.path.join(root, file)), file)
                        # TEXT PARSER
                        elif file.endswith('.txt'):
                            txt_parser(fileReader(os.path.join(root, file)), file)
             
def crawler(request):
    alldata=request.POST
    dir_to_parse = os.path.join('.\.',alldata.get("path"))
    print(dir_to_parse)
    directoryCrawler(dir_to_parse)
    return HttpResponse("POST request")
    
    
    
    
    
def loginView(request):
      
    if request.method == 'POST':
        Username = request.POST.get('Username')
        Password = request.POST.get('Password')
        
        user = authenticate(request, username=Username, password=Password)
        if user is not None:
            login(request, user)
            return redirect('my-view')
            
         
    return render(request, 'login.html', {})

def logoutView(request):
    logout(request)
    return redirect('login-view')

login_required(login_url='login-view')    
def deleteDoc(request, id):
    try:
        doc = Document.objects.get(pk=id)
        doc.delete()
        return redirect('my-view')
    except:
        print('Error')
                
def search_view(request):
    
    
    
    if request.method == 'POST':
        searched = request.POST['searched']
        dicts = Dictionary.objects.filter(word__contains=searched).select_related() 
        #print(dicts)

        return render(request, 'search.html', {'searched':searched, 'dicts':dicts})
    else:
        return render(request, 'search.html', {})