from django.shortcuts import render, redirect
from bs4 import BeautifulSoup
from datetime import datetime
from .models import Rotation, Driver, Arrival, Departure, Hidden, Setting
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import requests

# Global Variables
date_format_str = '%H:%M'
turnArd = datetime.strptime("00:45", date_format_str)
ldg_offset = datetime.strptime("00:05", date_format_str)
now = datetime.now()
current_time = now.strftime("%H:%M")

# UTILITIES
def nullCheck(text):
    if text == "\xa0": return None
    else: return text

def timeConverter(time):
    if time != None: return datetime.strptime(time, date_format_str)
    else: return None

def timeDifference(STD, ETA):
    time_d = STD - ETA
    diff_in_minutes = time_d.total_seconds() / 60
    return diff_in_minutes

def space_remov(FTN):
    if FTN == None: return None
    else:
        FTN = FTN.replace(" ","")
        return FTN
    
def space_remov(FTN):
    if FTN == None: return None
    else:
        FTN = FTN.replace(" ","")
        return FTN


# QUE BACKEND FUCNTIONS
def Que_Arrival(data):
    ETA = timeConverter(data['ETA'])
    data['IOT'] = ETA - ldg_offset
    data['OOT'] = ETA - ldg_offset
    Que_Insert(data)

def Que_Checked(data):
    check = Arrival.objects.get(A_FTNA = data['FTNA'])
    if check.A_CLSD == True: return data['OOT']
    else: return data['IOT']

def Que_Insert(data):

    if not data['FTNA'] == None:

        if not Arrival.objects.filter(A_FTNA = data['FTNA']).exists():
            arrQuery = Arrival(
                A_FTNA = data['FTNA'],
            )
            arrQuery.save()
        
        ARR_FK = Arrival.objects.get(A_FTNA = data['FTNA'])

    else: ARR_FK = None

    if not data['FTND'] == None:

        if not Departure.objects.filter(D_FTND = data['FTND']).exists():
            depQuery = Departure(
                D_FTND = data['FTND'],
            )
            depQuery.save()
        
        DEP_FK = Departure.objects.get(D_FTND = data['FTND'])

    else: DEP_FK = None

    OT_VER = Que_Checked(data)
    
    query = Rotation(
        R_STAND = data['STAND'],
        R_ACREG = data['ACREG'],
        R_FTNA = ARR_FK,
        R_APTA = data['APTA'],
        R_STA = data['STA'],
        R_ETA = data['ETA'],
        R_NA = data['NA'],
        R_RMPAG = data['RMPAG'],
        R_FTND = DEP_FK,
        R_APTD = data['APTD'],
        R_STD = data['STD'],
        R_ETD = data['ETD'],
        R_SLT = data['SLT'],
        R_ND = data['ND'],
        R_AOG = data['AOG'],
        R_OOT = str(data['OOT']),
        R_IOT = str(OT_VER),
    )
    query.save()

def Que_Sorter(STD, ETA, AOG):
    if ETA == None: return STD - turnArd, STD - turnArd
    else:
        time_diff = timeDifference(STD, ETA)
        if time_diff >= 45: return STD - turnArd, ETA - ldg_offset
        else:
            if AOG == False: return ETA - ldg_offset, ETA - ldg_offset
            else:
                # actual_time = timeConverter(current_time)
                actual_time = datetime.strptime("18:43", date_format_str)
                if actual_time >= ETA : return ETA - ldg_offset, ETA - ldg_offset
                else: return STD - turnArd, STD - turnArd

