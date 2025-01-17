void setup() {
    Serial.begin(9600);
    pinMode(13, OUTPUT); // Buzzer connected to pin 8
}

void loop() {
    if (Serial.available() > 0) {
        String data = Serial.readString();
        if (data == "ALERT\\n") {
            digitalWrite(13, HIGH);
            delay(1000); // Buzz for 1 second
            digitalWrite(13, LOW);
        }
    }
}
