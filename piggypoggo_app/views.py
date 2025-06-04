from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import *
from django.db.models import Q
from django.db.models import Count, Avg
from datetime import datetime, time
from django.utils.timezone import now
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from .decorators import status_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import openai
from decouple import config

@require_POST
@csrf_exempt
def tanya_ai(request):
    deskripsi = request.POST.get('deskripsi', '').strip()

    if not deskripsi:
        return JsonResponse({'response': 'Deskripsi tidak boleh kosong.'}, status=400)

    try:
        client = openai.OpenAI(
            api_key=f"{config('llama_3_api_key')}",
            base_url="https://api.groq.com/openai/v1"
        )

        response = client.chat.completions.create(
            model="llama3-70b-8192",
            # messages=[
            #     {"role": "system", "content": "Kamu adalah seorang dokter hewan ahli babi."},
            #     {"role": "user", "content": f"Babi saya mengalami: {deskripsi}. Apa diagnosis dan saran pengobatannya? Jawab se-simpel mungkin."}
            # ],
            messages=[
                {"role": "system", "content": "Kamu adalah seorang dokter hewan ahli babi lalu memiliki humor yang bagus."},
                {"role": "user", "content": f"{deskripsi}."}
            ],
            temperature=0.7
        )

        ai_reply = response.choices[0].message.content.strip()
        return JsonResponse({'response': ai_reply})

    except Exception as e:
        return JsonResponse({'response': f'Error dari AI: {str(e)}'}, status=500)


def format_number(value):
    try:
        value = int(value)
        return "{:,}".format(value).replace(",", ".")
    except:
        return value
    
