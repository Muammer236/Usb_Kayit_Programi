import json
import tkinter as tk
from tkinter import messagebox

DOSYA_ADI = "usb_kayit.json"

def dosyayi_oku():
    try:
        with open(DOSYA_ADI, "r", encoding="utf-8") as dosya:
            icerik = json.load(dosya)
            return icerik
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def dosyaya_yaz(cihazlar):
    with open(DOSYA_ADI, "w", encoding="utf-8") as dosya:
        json.dump(cihazlar, dosya, ensure_ascii=False, indent=4)

class USBUygulamasi:
    def __init__(self, pencere):
        self.pencere = pencere
        self.pencere.title("USB Cihaz Yöneticisi")
        self.pencere.geometry("400x450")
        self.pencere.configure(padx=20, pady=20)

        self.cihazlar = dosyayi_oku()

        self.lbl_isim = tk.Label(pencere, text="Cihaz Adı:", font=("Arial", 11, "bold"))
        self.lbl_isim.pack(pady=(0, 5))

        self.entry_isim = tk.Entry(pencere, font=("Arial", 12), width=30)
        self.entry_isim.pack(pady=5)

        self.btn_ekle = tk.Button(pencere, text="Cihaz Tak", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), command=self.cihaz_tak)
        self.btn_ekle.pack(pady=5)

        self.lbl_liste = tk.Label(pencere, text="Bağlı Cihazlar", font=("Arial", 11, "bold"))
        self.lbl_liste.pack(pady=(15, 5))

        self.liste_kutusu = tk.Listbox(pencere, font=("Arial", 11), width=40, height=10)
        self.liste_kutusu.pack(pady=5)

        self.btn_cikar = tk.Button(pencere, text="Seçili Cihazı Çıkar", bg="#f44336", fg="white", font=("Arial", 10, "bold"), command=self.cihaz_cikar)
        self.btn_cikar.pack(pady=5)

        self.lbl_durum = tk.Label(pencere, text="", font=("Arial", 10, "italic"))
        self.lbl_durum.pack(pady=10)

        self.listeyi_guncelle()

    def listeyi_guncelle(self):
        self.liste_kutusu.delete(0, tk.END)
        
        if not self.cihazlar:
            self.liste_kutusu.insert(tk.END, "Bağlı cihaz yok.")
            self.liste_kutusu.itemconfig(0, {'fg': 'gray'})
        else:
            for cid, isim in self.cihazlar.items():
                self.liste_kutusu.insert(tk.END, f"{cid} → {isim}")

    def cihaz_tak(self):
        isim = self.entry_isim.get().strip()
        
        if not isim:
            messagebox.showwarning("Uyarı", "Lütfen bir cihaz adı girin!")
            return

        mevcut_numaralar = []
        for cid in self.cihazlar.keys():
            if cid.startswith("USB"):
                try:
                    numara = int(cid[3:])
                    mevcut_numaralar.append(numara)
                except ValueError:
                    continue
        
        yeni_numara = max(mevcut_numaralar) + 1 if mevcut_numaralar else 1
        cihaz_id = f"USB{yeni_numara}"

        self.cihazlar[cihaz_id] = isim
        dosyaya_yaz(self.cihazlar)

        self.entry_isim.delete(0, tk.END)
        self.listeyi_guncelle()
        self.lbl_durum.config(text=f"✔ {isim} takıldı! ID: {cihaz_id}", fg="green")

    def cihaz_cikar(self):
        secim = self.liste_kutusu.curselection()
        
        if not secim:
            messagebox.showwarning("Uyarı", "Lütfen listeden çıkarmak istediğiniz cihazı seçin!")
            return

        secilen_metin = self.liste_kutusu.get(secim[0])
        
        if secilen_metin == "Bağlı cihaz yok.":
            return

        cihaz_id = secilen_metin.split(" → ")[0]

        if cihaz_id in self.cihazlar:
            isim = self.cihazlar[cihaz_id]
            del self.cihazlar[cihaz_id]
            dosyaya_yaz(self.cihazlar)
            
            self.listeyi_guncelle()
            self.lbl_durum.config(text=f"✘ {isim} çıkarıldı!", fg="red")

if __name__ == "__main__":
    pencere = tk.Tk()
    uygulama = USBUygulamasi(pencere)
    pencere.mainloop()