#include <Arduino.h>
#include <RadioLib.h>

// Konfiguracja modułu Lora
static const int LORA_NSS  = 41;
static const int LORA_DIO1 = 39;
static const int LORA_RST  = 42;
static const int LORA_BUSY = 40;
SX1262 radio = new Module(LORA_NSS, LORA_DIO1, LORA_RST, LORA_BUSY);
const float   RF_FREQ_MHZ = 868.0;
const uint8_t RF_BW_KHZ   = 125;
const uint8_t RF_SF       = 12;
const uint8_t RF_CR       = 5;
const uint8_t RF_SYNC     = 0x12;
const int8_t  RF_PWR_DBM  = 22;

// Konfiguracja deep sleep
const uint64_t uS_TO_S_FACTOR = 1000000ULL; // przelicznik sekund na mikrosekundy
const uint64_t TIME_TO_SLEEP = 7200;  // czas snu

// konfiguracja elektronicznego włącznika zasilania czujników
#define SENSORS_ON 44   // D7 = GPIO44

// Konfiguracja wejść analogowych
const int sensor_0 = 1;
const int sensor_1 = 2;
const int sensor_2 = 3;
const int sensor_3 = 4;
const int sensor_4 = 5;

void setup() {
  // konfiguracja pinów
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH);
  pinMode(SENSORS_ON, OUTPUT);
  pinMode(sensor_0, INPUT);
  pinMode(sensor_1, INPUT);
  pinMode(sensor_2, INPUT);
  pinMode(sensor_3, INPUT);
  pinMode(sensor_4, INPUT);

  // włączenie zasilania czujników
  digitalWrite(SENSORS_ON, HIGH);

  Serial.begin(115200);
  unsigned long t0 = millis();
  while (!Serial && (millis() - t0 < 1000)) { delay(10); }  // max 1 s czekania
  delay(300);
  Serial.println("TX: boot");
  

  // ważne dla tej płytki:
  radio.setRegulatorLDO();          // zgodnie z pinoutem Semtech
  radio.setTCXO(3.0, 5.0);          // 3.0V, ~5 ms start
  radio.setDio2AsRfSwitch(true);    // DIO2 = 38, przełącznik anteny

  int status_init_radio = radio.begin(RF_FREQ_MHZ, RF_BW_KHZ, RF_SF, RF_CR, RF_SYNC, RF_PWR_DBM);
  Serial.print("begin="); Serial.println(status_init_radio);
  if (status_init_radio != RADIOLIB_ERR_NONE) while (1) { delay(1000); }

  // opcjonalnie wzmocniony RX (nie przeszkadza TX)
  radio.setRxBoostedGainMode(true);
  Serial.println("TX ready");

  // Odczyt wejść analogowych
  int val_analog_0 = analogRead(sensor_0);
  int val_analog_1 = analogRead(sensor_1);
  int val_analog_2 = analogRead(sensor_2);
  int val_analog_3 = analogRead(sensor_3);
  int val_analog_4 = analogRead(sensor_4);

  String payload = 
      String(val_analog_0) + "," +
      String(val_analog_1) + "," +
      String(val_analog_2) + "," +
      String(val_analog_3) + "," +
      String(val_analog_4);

  int status_sending = radio.transmit(payload);   // blokująco, czeka na TX_DONE (DIO1)
  if (status_sending == RADIOLIB_ERR_NONE) {
    Serial.print("TX OK: "); Serial.println(payload);
  } else {
    Serial.print("TX err: "); Serial.println(status_sending);
  }
  // wyłączenie zasilania czujników
  digitalWrite(SENSORS_ON, LOW);

  // uśpienie radia (opcjonalnie, ale zalecane dla niskiego poboru)
  radio.sleep();


  // sygnalizacja zakończenia programu
  for (int i = 0; i < 4; i++) {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(50);
    digitalWrite(LED_BUILTIN, LOW);
    delay(50);
  }

  // konfiguracja timera do wybudzania 
  esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP * uS_TO_S_FACTOR);

  // przejście do deep sleep
  esp_deep_sleep_start();

}

void loop() {
  // put your main code here, to run repeatedly:

}
