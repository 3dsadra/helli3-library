from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from web.models import Book, User, Transaction
from django.utils import timezone
from web.forms import LoginForm, RegisterForm

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            return redirect('admin_dashboard')
        else:
            return redirect('member_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'خوش آمدید {user.username}!')
            
            if user.is_admin:
                return redirect('admin_dashboard')
            else:
                return redirect('member_dashboard')
        else:
            messages.error(request, 'نام کاربری یا رمز عبور اشتباه است')
            return render(request, 'login.html', {'form': LoginForm()})
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            return redirect('admin_dashboard')
        else:
            return redirect('member_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'این نام کاربری قبلاً استفاده شده است')
            else:
                user = User.objects.create_user(
                    username=username,
                    password=password1,
                    is_admin=False
                )
                login(request, user)
                messages.success(request, f'ثبت‌نام با موفقیت انجام شد. خوش آمدید {user.username}!')
                return redirect('member_dashboard')
        else:
            messages.error(request, 'رمز عبور و تکرار آن یکسان نیستند')
    
    return render(request, 'register.html', {'form': RegisterForm()})

def logout_view(request):
    logout(request)
    messages.info(request, 'با موفقیت از سیستم خارج شدید')
    return redirect('login')

@login_required(login_url='login')
def home(request):
    if request.user.is_admin:
        return redirect('admin_dashboard')
    else:
        return redirect('member_dashboard')

@login_required(login_url='login')
def admin_dashboard(request):
    if not request.user.is_admin:
        messages.error(request, 'شما مجاز به دسترسی به این بخش نیستید')
        return redirect('member_dashboard')
    
    books = Book.objects.all()
    users = User.objects.all()
    transactions = Transaction.objects.all()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action:
            pass
    
    return render(request, 'admin_dashboard.html', {
        'books': books,
        'users': users,
        'transactions': transactions,
    })

@login_required(login_url='login')
def member_dashboard(request):
    books = Book.objects.all()
    
    my_borrowed_books = Book.objects.filter(
        borrowed_by=request.user, 
        status=Book.Status.BORROWED
    )
    
    my_reserved_books = Book.objects.filter(
        reserved_by=request.user,
        status=Book.Status.RESERVED
    )
    
    available_books = Book.objects.filter(status=Book.Status.AVAILABLE)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'borrow_book':
            book_id = request.POST.get('book_id')
            book = Book.objects.filter(id=book_id).first()
            if book:
                if book.status == Book.Status.AVAILABLE:
                    book.status = Book.Status.BORROWED
                    book.borrowed_by = request.user
                    book.save()
                    
                    Transaction.objects.create(
                        book=book,
                        user=request.user,
                        action=Transaction.Action.BORROW,
                        date=timezone.now()
                    )
                    
                    messages.success(request, f'کتاب "{book.name}" با موفقیت امانت گرفته شد!')
                else:
                    messages.error(request, 'این کتاب در حال حاضر موجود نیست')
            else:
                messages.error(request, 'کتاب مورد نظر یافت نشد')
        
        return redirect('member_dashboard')
    
    return render(request, 'member_dashboard.html', {
        'books': books,
        'my_borrowed_books': my_borrowed_books,
        'my_reserved_books': my_reserved_books,
        'available_books': available_books,
    })