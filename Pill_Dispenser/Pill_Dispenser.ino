//#include <HX711.h>
#include <Servo.h>
//functions for weight sensor, pill dispensing (wait for touch), IR sensor(is pill available)

#define R1 2
#define B1 3
#define G1 4
#define Y 5
#define R2 6
#define B2 7
#define G2 8
#define Touch_Button_Pin_1 9
#define Speaker 17
#define Left_Button 10
#define Right_Button 11
#define IR_Sensor 9

Servo servo;
// Scale Settings
const int SCALE_DOUT_PIN = 12;
const int SCALE_SCK_PIN = 13;

int IRsensorValue = 0;        // value read from the receiver
int touchState = 0;        //Touch Sensor state
String incomingString = "";    //Serial read string
String temp = "";             //temporary String
String Dispense = "Dispense"; //Dispense Command
int count = 0;                //Dispense Amount
int leftButton;           //left button state
int lastLeftButton = LOW;       //previous left button state
int leftReading;            //left reading
int rightButton;          //right button state
int lastRightButton = LOW;       //previous right button state
int rightReading;           //right reading
unsigned long lastDebounceTime = 0; //last time button was pressed
unsigned long debounceDelay = 50;   //debounce time
int RButton = 0;        //keep track of toggle state
int LButton = 0;        //keep track of toggle state
bool L = 0;         //track empty
bool M = 0;         //track low
bool H = 0;         //track full
bool disp = 0;      //track dispense

//HX711 scale(SCALE_DOUT_PIN, SCALE_SCK_PIN);

void setup() {
  servo.attach(16); //D11
  servo.write(90);
  pinMode(IR_Sensor, INPUT);
  pinMode(Speaker, OUTPUT);
  pinMode(2, OUTPUT);
  pinMode(Touch_Button_Pin_1, INPUT);
  pinMode(Left_Button, INPUT);
  pinMode(Right_Button, INPUT);
  pinMode(R1, OUTPUT);
  pinMode(G1, OUTPUT);
  pinMode(B1, OUTPUT);
  pinMode(Y, OUTPUT);
  pinMode(R2, OUTPUT);
  pinMode(G2, OUTPUT);
  pinMode(B2, OUTPUT);
  Serial.begin(9600);
//  scale.set_scale(-1800.00/75.00);
//  scale.tare();
  Serial.println("setup done");
}

void loop() {
//  senseWeight();

  //read Serial
  while(Serial.available()){
    delay(1000);
    incomingString="";
    temp="";
    incomingString = Serial.readString();
    if(incomingString.length() > 0){
      temp = incomingString;
      temp.remove(8);
      if(temp.equals(Dispense)){
        temp = incomingString;
        temp.remove(0,9);
        temp.remove(1);
        if(temp.equals("L")){
            setColor1(255,0,0);
            digitalWrite(Y,LOW);
            setColor2(255,0,0);
            L = 1;
            M = 0;
            H = 0;
        }
        else if(temp.equals("M")){
            setColor1(0,0,0);
            digitalWrite(Y, HIGH);
            setColor2(0,0,0);
            L = 0;
            M = 1;
            H = 0;
      }
      else if(temp.equals("H")){
            setColor1(0,255,0);
            digitalWrite(Y, LOW);
            setColor2(0,255,0);
            L = 0;
            M = 0;
            H = 1;
      }
        temp = incomingString;
        temp.remove(0,11);
        count = temp.toInt();
        Serial.println(count);
        int timer = 0;
        while ((leftEar()||rightEar()) != 1){  
          if (timer%30 == 0){
            Serial.println("Alarm Disp"); 
            tone(Speaker, 261);
            delay(1000);
            noTone(Speaker);
            tone(Speaker, 329);
            delay(1000);
            noTone(Speaker);
            tone(Speaker, 392);
            delay(1000);
            noTone(Speaker);
          }
        timer = timer + 1;
        delay(100);
        }
        Serial.println("Ack Disp");
        disp = 1;
        setColor1(0,0,0);
        setColor2(0,0,0);
        delay(100);
        setColor1(0,255,0);
        delay(100);
        setColor1(0,0,0);
        delay(100);
        setColor2(0,255,0);
        delay(100);
        setColor2(0,0,0);
        delay(100);
        tone(Speaker, 440);
        delay(1000);
        noTone(Speaker);
        dispense(count);
        if (L == 1){
          setColor1(255,0,0);
          digitalWrite(Y,LOW);
          setColor2(255,0,0);
        }
        else if(M == 1){
          setColor1(0,0,0);
          digitalWrite(Y, HIGH);
          setColor2(0,0,0);
        }
        else if(H == 1){
          setColor1(0,255,0);
          digitalWrite(Y, LOW);
          setColor2(0,255,0);
        }
        break;
      }
      else{
        Serial.println(incomingString);
        break;
      }
    }
  }

//  if (pettouchSensor() == 1){
//    Serial.println("Pet");
//    setColor1(0,0,0);
//    setColor2(0,0,0);
//    delay(100);
//    setColor1(0,0,255);
//    setColor2(0,0,255);
//    delay(100);
//    setColor1(0,0,0);
//    setColor2(0,0,0);
//    tone(Speaker, 493);
//    delay(1000);
//    noTone(Speaker);
//  }
  if(disp == 1){
    leftEar();
    rightEar();
    disp = 0;
  }
  if (leftEar() == 1){
    Serial.println("Left Ear");
    setColor1(0,0,0);
    setColor2(0,0,0);
    delay(100);
    setColor1(0,255,255);
    delay(100);
    tone(Speaker, 294);
    delay(1000);
    noTone(Speaker);
    setColor1(0,0,0);
    if (L == 1){
      setColor1(255,0,0);
      digitalWrite(Y,LOW);
      setColor2(255,0,0);
     }
     else if(M == 1){
      setColor1(0,0,0);
      digitalWrite(Y, HIGH);
      setColor2(0,0,0);
     }
     else if(H == 1){
      setColor1(0,255,0);
      digitalWrite(Y, LOW);
      setColor2(0,255,0);
     }
  }

  if (rightEar() == 1){
    Serial.println("Right Ear");
    setColor1(0,0,0);
    setColor2(0,0,0);
    delay(100);
    setColor2(0,255,255);
    delay(100);
    tone(Speaker, 349);
    delay(1000);
    noTone(Speaker);
    setColor2(0,0,0);
    if (L == 1){
      setColor1(255,0,0);
      digitalWrite(Y,LOW);
      setColor2(255,0,0);
     }
     else if(M == 1){
      setColor1(0,0,0);
      digitalWrite(Y, HIGH);
      setColor2(0,0,0);
     }
     else if(H == 1){
      setColor1(0,255,0);
      digitalWrite(Y, LOW);
      setColor2(0,255,0);
     }
  }
}

