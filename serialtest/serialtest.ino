void setup() {
  Serial.begin(9600);
  pinMode(2, OUTPUT);
  digitalWrite(2, HIGH);
}

void loop() {
//  String data = "Left Ear";
//  Serial.println(data);
//  delay(2000);
//  data = "Right Ear";
//  Serial.println(data);
//  delay(8000);
//  data = "Petting";
//  Serial.println(data);
//  delay(2000);
  String l = Serial.readString();
  if(l.indexOf("Dispense 1")>0){
    digitalWrite(2, LOW);
  }
  
}

