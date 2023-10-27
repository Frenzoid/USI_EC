int pin 15;
int outputValue = 5;

void setup() {
  Serial.begin(9600);
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  analogWrite(pin_number, outputValue);
  digitalWrite(LED_BUILTIN, HIGH);
  Serial.print("Sending...");
  delay(2000);
  digitalWrite(LED_BUILTIN, LOW);
  delay(3000);
}
