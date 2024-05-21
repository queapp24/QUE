from django.urls import path
from . import views

urlpatterns = [
    path('ramp_view', views.Ramp_View, name="Ramp_View"),
    path('bhs_view', views.BHS_View, name="BHS_View"),
    path('host_view', views.Host_View, name="Host_View"),
    path('login_page', views.Login_Page, name="Login_Page"),
    path('Driver_Update/<str:pk>', views.Driver_Update, name="Driver_Update"),
    path('Close/<str:pk>', views.Close, name="Close"),
    path('Hide/<str:pk>', views.Hide, name="Hide"),
    path('Show/<str:pk>', views.Show, name="Show"),
    path('Bags_Update/<str:pk>', views.Bags_Update, name="Bags_Update"), 
    path('Sent_Update/<str:pk>', views.Sent_Update, name="Sent_Update"), 
    path('manage', views.Manage, name="Manage"),
    path('Remove_DRVR/<str:pk>', views.Remove_DRVR, name="Remove_DRVR"),
    path('Add_DRVR/<str:pk>', views.Add_DRVR, name="Add_DRVR"),
    path('DRVR_Area_ARR/<str:pk>', views.DRVR_Area_ARR, name="DRVR_Area_ARR"),
    path('DRVR_Area_DEP/<str:pk>', views.DRVR_Area_DEP, name="DRVR_Area_DEP"),
    path('User_Login', views.User_Login, name="User_Login"),
    path('User_Logout', views.User_Logout, name="User_Logout"),
]