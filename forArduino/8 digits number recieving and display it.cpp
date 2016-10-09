/*
 * (c) Dmytro Nikandrov
 * August 2016
 * 
 * This code should display the number received over serial connection from some host
 * uses 2 ICs 74HC595 to drive 2* 4 digits 7-segment indicators
 * default displayed value is 1 2 3 4 5 6 7 8
 */


// the number characters and null
char numStr[9];

// the number characters and null
char dispStr[9] = {'8', '7', '6', '5', '4', '3', '2', '1', '\0'};
char *ptrStr = dispStr;

// the number stored as a long integer
long number;
int i = 0;

// whether the number is complete
boolean isNumberComplete = false;
char endMarker = '\n';
char c;


// pins to which 74HC595 is connected
#define DATA_PIN    11
#define LATCH_PIN   8
#define CLOCK_PIN   12

#define SEGM_DIGIT_PIN_1   5
#define SEGM_DIGIT_PIN_2   4
#define SEGM_DIGIT_PIN_3   3
#define SEGM_DIGIT_PIN_4   2


/*
 * переменные, в каждой из которых хранится один байт
 * записанный побитно (после 0b) так, что каждый бит кодирует включение
 * или выключение одного сегмента индикатора, 
 * и комбинация включенных сегментов образует соответствующий символ-цифру
 * 
 * segments of the 7seg indicator
 * IC transmit this numbers as-written, so to light segment A chip will emit Q0=0,Q1=0,Q2=0,Q3=0,Q4=0,Q5=0,Q6=0,Q7=1
 * 
 * byte d0 = 0b00000001;//seg A
 * byte d1 = 0b00000010;//seg F 
 * byte d2 = 0b00000100;//seg B
 * byte d3 = 0b00001000;//seg G
 * byte d4 = 0b00010000;//seg C
 * byte d5 = 0b00100000;//seg dot
 * byte d6 = 0b01000000;//seg D
 * byte d7 = 0b10000000;//seg E
 */



byte d0 = 0b11010111;  //displayed digit 0 segments f e d c b a
byte d1 = 0b00010100;  //displayed digit 1 segments b c
byte d2 = 0b11001101;  //displayed digit 2 segments a b d e g
byte d3 = 0b01011101;  //displayed digit 3 segments a b c d g
byte d4 = 0b00011110;  //displayed digit 4 segments b c f g
byte d5 = 0b01011011;  //displayed digit 5 segments a c d f g
byte d6 = 0b11011011;  //displayed digit 6 segments a c d e f g
byte d7 = 0b00010101;  //displayed digit 7 segments a b c
byte d8 = 0b11011111;  //displayed digit 8 segments a b c d e f g
byte d9 = 0b01011111;  //displayed digit 9 segments a b c d f g
byte dd = 0b00100000;  //displayed symbol . segment dot

// default display data
byte value1 = 0b00000000, value2 = 0b00000000;

// n is a number of current digit shown by indicator
int n = 0;
int delay_value = 0;


byte SymbNumToByte(char somenum)
{
  switch(atoi(&somenum))
  {
     case 0:
        return d0;
     case 1:
        return d1;
     case 2:
        return d2;
     case 3:
        return d3;
     case 4:
        return d4;
     case 5:
        return d5;
     case 6:
        return d6;
     case 7:
        return d7;
     case 8:
        return d8;
     case 9:
        return d9;

     default :
        return d0;
  }
}


void setup()
{
  Serial.begin(9600);
  pinMode(DATA_PIN, OUTPUT);
  pinMode(CLOCK_PIN, OUTPUT);
  pinMode(LATCH_PIN, OUTPUT);

  pinMode(SEGM_DIGIT_PIN_1, OUTPUT);
  pinMode(SEGM_DIGIT_PIN_2, OUTPUT);
  pinMode(SEGM_DIGIT_PIN_3, OUTPUT);
  pinMode(SEGM_DIGIT_PIN_4, OUTPUT);

  digitalWrite(SEGM_DIGIT_PIN_1, LOW);
  digitalWrite(SEGM_DIGIT_PIN_2, LOW);
  digitalWrite(SEGM_DIGIT_PIN_3, LOW);
  digitalWrite(SEGM_DIGIT_PIN_4, LOW);

  delay_value = 1; // milliseconds
}


