from django import template
from web.models import User, Book, Transaction
from django.utils import timezone

register = template.Library()

@register.simple_tag
def borrow_book(book_id, username):
    try:
        book = Book.objects.get(id=book_id)
        user = User.objects.get(username=username)
        
        if book.status != Book.Status.AVAILABLE:
            return "Book is not available for borrowing"
        
        if Transaction.objects.filter(book=book, user=user, returned=False).exists():
            return f'User "{username}" already has this book'
        
        Transaction.objects.create(
            book=book,
            user=user,
            action=Transaction.Action.BORROW,
            date=timezone.now()
        )
        
        book.status = Book.Status.BORROWED
        book.borrowed_by = user
        book.save()
        
        return f'Book "{book.name}" borrowed by {username}'
    except Book.DoesNotExist:
        return "Book not found"
    except User.DoesNotExist:
        return f'User "{username}" not found'

@register.simple_tag
def reserve_book(book_id, username):
    try:
        book = Book.objects.get(id=book_id)
        user = User.objects.get(username=username)
        
        if book.status == Book.Status.RESERVED:
            return "Book is already reserved"
        
        if book.status == Book.Status.BORROWED:
            return "Book is currently borrowed, cannot reserve"
        
        book.status = Book.Status.RESERVED
        book.save()
        
        return f'Book "{book.name}" reserved by {username}'
    except Book.DoesNotExist:
        return "Book not found"
    except User.DoesNotExist:
        return f'User "{username}" not found'

@register.simple_tag
def view_book(book_id):
    try:
        book = Book.objects.get(id=book_id)
        return f"Book: {book.name} | Author: {book.author} | Status: {book.status} | Extra: {book.extra}"
    except Book.DoesNotExist:
        return "Book not found"

### Admin User Functions
@register.simple_tag
def add_book(name, author, extra):
    if not name or not author:
        return "Book name and author are required"
    
    if Book.objects.filter(name=name, author=author).exists():
        return f'Book "{name}" by {author} already exists'
    
    book = Book(
        name=name,
        author=author,
        extra=extra,
        status=Book.Status.AVAILABLE,
    )
    book.save()
    return f'Book "{name}" added successfully!'

@register.simple_tag
def remove_book(book_id):
    try:
        book = Book.objects.get(id=book_id)
        name = book.name
        book.delete()
        return f'Book "{name}" removed successfully!'
    except Book.DoesNotExist:
        return "Book not found!"

@register.simple_tag
def lend_book(book_id, username):
    try:
        book = Book.objects.get(id=book_id)
        user = User.objects.get(username=username)
        
        if book.status != Book.Status.AVAILABLE:
            return "Book is not available to lend"
        
        transaction = Transaction.objects.create(
            book=book,
            user=user,
            borrow_date=timezone.now(),
            returned=False
        )
        book.status = Book.Status.BORROWED
        book.save()
        
        return f'Book "{book.name}" lent to {username}'
    except Book.DoesNotExist:
        return "Book not found"
    except User.DoesNotExist:
        return f'User "{username}" not found'

@register.simple_tag
def receive_book(book_id):
    try:
        book = Book.objects.get(id=book_id)
        
        if book.status == Book.Status.AVAILABLE:
            return "Book is already available"
        
        transaction = Transaction.objects.filter(book=book, returned=False).first()
        if transaction:
            transaction.returned = True
            transaction.return_date = timezone.now()
            transaction.save()
        
        book.status = Book.Status.AVAILABLE
        book.save()
        
        return f'Book "{book.name}" received back!'
    except Book.DoesNotExist:
        return "Book not found"