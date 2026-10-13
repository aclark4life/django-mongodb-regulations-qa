# documents/models.py
from django.db import models


class Document(models.Model):
    document_number = models.CharField(max_length=32, unique=True)
    title = models.TextField()
    doc_type = models.CharField(max_length=32)
    agency = models.CharField(max_length=128)
    publication_date = models.DateField()
    abstract = models.TextField()
    source_url = models.URLField(max_length=500)

    def __str__(self):
        return f"{self.document_number}: {self.title[:60]}"