def Que_Main(URL):
    response = requests.get(URL)
    
    # Check if the request was successful (status code 200)
    if response.status_code != 200:
        print(f"Error fetching URL: {response.status_code}")
        return
    

    cont = response.content
    soup = BeautifulSoup(cont, 'lxml')
    flights = soup.find_all('tr')
    i = 0
    for flight in flights:
        data = dict()
        j = 0
        if i > 1:
            infos = flight.find_all('td')
            for info in infos:
                if j == 1: data['STAND'] = nullCheck(info.text)
                if j == 2: data['ACREG'] = nullCheck(info.text)
                if j == 3: 
                    data['FTNA'] = nullCheck(info.text)
                    data['FTNA'] = space_remov(data['FTNA'])
                if j == 4: data['APTA'] = nullCheck(info.text)
                if j == 6: data['STA'] = nullCheck(info.text)
                if j == 7: data['ETA'] = nullCheck(info.text)
                if j == 8: data['NA'] = nullCheck(info.text)
                if j == 10: data['RMPAG'] = nullCheck(info.text)
                if j == 11: 
                    data['FTND'] = nullCheck(info.text)
                    data['FTND'] = space_remov(data['FTND'])
                if j == 12: data['APTD'] = nullCheck(info.text)
                if j == 14: data['STD'] = nullCheck(info.text)
                if j == 15: data['ETD'] = nullCheck(info.text)
                if j == 16: data['SLT'] = nullCheck(info.text)
                if j == 17: data['ND'] = nullCheck(info.text)
                if j == 18: 
                    if info.text == "\xa0": data['AOG'] = False
                    else: data['AOG'] = True
                if j == 20: data['BOF'] = nullCheck(info.text)
                j += 1
                
            # Checks if ACREG is already inserted so it doesn't overwrite it with new data until the previous flight's departed
            if Rotation.objects.filter(R_ACREG = data['ACREG']).exists():
                rot_temp = Rotation.objects.get(R_ACREG = data['ACREG'])
                if rot_temp.R_STA != data['STA'] or rot_temp.R_STD != data['STD']: continue

            # Checks if BOF ain't None
            if data['BOF'] != None:
                if Rotation.objects.filter(R_ACREG = data['ACREG']).exists():
                    Rotation.objects.filter(R_ACREG = data['ACREG']).delete()
                    Arrival.objects.filter(A_FTNA = data['FTNA']).delete()
                    Departure.objects.filter(D_FTND = data['FTND']).delete()
                continue

            # Checks if departure exists
            if data['FTND'] == None: Que_Arrival(data)
            # If it doesn't, it starts to elaborate basic data
            else:
                STD = timeConverter(data['STD'])
                ETA = timeConverter(data['ETA'])
                times = list()
                times = Que_Sorter(STD, ETA, data['AOG'])
                data['OOT'] = times[0]
                data['IOT'] = times[1]
                # Finally, it inserts it in the DB with IOT and OOT. It keeps updating.
                Que_Insert(data)
        i += 1


# RENDER FUNCTIONS

@login_required
def Host_View(request):
    settings = Setting.load()
    URL = settings.S_LINK
    RATE = settings.S_RATE

    Que_Main(URL)

    _rotations = Rotation.objects.all().order_by('R_IOT')
    return render(request, 'Host.html', {'rotations': _rotations, 'refresh_rate': RATE, 'URL': URL})

@login_required
def Ramp_View(request):
    _rotations = Rotation.objects.all().order_by('R_IOT')
    _hidden = Hidden.objects.filter(H_USER = request.user)
    for item in _hidden:
        if item.H_HDDN:
            _rotations = _rotations.exclude(R_FTND=item.H_FTND.D_FTND)

    _drivers_ARR = Driver.objects.all().filter(DR_STAT = True, DR_AREA = "ARR")
    _drivers_DEP = Driver.objects.all().filter(DR_STAT = True, DR_AREA = "DEP")

    hidden_count = _hidden.count()
    
    settings = Setting.load()
    RATE = settings.S_RATE

    return render(request, 'Ramp.html', {
        'rotations': _rotations, 
        'drivers_ARR': _drivers_ARR, 
        'drivers_DEP': _drivers_DEP, 
        'hidden': _hidden, 
        'hidden_count': hidden_count,
        'refresh_rate': RATE
    })

@login_required
def BHS_View(request):
    _rotations = Rotation.objects.all().order_by('R_OOT')
    _drivers = Driver.objects.all().filter(DR_STAT = True, DR_AREA = "DEP")
    _hidden = Hidden.objects.filter(H_USER = request.user)
    for item in _hidden:
        if item.H_HDDN:
            _rotations = _rotations.exclude(R_FTND=item.H_FTND.D_FTND)

    hidden_count = _hidden.count()

    settings = Setting.load()
    RATE = settings.S_RATE

    return render(request, 'BHS.html', {'rotations': _rotations, 'drivers': _drivers, 'hidden': _hidden, 'hidden_count': hidden_count, 'refresh_rate': RATE})

def Manage(request):
    _drivers = Driver.objects.all().order_by('-DR_STAT')
    _hidden = Hidden.objects.filter(H_USER = request.user)

    hidden_count = _hidden.count()
    refresh_rate = None

    return render(request, 'Manage.html', {
        'drivers': _drivers, 
        'hidden': _hidden, 
        'hidden_count': hidden_count,
        'refresh_rate': refresh_rate
    })

