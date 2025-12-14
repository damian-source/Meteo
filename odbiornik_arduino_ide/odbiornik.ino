#include <Arduino.h>
#include <RadioLib.h>

// --- Piny SX1262 na XIAO ESP32-S3 (z Twojej tabeli) ---
static const int LORA_NSS  = 41;   // CS
static const int LORA_DIO1 = 39;   // IRQ (DIO1)
static const int LORA_RST  = 42;   // RESET
static const int LORA_BUSY = 40;   // BUSY

SX1262 radio = new Module(LORA_NSS, LORA_DIO1, LORA_RST, LORA_BUSY);

// --- Parametry RF: muszą być identyczne jak w TX ---
const float   RF_FREQ_MHZ = 868.0;
const uint8_t RF_BW_KHZ   = 125;
const uint8_t RF_SF       = 12;
const uint8_t RF_CR       = 5;
const uint8_t RF_SYNC     = 0x12;
const int8_t  RF_PWR_DBM  = 10;   // bez znaczenia dla RX, ale API tego wymaga w begin()

void setup() {
  Serial.begin(115200);
  while (!Serial) { delay(10); }
  delay(300);
  Serial.println("RX: boot");

  // Inicjalizacja charakterystyczna dla tej płytki:
  radio.setRegulatorLDO();        // zgodnie z pinoutem Semtech
  radio.setTCXO(3.0, 5.0);        // 3.0 V, ok. 5 ms start
  radio.setDio2AsRfSwitch(true);  // DIO2 steruje przełącznikiem anteny
  radio.setRxBoostedGainMode(true);

  int st = radio.begin(RF_FREQ_MHZ, RF_BW_KHZ, RF_SF, RF_CR, RF_SYNC, RF_PWR_DBM);
  Serial.print("begin="); Serial.println(st);
  if (st != RADIOLIB_ERR_NONE) {
    Serial.println("radio.begin() fail");
    while (true) { delay(1000); }
  }

  Serial.println("RX: ready");
}

void loop() {
  // Blokujące odbieranie z krótkim timeoutem (ms), aby nie zawieszać pętli na zawsze
  String str;
  //int st = radio.receive(str, /*timeout*/ 1000);
  int st = radio.receive(str);

  if (st == RADIOLIB_ERR_NONE) {
    // odebrano poprawną ramkę
    float rssi = radio.getRSSI();
    float snr  = radio.getSNR();
    long  fe   = radio.getFrequencyError();

    Serial.print("RX OK: ");
    Serial.print(str);
    Serial.print(" | RSSI=");
    Serial.print(rssi, 1);
    Serial.print(" dBm, SNR=");
    Serial.print(snr, 1);
    Serial.print(" dB, FErr=");
    Serial.print(fe);
    Serial.println(" Hz");
  } else if (st == RADIOLIB_ERR_RX_TIMEOUT) {
    // cisza w eterze w tym okienku – to normalne, nie spamujemy
  } else {
    Serial.print("RX err: ");
    Serial.println(st);
    // Sporadycznie po błędach można „odświeżyć” radio:
    // radio.standby(); // opcjonalnie
  }

  // krótka pauza, żeby monitor był czytelny
  delay(20);
}
