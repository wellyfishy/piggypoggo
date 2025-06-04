from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('tanya-ai/', views.tanya_ai, name='tanya_ai'),
    path('', views.auth, name="auth"),
    path('logout', views.logoutfunc, name="logout"),
    path('dashboard', views.dashboard, name="dashboard"),
    path('dashboard/riwayat', views.riwayat, name="riwayat"),
    path('kandang', views.kandang, name="kandang"),
    path('kandang/tambah', views.tambahKandang, name="tambah-kandang"),
    path('kandang/<int:kandang_pk>/edit/', views.editKandang, name="edit-kandang"),
    path('kandang/<int:kandang_pk>/hapus/', views.hapusKandang, name="hapus-kandang"),
    path('babi', views.babi, name="babi"),
    path('babi/tambah', views.tambahBabi, name="tambah-babi"),
    path('babi/<int:babi_pk>/edit/', views.editBabi, name="edit-babi"),
    path('laporan/<int:laporan_pk>/edit/', views.editLaporan, name="edit-laporan"),
    path('transaksi', views.transaksi, name="transaksi"),
    path('transaksi/tambah', views.tambahTransaksi, name="tambah-transaksi"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
