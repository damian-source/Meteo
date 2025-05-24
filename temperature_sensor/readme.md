# Instalacja MicroPython na Seeed Studio XIAO ESP32-C3 (ESP32-C3)

## 🧰 Wymagania wstępne

- Płytka: Seeed Studio XIAO ESP32-C3
- Kabel USB-C (przesyłający dane)
- System operacyjny: Ubuntu Linux
- Zainstalowany Python 3
- Narzędzie `esptool.py`

Instalacja `esptool`:
```bash
pip install esptool
```

---

## 📥 Krok 1: Pobranie firmware MicroPython

Pobierz firmware dla ESP32-C3 ze strony:

👉 [https://micropython.org/download/ESP32_GENERIC_C3/](https://micropython.org/download/ESP32_GENERIC_C3/)

W tym przypadku użyta została wersja:
```
ESP32_GENERIC_C3-20250415-v1.25.0.bin
```

---

## 🔌 Krok 2: Podłączenie płytki i identyfikacja portu

1. Podłącz płytkę XIAO ESP32-C3 do portu USB.
2. W terminalu sprawdź, na jakim porcie została wykryta:

```bash
sudo dmesg | grep tty
```

Oczekiwany wynik:

```
[ 1967.318839] cdc_acm 2-1:1.0: ttyACM0: USB ACM device
```

Co oznacza, że płytka dostępna jest jako port: `/dev/ttyACM0`

---

## 🧹 Krok 3: Wymazanie pamięci flash

Przed wgraniem MicroPython należy wyczyścić pamięć flash:

```bash
esptool.py --chip esp32c3 --port /dev/ttyACM0 erase_flash
```

---

## 🔥 Krok 4: Wgranie MicroPython

Po wymazaniu pamięci, wgraj pobrany firmware:

```bash
esptool.py --chip esp32c3 --port /dev/ttyACM0 --baud 460800 write_flash -z 0x0 ESP32_GENERIC_C3-20250415-v1.25.0.bin
```

---

## 🧪 Krok 5: Test działania MicroPython

Po zakończonym flashowaniu można sprawdzić działanie MicroPythona za pomocą terminala:

```bash
screen /dev/ttyACM0 115200
```

Jeśli pojawi się znak zachęty `>>>`, wszystko działa poprawnie.
Jeżeli pojawi się czarny ekran naciśnij CTRL+D a następnie CTRL+B.
Można ewentualnie spróbować Enter, CTRL+C lub Backspace.
Żeby wyjść z konsoli MicroPython naciśnij CTRL+A a następnie k.

---

## 💡 (Opcjonalnie) Krok 6: Użycie Thonny IDE

Thonny to prosty edytor wspierający MicroPython:

### Instalacja:

```bash
sudo apt install thonny
```

### Konfiguracja:

- Interpreter: **MicroPython (ESP32)**
- Port: `/dev/ttyACM0`

---

## ✅ Gotowe!

Płytka XIAO ESP32-C3 działa teraz z MicroPythonem i jest gotowa do dalszego programowania.
