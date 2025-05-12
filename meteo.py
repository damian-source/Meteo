import pygame
import sys
import requests
from datetime import datetime, timedelta
import json

# Inicjalizacja Pygame
pygame.init()
#screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen = pygame.display.set_mode((1024, 600), 0, 32)
pygame.display.set_caption("Zegar + Pogoda")

# Kolory i czcionki
WHITE = (120, 120, 120)
BLACK = (0, 0, 0)
font = pygame.font.SysFont("Arial", 180)
small_font = pygame.font.SysFont("Arial", 60)
temp_font = pygame.font.SysFont("Arial", 50)
label_font = pygame.font.SysFont("Arial", 30)

# Ustawienia
clock = pygame.time.Clock()
miasto = "Lodz"
pozycje = [(120, 320), (340, 320), (560, 320), (780, 320),
            (120, 470), (340, 470), (560, 470), (780, 470)]

# Mapowanie opisów na pliki ikon
ikony = {
    "clear": "sunny.png",
    "sunny": "sunny.png",
    "clear_night": "clear_night.png",
    "cloudy": "cloudy.png",
    "partly cloudy": "partly_cloudy.png",
    "partly cloudy night": "partly_cloudy_night.png",
    "mostly cloudy": "mostly_cloudy_day.png",
    "mostly cloudy night": "mostly_cloudy_night.png",
    "overcast": "cloudy.png",
    "rain": "showers_rain.png",
    "light rain": "drizzle.png",
    "moderate rain": "heavy_rain.png",
    "snow": "snow_showers_snow.png",
    "fog": "haze_fog_dust_smoke.png",
    "mist": "haze_fog_dust_smoke.png",
    "thunderstorm": "strong_tstorms.png",
    "default": "cloudy.png"
}

# Etykiety pór dnia i dni
pory_dnia = ["Rano", "Dzień", "Wieczór", "Noc"]
etykiety_dni = ["Dziś", "Jutro"]

# Funkcja pobierania danych z wttr.in
def pobierz_prognoze():
    try:
        url = f"https://wttr.in/{miasto}?format=j1"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        return None

# Dopasowanie ikon
def dopasuj_ikone(opis, godzina):
    opis = opis.lower()
    if "clear" in opis and godzina >= 20:
        return ikony.get("clear_night")
    if "partly" in opis and godzina >= 20:
        return ikony.get("partly cloudy night")
    for klucz in ikony:
        if klucz in opis:
            return ikony[klucz]
    return ikony["default"]

# Główna pętla
ostatnie_odswiezenie = datetime.min
prognoza = None

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or \
           (event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_q)):
            pygame.quit()
            sys.exit()

    now = datetime.now()

    if now - ostatnie_odswiezenie > timedelta(minutes=30):
        dane = pobierz_prognoze()
        if dane:
            prognoza = []
            dni = dane["weather"][:2]
            for dzien in dni:
                for h in [4, 10, 16, 22]:
                    najblizsza = min(dzien["hourly"], key=lambda x: abs(int(x["time"]) - h*100))
                    temp = najblizsza["tempC"]
                    opis = najblizsza["weatherDesc"][0]["value"]
                    godzina = h
                    ikona = dopasuj_ikone(opis, godzina)
                    prognoza.append((ikona, temp))
            ostatnie_odswiezenie = now

    screen.fill(BLACK)

    # Godzina, data, dzień tygodnia
    dni_tygodnia = {
        "Monday": "Poniedziałek", "Tuesday": "Wtorek", "Wednesday": "Środa",
        "Thursday": "Czwartek", "Friday": "Piątek", "Saturday": "Sobota", "Sunday": "Niedziela"
    }
    now_time = now.strftime("%H:%M")
    now_date = now.strftime("%d.%m.%Y")
    now_day = dni_tygodnia[now.strftime("%A")]

    screen.blit(font.render(now_time, True, WHITE), (100, 47))
    screen.blit(small_font.render(now_date, True, WHITE), (630, 60))
    screen.blit(small_font.render(now_day, True, WHITE), (665, 140))

    # Etykiety pór dnia (kolumny)
    for i, label in enumerate(pory_dnia):
        screen.blit(label_font.render(label, True, WHITE), (120 + i * 220, 270))

    # Etykiety dni (wiersze)
    for i, label in enumerate(etykiety_dni):
        screen.blit(label_font.render(label, True, WHITE), (30, 320 + i * 150))

    # Ikony i temperatury prognozy
    if prognoza:
        for i, (ikona_plik, temp) in enumerate(prognoza):
            try:
                img = pygame.image.load(f"ikony_png/{ikona_plik}").convert_alpha()
                img = pygame.transform.scale(img, (60, 60))

                # Przyciemnienie ikonki przez nałożenie czarnego półprzezroczystego filtru
                ciemna = pygame.Surface((60, 60), pygame.SRCALPHA)
                ciemna.fill((0, 0, 0, 120))  # 100 = poziom przyciemnienia (0-255) wiecej to ciemniej
                img.blit(ciemna, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

                x, y = pozycje[i]
                screen.blit(img, (x, y))
                screen.blit(temp_font.render(f"{temp}°C", True, WHITE), (x, y + 65))
            except:
                pass

    pygame.display.flip()
    clock.tick(1)