//void senseWeight(){
//  float w = scale.get_units(1); //get weight
//  String weight = String(w, 2);
//  Serial.println(weight);
//  if (w <= 20){
//    setColor1(255,0,0);
//    digitalWrite(Y,LOW);
//    setColor2(255,0,0);
//    Serial.println("Empty");
//    delay(1000);
//  }
//  else if (w > 20 && w <= 100){
//    setColor1(0,0,0);
//    digitalWrite(Y, HIGH);
//    setColor2(0,0,0);
//    Serial.println("Low");
//    delay(1000);
//  }
//  else if (w > 100){
//    setColor1(0,255,0);
//    digitalWrite(Y, LOW);
//    setColor2(0,255,0);
//    Serial.println("Gucci");
//    delay(1000);
//  }
//}

void dispense(int count){
  int i = 0;
  unsigned long start = millis();
  Serial.println("Dispensing");
  while (i < count){
   servo.write(140);
   if (pillDispensed() == 1){              //If pill dispensed
      start = millis();
      i++;  
      delay(100);
   }
   if ((millis() - start) > 10000){
    Serial.println("Jam");
    break;
   }
  }
  servo.write(90);
  Serial.println("Done Disp");
}

bool pillDispensed(){
  // read the analog in value:
  int count = 0;
  // print the results to the serial monitor:
  //Serial.print("\nsensor = ");
  //Serial.print(IRsensorValue);
  //the threshold found fron analog In Out program was when object is detected, the sensor value is below 100
  //set the threshold whihc you get
  //the threshold varies for different sets of emitter-receiver pairs
  while (count < 15){
    if (digitalRead(IR_Sensor) == false){
      count++;
      continue;
    }
    else{
      break;
    }
  }
  if(count >= 15){ //checks if object is there or not
    Serial.print("\nObject Detected");
    return true;
    }
  else{
    return false;
    }
}

//bool pettouchSensor(){
//  return digitalRead(Touch_Button_Pin_1);         //check if touched
//}

bool leftEar(){
  int state = digitalRead(Left_Button);
  if (LButton != state){
    LButton = state;
    return true;
  }
  return false;
}

bool rightEar(){
  int state = digitalRead(Right_Button);
  if (RButton != state){
    RButton = state;
    return true;
  }
  return false;
}

void setColor1 (int redValue, int greenValue, int blueValue) {
  analogWrite(R1, redValue);
  analogWrite(G1, greenValue);
  analogWrite(B1, blueValue);
}

void setColor2(int redValue, int greenValue, int blueValue) {
  analogWrite(R2, redValue);
  analogWrite(G2, greenValue);
  analogWrite(B2, blueValue);
}