def auth(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard') 
        else:
            messages.error(request, "Username atau password salah!")
            return redirect('auth') 
    return render(request, 'auth.html')

@login_required
@status_required([1, 2])
def logoutfunc(request):
    logout(request)
    return redirect('auth')

@login_required
@status_required([1, 2])
def dashboard(request):
    user_profile = UserProfile.objects.get(user=request.user)
    all_riwayats = Riwayat.objects.all().order_by('-pk')
    paginator = Paginator(all_riwayats, 5)
    all_kandang_count = Kandang.objects.all().count()
    all_babi_count = Babi.objects.filter(terjual=False).count()
    babi_per_kandang = Kandang.objects.annotate(babi_count=Count('babi'))
    average_babi_per_kandang = babi_per_kandang.aggregate(avg=Avg('babi_count'))['avg'] or 0

    omset_full = Nota.objects.all().aggregate(total_semua=Sum('total_harga'))['total_semua'] or 0
    omset_full = format_number(omset_full)

    daily = Daily.objects.filter(user=user_profile).first()
    dailies = DailyDetail.objects.filter(daily=daily)

    if request.method == 'POST':
        check_id = request.POST.get('daily')

        daily_detail = DailyDetail.objects.get(pk=check_id)
        daily_detail.last_check = date.today()    
        daily_detail.save()

        return redirect('dashboard')  

    context = {
        'on': 'utama',
        'all_riwayats': paginator.get_page(1),
        'all_kandang_count': all_kandang_count,
        'all_babi_count': all_babi_count,
        'average_babi_per_kandang': round(average_babi_per_kandang, 2),
        'omset_full': omset_full,
        'dailies': dailies,
    }
    return render(request, 'dashboard.html', context)

@login_required
@status_required([1, 2])
def daily_check(request, dailydetail_pk):
    daily_detail = DailyDetail.objects.get(pk=dailydetail_pk)
    daily_detail.last_check(date.today())
    daily_detail.save()
    return redirect('dashboard')

@login_required
@status_required([1, 2])
def riwayat(request):
    filter_option = request.GET.get('filter', 'semua')
    all_riwayats = Riwayat.objects.all()

    if filter_option == 'hari_ini':
        from django.utils.timezone import now
        today = now().date()
        all_riwayats = all_riwayats.filter(tanggal__date=today)
    elif filter_option == 'minggu_ini':
        from django.utils.timezone import now
        from datetime import timedelta
        today = now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        all_riwayats = all_riwayats.filter(tanggal__date__range=(start_of_week, end_of_week))
    elif filter_option == 'bulan_ini':
        from django.utils.timezone import now
        today = now().date()
        all_riwayats = all_riwayats.filter(tanggal__year=today.year, tanggal__month=today.month)

    all_riwayats = all_riwayats.order_by('-tanggal')

    paginator = Paginator(all_riwayats, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'filter': filter_option,
    }
    return render(request, 'riwayat.html', context)


@login_required
@status_required([1, 2])
def kandang(request):
    all_kandangs = Kandang.objects.all()

    for kandang in all_kandangs:
        count = 0
        all_babis = Babi.objects.filter(kandang=kandang)
        count += all_babis.count()
        kandang.banyaknya_babi = count
        
    context = {
        'on': 'kandang',
        'all_kandangs': all_kandangs,
    }
    return render(request, 'kandang.html', context)

@login_required
@status_required([1, 2])
def tambahKandang(request):
    all_babis = Babi.objects.filter(kandang=None, terjual=False)

    if request.method == 'POST':
        nomor_kandang = request.POST.get('nomor_kandang')
        babi = request.POST.getlist('babi')

        if Kandang.objects.filter(nomor_kandang=nomor_kandang).exists():
            messages.error(request, f'Kandang dengan nomor "{nomor_kandang}" sudah ada!')
        else:
            kandang = Kandang.objects.create(nomor_kandang=nomor_kandang)
            riwayat = Riwayat.objects.create(riwayat=f'Membuat kandang {kandang.nomor_kandang}')
            messages.success(request, f'Sukses membuat kandang dengan nomor {nomor_kandang}')
        
        return redirect('kandang')
    
    context = {
        'on': 'kandang',
        'all_babis': all_babis,
    }
    return render(request, 'tambah-kandang.html', context)

@login_required
@status_required([1, 2])
def editKandang(request, kandang_pk):
    kandang = Kandang.objects.get(pk=kandang_pk)
    all_babis = Babi.objects.filter(Q(terjual=False) & (Q(kandang=None) | Q(kandang=kandang)))

    if request.method == 'POST':
        nomor_kandang = request.POST.get('nomor_kandang')
        selected_babis = list(map(int, request.POST.getlist('babi')))
        kandang_validation = Kandang.objects.filter(nomor_kandang=nomor_kandang).first()

        if kandang == kandang_validation or not kandang_validation:
            riwayat = Riwayat.objects.create(riwayat=f'Mengedit kandang {kandang.nomor_kandang} -> {nomor_kandang}')
            for babi in all_babis:
                if babi.pk in selected_babis:
                    babi.kandang = kandang
                else:
                    babi.kandang = None
                babi.save()

            kandang.nomor_kandang = nomor_kandang
            kandang.save()

            messages.success(request, f'Sukses mengedit kandang dengan nomor {nomor_kandang}')
        else:
            messages.error(request, f'Kandang dengan nomor "{nomor_kandang}" sudah ada!')
        
        return redirect('kandang')
    
    context = {
        'on': 'kandang',
        'kandang': kandang,
        'all_babis': all_babis
    }
    return render(request, 'edit-kandang.html', context)

@login_required
@status_required([1, 2])
def hapusKandang(request, kandang_pk):
    kandang = Kandang.objects.get(pk=kandang_pk)
    new_riwayat = Riwayat.objects.create(riwayat=f'Menghapus kandang {kandang}')
    messages.success(request, f'Sukses menghapus kandang dengan nomor {kandang}')
    kandang.delete()

    return redirect('kandang')

@login_required
@status_required([1, 2])
def babi(request):
    today = now().date()
    current_month = today.month
    current_year = today.year

    all_babis = Babi.objects.all().order_by('-pk')

    for babi in all_babis:
        laporans = Laporan.objects.filter(babi=babi)

        babi.bb_rata_rata = 0
        babi.bb_bulan_ini = 0
        babi.harga_bulan_ini = 0

        if laporans:
            babi.bb_bulan_ini = laporans.last().berat_badan
            babi.harga_bulan_ini = format_number(babi.harga)

            for laporan in laporans:
                babi.bb_rata_rata += laporan.berat_badan

            if babi.bb_rata_rata != 0:
                babi.bb_rata_rata = babi.bb_rata_rata / laporans.count() 

        last_laporan = (
            Laporan.objects.filter(babi=babi)
            .order_by('-tanggal')
            .first()
        )

        if not last_laporan or last_laporan.tanggal.month != current_month or last_laporan.tanggal.year != current_year:
            last_laporan = Laporan.objects.create(
                babi=babi,
                tanggal=now(),
                berat_badan=0,
                obat=False
            )
        
        if last_laporan.obat == False or last_laporan.berat_badan == 0 or laporan.babi.harga == 0:
            babi.status = 'Belum'
        else:
            babi.status = 'Sudah'

        babi.last_laporan = last_laporan

    context = {
        'on': 'babi',
        'all_babis': all_babis,
    }
    return render(request, 'babi.html', context)

@login_required
@status_required([1, 2])
def editBabi(request, babi_pk):
    all_kandangs = Kandang.objects.annotate(jumlah_babi=Count('babi')).filter(
        Q(jumlah_babi__lt=6) | Q(pk=babi.kandang.pk)
    )
    babi = Babi.objects.get(pk=babi_pk)

    if request.method == 'POST':
        nama_babi = request.POST.get('nama_babi')
        pk_kandang = request.POST.get('pk_kandang')
        kandang = Kandang.objects.get(pk=pk_kandang)

        babi.nama_babi = nama_babi
        babi.kandang = kandang

        babi.save()

        messages.success(request, f'Babi dengan nama "{babi.nama_babi}" berhasil di edit!')
        return redirect('babi')

    context = {
        'on': 'babi',
        'babi': babi,
        'all_kandangs': all_kandangs,
    }
    return render(request, 'edit-babi.html', context)

@login_required
@status_required([1, 2])
def tambahBabi(request):
    all_kandangs = Kandang.objects.annotate(jumlah_babi=Count('babi')).filter(jumlah_babi__lt=6)

    if request.method == 'POST':
        nama_babi = request.POST.get('nama_babi')
        pk_kandang = request.POST.get('pk_kandang')

        if Babi.objects.filter(nama_babi=nama_babi.strip()).exists():
            messages.error(request, f'Babi dengan nama "{nama_babi}" sudah ada!')
        else:
            kandang = None
            if pk_kandang != '-':
                kandang = Kandang.objects.get(pk=pk_kandang)
            babi = Babi.objects.create(nama_babi=nama_babi.strip(), kandang=kandang)
            messages.success(request, f'Babi dengan nama "{babi.nama_babi}" berhasil di tambah!')
            riwayat = Riwayat.objects.create(riwayat=f'Berhasil menambah babi {babi.nama_babi}')

        return redirect('babi')
    context = {
        'on': 'babi',
        'all_kandangs': all_kandangs,
    }
    return render(request, 'tambah-babi.html', context)

@login_required
@status_required([1, 2])
def editLaporan(request, laporan_pk):
    laporan = Laporan.objects.get(pk=laporan_pk)
    babi = laporan.babi
    all_kandangs = Kandang.objects.all()

    babi.harga_format = format_number(babi.harga)
    status = 'Sudah'
    if laporan.obat == False or laporan.berat_badan == 0 or babi.harga == 0:
        status = 'Belum'

    if request.method == 'POST':
        if request.POST.get('submit_type') == 'babi':
            nama_babi = request.POST.get('nama_babi')
            pk_kandang = request.POST.get('pk_kandang')
            if pk_kandang == '-':
                babi.kandang = None
            else:
                kandang = Kandang.objects.get(pk=pk_kandang)
                babi.kandang = kandang

            babi.nama_babi = nama_babi
            babi.save()

        elif request.POST.get('submit_type') == 'laporan':
            berat_badan = request.POST.get('berat_badan_babi')
            obat = request.POST.get('obat')
            harga = request.POST.get('harga_babi')
            harga = harga.replace('.', '')
            harga = int(harga)
            status_kesehatan = request.POST.get('kesehatan')

            laporan.berat_badan = berat_badan
            babi.harga = harga

            if obat == '1':
                laporan.obat = True
            elif obat == '2':
                laporan.obat = False

            if status_kesehatan == '1':
                babi.sakit = False
            elif status_kesehatan == '2':
                babi.sakit = True

            laporan.save()
            babi.save()

        return redirect('edit-laporan', laporan_pk=laporan_pk)

    context = {
        'on': 'babi',
        'laporan': laporan,
        'babi': babi,
        'all_kandangs': all_kandangs,
        'status': status,
    }
    return render(request, 'edit-laporan.html', context)

@login_required
@status_required([1, 2])
def transaksi(request):
    all_notas = Nota.objects.all().order_by('-pk')
    babi_terjual_count = Babi.objects.filter(terjual=True).count()


    today = now().date()
    omset_bulan_ini = Nota.objects.filter(
        tanggal_nota__year=today.year,
        tanggal_nota__month=today.month
    ).aggregate(total_bulan_ini=Sum('total_harga'))['total_bulan_ini'] or 0

    omset_tahun_ini = Nota.objects.filter(
        tanggal_nota__year=today.year,
    ).aggregate(total_tahun_ini=Sum('total_harga'))['total_tahun_ini'] or 0

    omset_bulan_ini = format_number(omset_bulan_ini)
    omset_tahun_ini = format_number(omset_tahun_ini)

    pengingat = Nota.objects.filter(tanggal_dibeli__gte=today)
    mulai = 'Hari ini'
    hingga = 'Hari ini'

    if request.method == 'POST':
        mulai = request.POST.get('mulai-dari')  
        hingga = request.POST.get('hingga-dari') 

        if mulai and hingga:
            mulai_datetime = datetime.combine(datetime.strptime(mulai, '%Y-%m-%d'), time.min)
            hingga_datetime = datetime.combine(datetime.strptime(hingga, '%Y-%m-%d'), time.max)

            all_notas = Nota.objects.filter(tanggal_nota__range=[mulai_datetime, hingga_datetime]).order_by('-pk')
        else:
            all_notas = Nota.objects.all().order_by('-pk')

    for nota in all_notas:
        nota.formatted_total_harga = format_number(nota.total_harga)
    
    context = {
        'on': 'transaksi',
        'all_notas': all_notas,
        'babi_terjual_count': babi_terjual_count,
        'omset_bulan_ini': omset_bulan_ini,
        'omset_tahun_ini': omset_tahun_ini,
        'pengingat': pengingat,
        'mulai': mulai,
        'hingga': hingga,
    }
    return render(request, 'transaksi.html', context)

@login_required
@status_required([1, 2])
def tambahTransaksi(request):
    all_babis = Babi.objects.filter(terjual=False, sakit=False).exclude(harga=0)

    for babi in all_babis:
        babi.formatted_harga = format_number(babi.harga)

    if request.method == 'POST':
        nama_pembeli = request.POST.get('nama_pembeli')
        total_harga = request.POST.get('total_harga')
        total_harga = total_harga.replace('.', '')
        total_harga = int(total_harga)
        all_babis = request.POST.getlist('babi')
        tanggal_dibeli = request.POST.get('tanggal')

        new_nota = Nota.objects.create(nama_pembeli=nama_pembeli, total_harga=total_harga, tanggal_nota=timezone.now())
        new_nota.kode_nota = f'N{new_nota.pk}'
        
        if tanggal_dibeli:
            new_nota.tanggal_dibeli = tanggal_dibeli
        
        new_nota.save()

        for babi in all_babis:
            babi = Babi.objects.get(pk=babi)
            new_dnota = DetailNota.objects.create(babi=babi, harga=babi.harga, nota=new_nota)
            babi.kandang = None
            babi.terjual = True
            babi.save()

        messages.success(request, f'Sukses membuat nota {new_nota.kode_nota}')
        return redirect('transaksi')
    
    context = {
        'on': 'transaksi',
        'all_babis': all_babis,
    }
    return render(request, 'tambah-transaksi.html', context)
