import pygame
import sys
import requests
from datetime import datetime, timedelta
import asyncio
from bleak import BleakScanner
import serial

# ---------- Pygame Setup ----------
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Zegar + Pogoda + BLE")
pygame.mouse.set_visible(False)

# ---------- mail detector setup ----------
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
mailDetected = False
mailError = False
last_lora = datetime.now()

WHITE = (120, 120, 120)
DATE_COLOR = (0, 180, 0)
BLACK = (0, 0, 0)
font = pygame.font.SysFont("Arial", 180)
date_font = pygame.font.SysFont("Arial", 120)
temp_font = pygame.font.SysFont("Arial", 100)
small_font = pygame.font.SysFont("Arial", 40)

clock = pygame.time.Clock()
miasto = "Lodz"

# ---------- Ikony pogody ----------
ikony_day = {
    "Clear": "sunny.png",
    "Cloudy": "cloudy.png",
    "Fog": "haze_fog_dust_smoke.png",
    "Haze": "haze_fog_dust_smoke.png",
    "Heavy rain": "heavy_rain.png",
    "Heavy rain at times": "heavy_rain.png",
    "Light drizzle": "drizzle.png",
    "Light rain": "drizzle.png",
    "Light rain shower": "scattered_showers_day.png",
    "Light rain, haze": "drizzle.png",
    "Mist": "haze_fog_dust_smoke.png",
    "Moderate or heavy rain in area with thunder": "isolated_scattered_tstorms_day.png",
    "Moderate or heavy rain shower": "scattered_showers_day.png",
    "Moderate or heavy rain with thunder": "isolated_scattered_tstorms_day.png",
    "Moderate rain": "heavy_rain.png",
    "Moderate rain at times": "heavy_rain.png",
    "Overcast": "cloudy.png",
    "Partly Cloudy": "partly_cloudy.png",
    "Partly cloudy": "partly_cloudy.png",
    "Patchy light drizzle": "drizzle.png",
    "Patchy light rain": "drizzle.png",
    "Patchy rain nearby": "drizzle.png",
    "Rain shower": "scattered_showers_day.png",
    "Rain with thunderstorm": "isolated_scattered_tstorms_day.png",
    "Shower in vicinity": "scattered_showers_day.png",
    "Shower in vicinity, rain shower": "scattered_showers_day.png",
    "Sunny": "sunny.png",
    "Thundery outbreaks in nearby": "isolated_scattered_tstorms_day.png",
    "Freezing fog": "haze_fog_dust_smoke.png",
    "Heavy snow": "heavy_snow.png",
    "Light freezing rain": "wintry_mix_rain_snow.png",
    "Light rain, mist": "drizzle.png",
    "Light sleet": "sleet_hail.png",
    "Patchy heavy snow": "heavy_snow.png",
    "Patchy light snow": "flurries.png",
    "Patchy moderate snow": "heavy_snow.png",
    "Patchy snow nearby": "flurries.png"
}
ikony_night = {
    "Clear": "clear_night.png",
    "Cloudy": "cloudy.png",
    "Fog": "haze_fog_dust_smoke.png",
    "Haze": "haze_fog_dust_smoke.png",
    "Heavy rain": "heavy_rain.png",
    "Heavy rain at times": "heavy_rain.png",
    "Light drizzle": "drizzle.png",
    "Light rain": "drizzle.png",
    "Light rain shower": "scattered_showers_night.png",
    "Light rain, haze": "drizzle.png",
    "Mist": "haze_fog_dust_smoke.png",
    "Moderate or heavy rain in area with thunder": "isolated_scattered_tstorms_night.png",
    "Moderate or heavy rain shower": "scattered_showers_night.png",
    "Moderate or heavy rain with thunder": "isolated_scattered_tstorms_night.png",
    "Moderate rain": "heavy_rain.png",
    "Moderate rain at times": "heavy_rain.png",
    "Overcast": "cloudy.png",
    "Partly Cloudy": "partly_cloudy_night.png",
    "Partly cloudy": "partly_cloudy_night.png",
    "Patchy light drizzle": "drizzle.png",
    "Patchy light rain": "drizzle.png",
    "Patchy rain nearby": "drizzle.png",
    "Rain shower": "scattered_showers_night.png",
    "Rain with thunderstorm": "isolated_scattered_tstorms_night.png",
    "Shower in vicinity": "scattered_showers_night.png",
    "Shower in vicinity, rain shower": "scattered_showers_night.png",
    "Sunny": "mostly_clear_night.png",
    "Thundery outbreaks in nearby": "isolated_scattered_tstorms_night.png",
    "Freezing fog": "haze_fog_dust_smoke.png",
    "Heavy snow": "heavy_snow.png",
    "Light freezing rain": "wintry_mix_rain_snow.png",
    "Light rain, mist": "drizzle.png",
    "Light sleet": "sleet_hail.png",
    "Patchy heavy snow": "heavy_snow.png",
    "Patchy light snow": "flurries.png",
    "Patchy moderate snow": "heavy_snow.png",
    "Patchy snow nearby": "flurries.png"
}

# ---------- Pogoda ----------
def pobierz_prognoze():
    try:
        url = f"https://wttr.in/{miasto}?format=j1"
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        return None

def pobierz_temperature():
    try:
        url = "https://danepubliczne.imgw.pl/api/data/synop/station/lodz"
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()['temperatura']
    except:
        return None

