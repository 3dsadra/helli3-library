from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_admin = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to.'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.'
    )
        
    def __str__(self):
        return self.username

class Book(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = 'available', 'Available'
        BORROWED = 'borrowed', 'Borrowed'
        RESERVED = 'reserved', 'Reserved'
    
    name = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    extra = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE
    )
    
    # For borrowed/reserved status tracking
    borrowed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='borrowed_books'
    )
    reserved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reserved_books'
    )
    return_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} by {self.author}"

class Transaction(models.Model):
    class Action(models.TextChoices):
        BORROW = 'borrow', 'Borrow'
        RETURN = 'return', 'Return'
        RESERVE = 'reserve', 'Reserve'
    
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=Action.choices)
    date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.book.name}"