def Login_Page(request):
    return render(request, 'Login.html', {})

# DEP/ARR FUNCTIONS
def Close(request, pk):
    if request.method == 'POST':
        _CLSD = request.POST.get('closed')
        _TYPE = request.POST.get('rotation_type')
        if _TYPE == 'A':
            instance = Arrival.objects.get(pk=pk)
            instance.close_arr(_CLSD)
        elif _TYPE == 'D':
            instance = Departure.objects.get(pk=pk)
            instance.close_dep(_CLSD)
    return redirect('Ramp_View')

def Driver_Update(request, pk):
    if request.method == 'POST':
        _DRVR = request.POST.get('sel_driver')
        _TYPE = request.POST.get('rotation_type')
        _FROM = request.POST.get('from')
        if Driver.objects.filter(DR_NAME = _DRVR).exists():
            if _TYPE == 'A':
                if Arrival.objects.filter(A_FTNA=pk).exists() and _DRVR:
                    instance = Arrival.objects.get(pk=pk)
                    instance.driver_update_arr(_DRVR)
                return Driver_Update_Redirect(_FROM)
            elif _TYPE == 'D':
                if Departure.objects.filter(D_FTND=pk).exists() and _DRVR:
                    instance = Departure.objects.get(pk=pk)
                    instance.driver_update_dep(_DRVR)
                return Driver_Update_Redirect(_FROM)
    return Driver_Update_Redirect(_FROM)

def Driver_Update_Redirect(_FROM):
    if _FROM == 'bhs': return redirect('BHS_View')
    else: return redirect('Ramp_View')

def Hide(request, pk):
    query = Hidden(
        H_USER = request.user,
        H_FTND = Departure.objects.get(pk=pk),
        H_NOTE = request.POST.get('notes'),
        H_HDDN = True
    )
    query.save()
    return redirect('Ramp_View')

def Show(request, pk):
    if Hidden.objects.filter(H_FTND = pk).exists():
        Hidden.objects.filter(H_FTND = pk).delete()

    return redirect('Ramp_View')

# DRIVER RELATED FUNCTIONS
def Remove_DRVR(request, pk):
    instance = Driver.objects.get(pk=pk)
    instance.status_update(False)
    return redirect('Manage')

def Add_DRVR(request, pk):
    instance = Driver.objects.get(pk=pk)
    instance.status_update(True)
    return redirect('Manage')

def DRVR_Area_ARR(request, pk):
    instance = Driver.objects.get(pk=pk)
    instance.area_update('ARR')
    return redirect('Manage')

def DRVR_Area_DEP(request, pk):
    instance = Driver.objects.get(pk=pk)
    instance.area_update('DEP')
    return redirect('Manage')


# BHS VIEW RELATED FUNCTIONS
def Bags_Update(request, pk):
    if request.method == 'POST':
        _BAGSN = request.POST.get('bags_nbr')
        _ZONE = request.POST.get('zone')
        instance = Departure.objects.get(pk=pk)

        if _BAGSN: instance.bags_closure_dep(_BAGSN)
        if _ZONE: instance.assign_zone_dep(_ZONE)

        return redirect('BHS_View')
    else: return redirect('BHS_View')

def Sent_Update(request, pk):
    if request.method == 'POST':
        _SENT = request.POST.get('sent')
        instance = Departure.objects.get(pk=pk)
        instance.sent_dep(_SENT)
    return redirect('BHS_View')


# AUTHENTICATION FUNCTIONS
def User_Login(request):
    if request.method == 'POST':
        _USER = request.POST['username']
        _PWD = request.POST['password']

        user = authenticate(request, username = _USER, password = _PWD)

        if user is not None:
            login(request, user)
            return redirect('Ramp_View')
        else:
            return redirect('BHS_View')
    else: return redirect('Manage')

def User_Logout(request):
    logout(request)
    return redirect('Ramp_View')

# SETTINGS RELATED FUNCTIONS
def Edit_Settings(request):
    if request.method == 'POST':
        _URL = request.POST['url']
        _RATE = request.POST['ref_rate']

        query = Setting(
            S_LINK = _URL,
            S_RATE = _RATE
        )
        query.save()

        return redirect('Host_View')
    
    else: return redirect('Host_View')
