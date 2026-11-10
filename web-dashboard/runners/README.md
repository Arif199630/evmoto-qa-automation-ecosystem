# Standalone Test Runners (Modul 01 - 25)

Folder ini berisi runner satuan untuk masing-masing modul pengujian (01 s/d 25) yang memanggil test suite di folder \	ests/\.

## Cara Eksekusi

### Dari Root Project:
\\ash
python runners/01_halaman_login.py
python runners/02_beranda.py
python runners/10_vehicle_management.py
\
### Dari Folder runners/:
\\ash
cd runners
python 01_halaman_login.py
\
### Menjalankan Semua Test Sekaligus:
Gunakan runner utama di root project:
\\ash
python main_runner.py
\