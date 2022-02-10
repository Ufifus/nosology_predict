from django.shortcuts import render, HttpResponse, redirect
from django.views.generic.list import ListView, View
from django.template.defaultfilters import slugify
from django.db.models import Count
from django.http import FileResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .models import *
from .forms import *

import pandas as pd


"""Главная страница сайта"""
def Hall_page(request):
    return render(request, 'nosologies/hall_page.html')


"""Страница с авторизаций пользователя"""
def User_Login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            print(request.POST)
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('/')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'nosologies/login.html', {'form': form})


"""Страница с регистраций нового пользователя"""
def RegisterNewUser(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            return render(request, 'nosologies/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'nosologies/register.html', {'user_form': user_form})


"""Выход пользователя из аккаунта"""
@login_required
def UserLogOut(request):
    logout(request)
    return redirect('/')


"""Страница с просмотром нозологий"""
class NosologyListAll(ListView):

    template_name = 'nosologies/list_nosology.html'
    paginate_by = 2
    model = Nosology
    context_object_name = 'nosology'

    def get_queryset(self):
        return Nosology.objects.all()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        return context


"""Поиск нозологий по запросу"""
class SearchNosologyList(ListView):

    template_name = 'nosologies/list_nosology.html'
    paginate_by = 20
    model = Nosology
    context_object_name = 'nosology'

    def get_queryset(self):
        return Nosology.objects.filter(nosologyname=self.request.GET.get("q"))

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['q'] = self.request.GET.get("q")
        context['all'] = True
        return context


"""Добавление нозологии"""
@login_required
def AddNosology(request):
    if request.method == 'POST':
        for nosology in Nosology.objects.all():
            if request.POST['nosologyname'] == nosology.nosologyname:
                try:
                    return HttpResponse('<p>Nosology is exist now</p>')
                except:
                    pass
        form = NosologyForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.url = form.nosologyname
            form.save()
            return redirect('/nosologies')


"""Страница с наблюдениями нозологии"""
class NosologyObserverList(View):

    def get(self, request, url):
        nosology = Nosology.objects.get(url=url)
        data = Nosologydata.objects.filter(idnosology=nosology)
        try:
            corteges = Observer.objects.filter(idmodel=data[0]).latest().cortege
        except:
            corteges = 0
        observe = []
        for index in range(corteges+1):
            row = []
            for d in data:
                try:
                    query = Observer.objects.get(idmodel=d, cortege=index)
                except Observer.DoesNotExist:
                    query = None
                row.append(query)
            observe.append(row)
        paginator = Paginator(observe, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'page_obj': page_obj,
            'data': data,
            'nosology': nosology,
        }
        return render(request, 'nosologies/data_observer.html', context)


"""Скачиваем все наблюдения по определенной нозологии"""
def DownloadFile(request, idnosology):

    i = 0
    observe = []
    matrix = {}
    nosology = Nosology.objects.get(idnosology=idnosology).nosologyname
    data = Nosologydata.objects.filter(idnosology=idnosology)
    for d in data:
        i += 1
        query = Observer.objects.filter(idmodel=d.iddata)
        observe.append(query)
        row = []
        for q in query:
            row.append(q.val)
        matrix[f'{d}'] = row
        matrix = pd.DataFrame(matrix)
    name_file = f'{nosology}_file.csv'
    try:
        matrix.to_csv(name_file)
    except:
        return HttpResponse('<p>File is Void</p>')
    return FileResponse(open(name_file, 'rb'))


"""Загружаем данные по определенной нозологии"""
@login_required
def UploadFile(request, url):
    """Upload file in database"""

    nosology = Nosology.objects.get(url=url)
    print(nosology)

    if request.method == 'POST':
        file = request.FILES['file']
        inf = pd.read_csv(file)
        data_list = get_data(inf, nosology)
        get_observer(inf, data_list)
        return redirect('/nosologies')

def get_data(inf, nosology):
    l = []
    try:
        exist = Nosologydata.objects.filter(idnosology=nosology).latest()
    except:
        exist = None

    if exist is not None:
        if len(Nosologydata.objects.filter(idnosology=nosology)) != len(inf[1:]):
            return HttpResponse('<p>Error, not simple size</p>')

    for i, data in enumerate(inf.columns[1:]):
        dtype = str(inf.dtypes[i+1])
        print('dtype', len(dtype), dtype)
        try:
            nosdata = Nosologydata.objects.get_or_create(idnosology=nosology, value=data, valuetype=dtype)
        except:
            nosdata = Nosologydata.objects.get_or_create(idnosology=nosology, value=data, valuetype='none')
        l.append(nosdata[0])
    print(l)
    return l

def get_observer(inf, data_list):
    if len(data_list) == 0:
        return HttpResponse('<p>Error</p>')
    else:
        inf = inf.to_numpy()
        try:
            corteges = Observer.objects.filter(idmodel=data_list[0]).latest().cortege + 1
        except:
            corteges = 0
        for cortege, row in enumerate(inf):
            user = get_user(row[-1])
            for i, col in enumerate(data_list):
                observe = Observer(idmodel=col,
                                   iduser=Patient.objects.get(username=user),   #потом добавить выбор пациента
                                   val=row[i+1],
                                   cortege=corteges + cortege)
                observe.save()

def get_user(name):
    try:
        user = Patient.objects.get(username=name)
    except Patient.DoesNotExist:
        slug = slugify(name)
        user = Patient.objects.create(username=name, url=slug)
    return user


"""Страница с просмотром пациентов"""
class PatientsList(ListView):
    model = Patient
    template_name = 'nosologies/list_patients.html'
    context_object_name = 'patients'
    paginate_by = 20

    def get_queryset(self):
        return Patient.objects.all()

    def get_context_data(self, *args, **kwargs):
        context = super(PatientsList, self).get_context_data(*args, **kwargs)
        return context


"""Поиск пациентов по имени"""
class SearchUserList(ListView):

    model = Patient
    template_name = 'nosologies/list_patients.html'
    context_object_name = 'patients'
    paginate_by = 20

    def get_queryset(self):
        return Patient.objects.filter(username=self.request.GET.get("quser"))

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['quser'] = self.request.GET.get("quser")
        return context


"""Вывод информации о пациенте"""
class PatientObserverList(View):
    """Вывод инфлормации о пациэнте"""

    def get(self, request, url):
        user = Patient.objects.get(url=url)
        user_data = Observer.objects.filter(iduser=user)
        list_data = []
        mas = []
        i = 0
        for j, data in enumerate(user_data):
            if i == data.cortege:
               mas.append(data)
            else:
                mas = []
                i = data.cortege
                print(i)
                list_data.append(mas)
        paginator = Paginator(list_data, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'patient': user,
            'page_obj': page_obj
        }
        return render(request, 'nosologies/patient_observer.html', context)