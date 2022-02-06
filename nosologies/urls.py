from django.urls import path, include
from .views import *

urlpatterns = [
    # hall page and user pages
    path('', Hall_page, name='hall-page'),
    path('login/', User_Login, name='log-in'),
    path('register/', RegisterNewUser, name='register'),
    path('logout/', UserLogOut, name='log-out'),

    # nosology
    path('nosologies/', NosologyListAll.as_view(), name='n-listall'),
    path('nosologies/search/', SearchNosologyList.as_view(), name='n-search'),
    path('nosologies/add/', AddNosology, name='n-add'),

    # patients
    path('patients/', PatientsList.as_view(), name='p-listall'),
    path('patients/search', SearchUserList.as_view(), name='p-listfew'),

    #data-observer
    path('nosology/<slug:url>', NosologyObserverList.as_view(), name='list-data'),
    path('nosology/download/<int:idnosology>', DownloadFile, name='download'),
    path('nosology/<slug:url>/add', UploadFile, name='create-data'),

    #patient-observer
    path('patient/<slug:url>', PatientObserverList.as_view(), name='patient-observer'),
]