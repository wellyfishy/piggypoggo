from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q, CheckConstraint
from datetime import date, timedelta
from django.utils.timezone import now

class UserProfile(models.Model):
    LEVEL_USER = [
        (1, "Operator"),
        (2, "Admin"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    level = models.IntegerField(choices=LEVEL_USER, default=1)

    def __str__(self):
        return f"{self.user.username} - {self.get_level_display()}"
    
class Daily(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.user}'
    
class DailyDetail(models.Model):
    daily = models.ForeignKey(Daily, null=True, blank=True, on_delete=models.CASCADE)
    nama_daily = models.CharField(max_length=50, null=True, blank=True)
    last_check = models.DateField()

    def __str__(self):
        return f'{self.daily} - {self.nama_daily}'
    
    @property
    def get_status(self):
        if self.last_check < date.today():
            return "Belum"
        else:
            return "Sudah"

class Kandang(models.Model):
    nomor_kandang = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.nomor_kandang}'
    
class Babi(models.Model):
    nama_babi = models.CharField(max_length=50, null=True, blank=True)
    kandang = models.ForeignKey(Kandang, null=True, blank=True, on_delete=models.SET_NULL)
    terjual = models.BooleanField(default=False)
    harga = models.IntegerField(default=0)
    sakit = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.nama_babi}'
    
class Riwayat(models.Model):
    riwayat = models.TextField(null=True, blank=True)
    tanggal = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.riwayat}'

class Laporan(models.Model):
    babi = models.ForeignKey(Babi, on_delete=models.CASCADE, null=True, blank=True)
    tanggal = models.DateTimeField(null=True, blank=True)
    berat_badan = models.CharField(max_length=10, null=True, blank=True)
    obat = models.BooleanField(default=False)
    foto_babi = models.ImageField(upload_to='foto_babi/', blank=True, null=True)

    def __str__(self):
        return f'{self.babi}'
    
class ToDo(models.Model):
    TIPE = [
        ('1', 'Harian'),
        ('2', 'Mingguan'),
        ('3', 'Bulanan')
    ]

    todo = models.CharField(max_length=50, null=True, blank=True)
    tipe = models.CharField(max_length=10, null=True, blank=True, choices=TIPE)
    last_reset = models.DateField(auto_now_add=True)

    def get_status(self):
        today = date.today()
        
        if self.tipe == '1': 
            return 'Sudah' if self.last_reset == today else 'Belum'
        
        elif self.tipe == '2':  
            monday = today - timedelta(days=today.weekday())
            return 'Sudah' if self.last_reset >= monday else 'Belum'

        elif self.tipe == '3':  
            first_of_month = today.replace(day=1)
            return 'Sudah' if self.last_reset >= first_of_month else 'Belum'
        
        return 'Tidak diketahui'
    
class Nota(models.Model):
    kode_nota = models.CharField(unique=True, blank=True, null=True, max_length=10)
    nama_pembeli = models.CharField(max_length=50, null=True, blank=True)
    total_harga = models.IntegerField(null=True, blank=True)
    tanggal_nota = models.DateTimeField(null=True, blank=True)
    tanggal_dibeli = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.pk}'
    
class DetailNota(models.Model):
    babi = models.ForeignKey(Babi, null=True, blank=True, on_delete=models.SET_NULL)
    harga = models.IntegerField(null=True, blank=True)
    nota = models.ForeignKey(Nota, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.babi} - {self.nota}'