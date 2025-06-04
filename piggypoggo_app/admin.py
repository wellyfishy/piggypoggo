from django.contrib import admin
from .models import *

admin.site.register(UserProfile)
admin.site.register(Kandang)
admin.site.register(Babi)
admin.site.register(Riwayat)
admin.site.register(Laporan)
admin.site.register(Nota)
admin.site.register(DetailNota)
admin.site.register(Daily)
admin.site.register(DailyDetail)