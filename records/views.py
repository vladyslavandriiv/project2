from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, AnimalForm, DoctorForm, VisitForm
from .models import Animal, Doctor, Visit
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa

def home_view(request):
    return render(request, 'records/home.html')

def register_view(request):
    form = UserRegisterForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('records:login')
    return render(request, 'records/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(request.GET.get('next') or 'records:dashboard')  # ✅ виправлено тут
        else:
            messages.error(request, "Невірне ім'я користувача або пароль.")
    else:
        form = AuthenticationForm()
    return render(request, 'records/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('records:login')

@login_required
def dashboard(request):
    animals = Animal.objects.filter(owner=request.user)
    return render(request, 'records/dashboard.html', {'animals': animals})

@login_required
def create_animal(request):
    form = AnimalForm(request.POST or None)
    if form.is_valid():
        animal = form.save(commit=False)
        animal.owner = request.user
        animal.save()
        return redirect('records:dashboard')
    return render(request, 'records/animal_form.html', {'form': form})

@login_required
def update_animal(request, id):
    animal = get_object_or_404(Animal, id=id, owner=request.user)
    form = AnimalForm(request.POST or None, instance=animal)
    if form.is_valid():
        form.save()
        return redirect('records:dashboard')
    return render(request, 'records/animal_form.html', {'form': form})

@login_required
def delete_animal(request, id):
    animal = get_object_or_404(Animal, id=id, owner=request.user)
    animal.delete()
    return redirect('records:dashboard')

@login_required
def create_doctor(request):
    form = DoctorForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('records:list_doctors')
    return render(request, 'records/doctor_form.html', {'form': form})

@login_required
def list_doctors(request):
    doctors = Doctor.objects.all()
    return render(request, 'records/doctors.html', {'doctors': doctors})

@login_required
def create_visit(request):
    form = VisitForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('records:list_visits')
    return render(request, 'records/visit_form.html', {'form': form})

@login_required
def list_visits(request):
    visits = Visit.objects.filter(animal__owner=request.user)
    return render(request, 'records/visits.html', {'visits': visits})

@login_required
def generate_pdf(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id, owner=request.user)
    visits = Visit.objects.filter(animal=animal)
    html = render_to_string('records/animal_pdf.html', {'animal': animal, 'visits': visits})
    response = HttpResponse(content_type='application/pdf')
    pisa_status = pisa.CreatePDF(html, dest=response)
    return response