void serialEvent() {

    // read the characters from the buffer into a character array
    while(Serial.available() > 0)
    {
      c = Serial.read();
      if (c != endMarker && (!isalpha(c)) && (i < 8))
      {
        numStr[i] = c;
        numStr[i+1] = '\0'; // terminate the string with a null prevents atol reading too far
//        Serial.print(i);
//        Serial.print(" : ");
//        Serial.println(numStr[i]);
        i++;
      }
    }

    if (i == 8)
    {
      // convert to long int
      number = atol(numStr);
      isNumberComplete = true;
      i = 0;
    }
    
//    Serial.println("serialEvent finish");
}


void loop() {
    if (isNumberComplete)
  {
    strcpy(dispStr, numStr);
    Serial.println(number);
//    delay(10000);
    // clear the string:
    numStr[0] = '\0';
    isNumberComplete = false;
  }

  if (n > 4) n=0;
  n++;

  if (n == 1)
{
    digitalWrite(SEGM_DIGIT_PIN_1, HIGH);
    digitalWrite(SEGM_DIGIT_PIN_2, LOW);
    digitalWrite(SEGM_DIGIT_PIN_3, LOW);
    digitalWrite(SEGM_DIGIT_PIN_4, LOW);

    value1 = SymbNumToByte(dispStr[3]);
    value2 = SymbNumToByte(dispStr[7]);
}

  if (n == 2) {
    digitalWrite(SEGM_DIGIT_PIN_1, LOW);
    digitalWrite(SEGM_DIGIT_PIN_2, HIGH);
    digitalWrite(SEGM_DIGIT_PIN_3, LOW);
    digitalWrite(SEGM_DIGIT_PIN_4, LOW);

    value1 = SymbNumToByte(dispStr[2]);
    value2 = SymbNumToByte(dispStr[6]);
}
    
  if (n == 3) {
    digitalWrite(SEGM_DIGIT_PIN_1, LOW);
    digitalWrite(SEGM_DIGIT_PIN_2, LOW);
    digitalWrite(SEGM_DIGIT_PIN_3, HIGH);
    digitalWrite(SEGM_DIGIT_PIN_4, LOW);

    value1 = SymbNumToByte(dispStr[1]);
    value2 = SymbNumToByte(dispStr[5]);
}
  
  if (n == 4)
{
    digitalWrite(SEGM_DIGIT_PIN_1, LOW);
    digitalWrite(SEGM_DIGIT_PIN_2, LOW);
    digitalWrite(SEGM_DIGIT_PIN_3, LOW);
    digitalWrite(SEGM_DIGIT_PIN_4, HIGH);

    value1 = SymbNumToByte(dispStr[0]);
    value2 = SymbNumToByte(dispStr[4]);
}


digitalWrite(LATCH_PIN, LOW);   
shiftOut(DATA_PIN, CLOCK_PIN, LSBFIRST, value2);  // value for IC №2
shiftOut(DATA_PIN, CLOCK_PIN, LSBFIRST, value1);  // value for IC №1
digitalWrite(LATCH_PIN, HIGH);

delay(2);

// zeroing pins of the 74hc595 to eradicate IC memory effect
// which causes glitches on the indicator
digitalWrite(LATCH_PIN, LOW);
shiftOut(DATA_PIN, CLOCK_PIN, LSBFIRST, 0b00000000);  // value for IC №2
shiftOut(DATA_PIN, CLOCK_PIN, LSBFIRST, 0b00000000);  // value for IC №1
digitalWrite(LATCH_PIN, HIGH);

// Serial.println(delay_value);
delay(delay_value);
}
