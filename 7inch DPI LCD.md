# 📘 Waveshare 7inch DPI LCD – Instrukcja obsługi

## 🖼️ Wprowadzenie

7-calowy ekran IPS o rozdzielczości 1024×600, przeznaczony do współpracy z Raspberry Pi. Wykorzystuje interfejs DPI (bez funkcji dotykowej).

## ✨ Cechy

- 7-calowy ekran IPS, rozdzielczość sprzętowa 1024×600.
- Projekt oparty o 40-pinowe złącze GPIO Raspberry Pi.
- Obsługuje systemy Raspberry Pi OS oraz Ubuntu.
- Sterowanie podświetleniem – zmniejszenie zużycia energii.
- Kompaktowe rozmiary, idealny do wielu projektów.

> **Uwaga**: Ekran służy tylko do wyświetlania. Jeśli potrzebujesz funkcji dotykowej, wybierz model **7inch HDMI LCD(C)** (pojemnościowy) lub **7inch HDMI LCD (rezystancyjny)**.

## ⚙️ Praca z Raspberry Pi

### 🔌 Połączenia sprzętowe

1. Podłącz RGB LCD HAT do gniazda JP1 na adapterze RGB 50P TO 40/50P za pomocą białego kabla FFC.
2. Podłącz złoty kabel FPC z wyświetlacza do gniazda JP2 na adapterze.

> **Uwaga:** Przed podłączeniem otwórz czarny zatrzask, włóż przewód i zamknij zatrzask.

### 💻 Ustawienia programowe

#### 📂 Raspberry Pi OS – Bookworm/Bullseye

1. Pobierz obraz systemu z oficjalnej strony Raspberry Pi.
2. Rozpakuj obraz `.img`.
3. Sformatuj kartę TF za pomocą SDFormatter.
4. Nagraj obraz systemu przy pomocy Win32DiskImager.
5. W pliku `config.txt` dopisz na końcu:

```
dtoverlay=vc4-kms-v3d
dtoverlay=vc4-kms-DPI-7inch
dtoverlay=waveshare-7dpi
```

6. Umieść dwa pliki `.dtbo` w katalogu `/boot/overlays`.
7. Włącz podświetlenie LCD.
8. Uruchom Raspberry Pi.

#### 📂 Raspberry Pi OS – Buster / Ubuntu

1. W pliku `config.txt` dopisz:

```
[pi4]
dpi_timings=1024 1 40 48 128 600 1 13 3 45 0 0 0 60 0 37000000 6

[all]
dtoverlay=dpi24
enable_dpi_lcd=1
display_default_lcd=1
dpi_group=2
dpi_mode=87
dpi_output_format=0x6f005
hdmi_cvt 1024 600 60 6 0 0 0
disable_overscan=1
```

2. Włącz podświetlenie LCD.
3. Uruchom Raspberry Pi.

> **Uwaga:** W przypadku problemów z wyświetlaniem spróbuj dostosować napięcie VCOM.

## 🧠 O systemie Raspberry Pi OS

Od 2 grudnia 2021 r. Raspberry Pi OS został podzielony na dwie wersje:

- **Buster**: starsza, stabilniejsza, domyślnie używa raspicam.
- **Bullseye**: nowsza, z domyślnym sterownikiem KMS i libcamera.

## 📚 Zasoby

- **Dokumentacja**:
  - Schemat RGB LCD HAT
  - Schemat złącza płaskiego
  - Karta katalogowa wyświetlacza 1024×600

- **Oprogramowanie**:
  - Panasonic SDFormatter
  - Win32DiskImager
  - PuTTY

- **Serie poradników**:
  - Raspberry Pi Tutorial Series

## ❓ FAQ

### Jak usunąć kolorowe kwadraty GPU przy starcie?
Dodaj do `config.txt`:
```
disable_splash=1
```

### Jak zmienić logo startowe Raspberry Pi?
Zamień plik `/usr/share/plymouth/themes/pix/splash.png` na własne logo.

### Jaki jest prąd pracy 7inch DPI LCD?
- Podświetlenie włączone: ok. 450 mA
- Podświetlenie wyłączone: ok. 60 mA

### Jak ustawić długie naciśnięcie jako kliknięcie prawym przyciskiem?
Obsługiwane modele: ekran DSI, DPI i HDMI z dotykiem pojemnościowym.

Instalacja:
```
wget https://files.waveshare.com/upload/1/18/Evdev-right-click-emulation.zip
unzip Evdev-right-click-emulation.zip
cd evdev-right-click-emulation
sudo apt install build-essential libevdev2 libevdev-dev
sudo cp out/evdev-rce /usr/local/bin/
sudo chmod +x /usr/local/bin/evdev-rce
```

Uruchomienie:
```
sudo evdev-rce
```

Ustawienia autostartu:
```
sudo mkdir ~/.config/autostart
sudo nano ~/.config/autostart/right_click.desktop
```

Treść pliku:
```
[Desktop Entry]
Version=1.0
Type=Application
Name=evdev-rce
GenericName=Enable long-press-to-right-click gesture
Exec=env LONG_CLICK_INTERVAL=1000 LONG_CLICK_FUZZ=200 /usr/local/bin/evdev-rce
Terminal=true
StartupNotify=false
```

### Jaka jest częstotliwość odświeżania?
60 Hz

### Czy ekran przechodzi automatycznie w tryb uśpienia?
Zależy od systemu. Raspberry Pi OS domyślnie przechodzi w uśpienie po około 10 minutach.

### Czy ekran obsługuje regulację jasności przez PWM?
Nie.

---

© Waveshare.com | Tłumaczenie: Damian Urbański
