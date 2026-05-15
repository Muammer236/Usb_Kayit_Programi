import json
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import os
import string
from plyer import notification 

DOSYA_ADI = "usb_kayit.json"

def dosyayi_oku():
    try:
        with open(DOSYA_ADI, "r", encoding="utf-8") as dosya:
            return json.load(dosya)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def dosyaya_yaz(cihazlar):
    with open(DOSYA_ADI, "w", encoding="utf-8") as dosya:
        json.dump(cihazlar, dosya, ensure_ascii=False, indent=4)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class USBUygulamasi:
    def __init__(self, pencere):
        self.pencere = pencere 
        self.pencere.title("USB Bağlantı Monitörü")
        self.pencere.geometry("450x550")
        self.pencere.configure(padx=20, pady=20)

        self.cihazlar = dosyayi_oku()
        self.mevcut_suruculer = self.aktif_suruculeri_bul()

        # Arayüz Elemanları
        self.lbl_isim = ctk.CTkLabel(pencere, text="Manuel Cihaz Adı:", font=("Arial", 14, "bold"))
        self.lbl_isim.pack(pady=(0, 5))

        self.entry_isim = ctk.CTkEntry(pencere, font=("Arial", 14), width=300, placeholder_text="Örn: Bellek")
        self.entry_isim.pack(pady=5)

        self.btn_ekle = ctk.CTkButton(pencere, text="Cihaz Tak (Manuel)", fg_color="#2FA572", command=self.cihaz_tak)
        self.btn_ekle.pack(pady=10)

        self.lbl_liste = ctk.CTkLabel(pencere, text="Aktif Bağlantılar", font=("Arial", 14, "bold"))
        self.lbl_liste.pack(pady=(15, 5))

        self.liste_kutusu = tk.Listbox(pencere, font=("Consolas", 12), width=45, height=8, bg="#2b2b2b", fg="white", borderwidth=0)
        self.liste_kutusu.pack(pady=5)

        self.btn_cikar = ctk.CTkButton(pencere, text="Seçili Cihazı Çıkar", fg_color="#E74C3C", command=self.cihaz_cikar)
        self.btn_cikar.pack(pady=10)

        self.lbl_durum = ctk.CTkLabel(pencere, text="Sistem dinleniyor...", font=("Arial", 12, "italic"), text_color="gray")
        self.lbl_durum.pack(pady=10)

        self.listeyi_guncelle()
        self.pencere.after(2000, self.gercek_usb_dinle)

    def aktif_suruculeri_bul(self):
        suruculer = set()
        if os.name == 'nt':
            for harf in string.ascii_uppercase:
                surucu = f"{harf}:\\"
                if os.path.exists(surucu):
                    suruculer.add(surucu)
        return suruculer

    def gercek_usb_dinle(self):
        guncel_suruculer = self.aktif_suruculeri_bul()
        yeni_takilanlar = guncel_suruculer - self.mevcut_suruculer
        cikarilanlar = self.mevcut_suruculer - guncel_suruculer

        for surucu in yeni_takilanlar:
            isim = f"Fiziksel Disk ({surucu})"
            self.otomatik_ekle(isim)
            # Plyer bildirimi
            notification.notify(
                title="USB Takıldı!",
                message=f"Yeni cihaz algılandı: {surucu}",
                timeout=5
            )
            
        for surucu in cikarilanlar:
            isim = f"Fiziksel Disk ({surucu})"
            self.otomatik_cikar(isim)
            # Plyer bildirimi
            notification.notify(
                title="USB Çıkarıldı!",
                message=f"Cihaz bağlantısı kesildi: {surucu}",
                timeout=5
            )

        self.mevcut_suruculer = guncel_suruculer
        self.pencere.after(2000, self.gercek_usb_dinle)

    def otomatik_ekle(self, isim):
        cihaz_id = self.yeni_id_olustur()
        self.cihazlar[cihaz_id] = isim
        dosyaya_yaz(self.cihazlar)
        self.listeyi_guncelle()
        self.lbl_durum.configure(text=f"[+] Donanım Algılandı: {isim}", text_color="#2FA572")

    def otomatik_cikar(self, isim):
        silinecek_id = None
        for cid, cihaz_adi in self.cihazlar.items():
            if cihaz_adi == isim:
                silinecek_id = cid
                break
        if silinecek_id:
            del self.cihazlar[silinecek_id]
            dosyaya_yaz(self.cihazlar)
            self.listeyi_guncelle()
            self.lbl_durum.configure(text=f"[-] Donanım Çıkarıldı: {isim}", text_color="#E74C3C")

    def yeni_id_olustur(self):
        mevcut_numaralar = [int(cid[3:]) for cid in self.cihazlar.keys() if cid.startswith("USB") and cid[3:].isdigit()]
        return f"USB{max(mevcut_numaralar) + 1 if mevcut_numaralar else 1}"

    def listeyi_guncelle(self):
        self.liste_kutusu.delete(0, tk.END)
        if not self.cihazlar:
            self.liste_kutusu.insert(tk.END, "Aktif bağlantı yok.")
        else:
            for cid, isim in self.cihazlar.items():
                self.liste_kutusu.insert(tk.END, f" {cid} | {isim}")

    def cihaz_tak(self):
        isim = self.entry_isim.get().strip()
        if not isim: return
        cihaz_id = self.yeni_id_olustur()
        self.cihazlar[cihaz_id] = isim
        dosyaya_yaz(self.cihazlar)
        self.entry_isim.delete(0, tk.END)
        self.listeyi_guncelle()

    def cihaz_cikar(self):
        secim = self.liste_kutusu.curselection()
        if not secim: return
        secilen_metin = self.liste_kutusu.get(secim[0])
        if "USB" not in secilen_metin: return
        cihaz_id = secilen_metin.split(" | ")[0].strip()
        if cihaz_id in self.cihazlar:
            del self.cihazlar[cihaz_id]
            dosyaya_yaz(self.cihazlar)
            self.listeyi_guncelle()

if __name__ == "__main__":
    pencere = ctk.CTk()
    uygulama = USBUygulamasi(pencere)
    pencere.mainloop()