def dopasuj_ikone(opis, godzina):
    # Zapisuje opisy pogodowe do których nie znaleziono przyporządkowania ikonki
    if opis not in ikony_day or opis not in ikony_night:
        with open('not_matched.txt', "a", encoding="utf-8") as file:
            file.write(f'{opis}\n')  
    if godzina < 20:
        return ikony_day.get(opis, "cloudy.png")
    else:
        return ikony_night.get(opis, "cloudy.png")



# ---------- BLE ----------
ESP_NAME = "ESP32C3"
dom_temp = "--"
dom_batt = "--"
ostatnie_ble = datetime.min

ESP_NAME = "ESP32C3"

def ble_callback(device, advertisement_data):
    global dom_temp, dom_batt, ostatnie_ble

    if device.name and ESP_NAME in device.name:
        md = advertisement_data.manufacturer_data
        if md:
            for _, data in md.items():
                try:
                    tekst = data.decode(errors="ignore")
                    if "-" in tekst:
                        temp_str, batt_str = tekst.split("-")
                        dom_temp = f"{temp_str}°C"
                        dom_batt = f"{batt_str}%"
                        ostatnie_ble = datetime.now()
                        print(f"[BLE] {dom_temp}, {dom_batt}")
                except:
                    pass

async def ble_listener():
    scanner = BleakScanner()
    scanner.register_detection_callback(ble_callback)
    await scanner.start()
    print("[BLE] Skanowanie rozpoczęte.")
    while True:
        await asyncio.sleep(1)  # podtrzymuje działanie

# ---------- Start BLE listener ----------
loop = asyncio.get_event_loop()
loop.create_task(ble_listener())

# ---------- Inicjalizacja ----------
ostatnie_odswiezenie = datetime.min
ikona_biezaca = "cloudy.png"
temp_biezaca = "--"

# ---------- Główna pętla ----------
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or \
           (event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_q)):
            pygame.quit()
            sys.exit()

    now = datetime.now()

    # Czy dane z ESP są nieaktualne?
    if now - ostatnie_ble > timedelta(minutes=60):
        dom_temp = "--"
        dom_batt = "--"

    # odczyt danych z portu szeregowego usb
    tresholodDetection = 3900
    
    line = ser.readline().decode(errors='ignore').strip()
    if line:
        # parsowanie z RX OK: 4095,4095,4095,4095,4095 | RSSI=-83.0 dBm, SNR=6.7 dB, FErr=193 Hz
        # do listy surowych wartości analogowych
        try:
            listAnalogSensors = line[7:].split(' | ')[0].split(',')
            listAnalogSensors = [int(x) for x in listAnalogSensors]
        except:
            pass
        #print(listAnalogSensors)
        mailDetected = False
        mailError = False
        last_lora = datetime.now()
        for analogSensor in listAnalogSensors:
            if analogSensor <= tresholodDetection:
                mailDetected = True
    # Tu ustaw timeout wyświetlania ikonki błędu czujnika listu
    if now - last_lora > timedelta(minutes=180):
        mailError = True



    # Aktualizacja pogody co 30 minf
    if now - ostatnie_odswiezenie > timedelta(minutes=10):
        dane = pobierz_prognoze()
        if dane:
            try:
                aktualna = dane["current_condition"][0]
                temp_biezaca = pobierz_temperature()#aktualna["temp_C"]
                opis = aktualna["weatherDesc"][0]["value"]
                godzina = now.hour
                ikona_biezaca = dopasuj_ikone(opis, godzina)
                ostatnie_odswiezenie = now
                print(ikona_biezaca)
            except:
                pass

    # ---------- Wyświetlanie ----------
    screen.fill(BLACK)
    now_time = now.strftime("%H:%M")
    now_date = now.strftime("%d.%m")

    screen.blit(font.render(now_time, True, WHITE), (100, 47))
    screen.blit(date_font.render(now_date, True, DATE_COLOR), (600, 70))

    try:
        img = pygame.image.load(f"ikony_png/{ikona_biezaca}").convert_alpha()
        img = pygame.transform.scale(img, (220, 220))
        ciemna = pygame.Surface((220, 220), pygame.SRCALPHA)
        ciemna.fill((0, 0, 0, 120))
        img.blit(ciemna, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
        screen.blit(img, (112, 230))
    except:
        pass

    screen.blit(temp_font.render(f"{temp_biezaca}°C", True, WHITE), (120, 450))

    # Wyświetlanie ikonu domku
    try:
        dom_img = pygame.image.load("ikony_png/home.png").convert_alpha()
        dom_img = pygame.transform.scale(dom_img, (100, 100))
        screen.blit(dom_img, (480, 280))
    except:
        pass

    # wyświetlanie ikony listu
    if mailError == False:
        if mailDetected == True:
            try:
                mail_img = pygame.image.load("ikony_png/letter.png").convert_alpha()
                mail_img = pygame.transform.scale(mail_img, (100, 100))
                screen.blit(mail_img, (480, 440))
            except:
                pass
    else:
        # wyświetlanie ikony błędu czujnika listu
        try:
            mailErr_img = pygame.image.load("ikony_png/letterErr.png").convert_alpha()
            mailErr_img = pygame.transform.scale(mailErr_img, (100, 100))
            screen.blit(mailErr_img, (480, 440))
        except:
            pass


    screen.blit(temp_font.render(f"{dom_temp}", True, WHITE), (600, 280))
    screen.blit(small_font.render(f"{dom_batt}", True, WHITE), (600, 380))

    pygame.display.flip()
    clock.tick(1)
    loop.run_until_complete(asyncio.sleep(0))
