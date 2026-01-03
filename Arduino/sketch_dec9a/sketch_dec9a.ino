// Código Arduino para alarma - SONIDO DE ALARMA REAL
const int BUZZER_PIN = 9;
const int LED_PIN = 13;

bool alarmActive = false;
unsigned long previousMillis = 0;
int toneState = 0;

void setup() {
  Serial.begin(9600);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  
  // Asegurar que todo esté apagado al inicio
  digitalWrite(LED_PIN, LOW);
  digitalWrite(BUZZER_PIN, LOW);
  noTone(BUZZER_PIN);
  
  // Señal de inicio
  delay(1000);
  digitalWrite(LED_PIN, HIGH);
  tone(BUZZER_PIN, 1000, 200);
  delay(300);
  digitalWrite(LED_PIN, LOW);
}

void loop() {
  // Verificar comandos seriales
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command == "ALARM_ON") {
      alarmActive = true;
      Serial.println("OK_ALARM_ON");
    }
    else if (command == "ALARM_OFF") {
      alarmActive = false;
      digitalWrite(LED_PIN, LOW);
      noTone(BUZZER_PIN);
      digitalWrite(BUZZER_PIN, LOW);
      Serial.println("OK_ALARM_OFF");
    }
    else if (command == "TEST") {
      // Test de alarma por 2 segundos
      unsigned long testStart = millis();
      while (millis() - testStart < 2000) {
        playAlarmSound();
      }
      digitalWrite(LED_PIN, LOW);
      noTone(BUZZER_PIN);
      Serial.println("OK_TEST");
    }
  }
  
  // Si la alarma está activa, reproducir sonido
  if (alarmActive) {
    playAlarmSound();
  }
}

void playAlarmSound() {
  unsigned long currentMillis = millis();
  
  // Patrón de sirena: alterna entre dos tonos cada 150ms
  if (currentMillis - previousMillis >= 150) {
    previousMillis = currentMillis;
    
    if (toneState == 0) {
      tone(BUZZER_PIN, 800);  // Tono bajo
      digitalWrite(LED_PIN, HIGH);
      toneState = 1;
    } 
    else if (toneState == 1) {
      tone(BUZZER_PIN, 1200); // Tono alto
      digitalWrite(LED_PIN, LOW);
      toneState = 2;
    }
    else if (toneState == 2) {
      tone(BUZZER_PIN, 800);  // Tono bajo
      digitalWrite(LED_PIN, HIGH);
      toneState = 3;
    }
    else {
      tone(BUZZER_PIN, 1200); // Tono alto
      digitalWrite(LED_PIN, LOW);
      toneState = 0;
    }
  }
}