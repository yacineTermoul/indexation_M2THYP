from django.db import models

# Create your models here.



class Document(models.Model):
    docfile = models.FileField(upload_to='')
    image = models.ImageField(upload_to='images/')
    #docfile = models.FileField(upload_to='documents/%Y/%m/%d')
    extension= models.CharField(max_length=10)
    description = models.CharField(max_length=500)
    

class Dictionary(models.Model):
    word = models.CharField(max_length=100)
    occurence = models.IntegerField()
    file = models.ForeignKey(
        "Document", on_delete=models.CASCADE)
    
    def __str__(self):
        return self.word + "-->" + self.file
    
class Website(models.Model):
    word = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    
    def __str__(self):
        return self.word + "-->" + self.title