/*
 * Commands to the Teensy should convey the entire state of the AC
 * Commands follow the NMEA data format, because it's simple
 * Format: $PAC,on,mode,temperature,fan speed
 * 
 * Set temperature: $PAC,1,C,75,3
 * Turn off: $PAC,0,,,,
 * 
 */

#include <IRremote.h>

#define CMD_PREFIX "$PAC,"

enum ACMode: uint8_t {
  MODE_COOL = 0x0,
  MODE_DRY = 0x1,
  MODE_FAN = 0x2,
  MODE_MONEYSAVER = 0x6,
};

IRsend irsend;
String cmdBuffer;

void setup() {
  Serial.begin(9600); // USB is always 12 Mbit/sec
}

/*
 * Read commands from the serial port, and dispatch the command handler
 * when a full newline-terminated command is received
 */
void loop() {
  while(Serial.available()) {
    char c = Serial.read();
    if(c == '\n') {
      handleCommand(cmdBuffer);
      cmdBuffer = "";
    } else {
      cmdBuffer += c;
    }
  }
}

/* 
 * Parse a single command and (if valid) send it to the AC
 */
void handleCommand(const String& cmd) {
  // Check for malformed commands
  if (!cmd.startsWith(CMD_PREFIX)) {
    return;
  }

  int on_idx = cmd.indexOf(',') + 1;
  bool on = (cmd.charAt(on_idx) == '1');

  if(!on) {
    turnOff();
    return;
  }

  ACMode mode = MODE_COOL;
  int mode_idx = cmd.indexOf(',', on_idx) + 1;
  switch (cmd.charAt(mode_idx)) {
    case 'C':
      mode = MODE_COOL;
      break;
    case 'D':
      mode = MODE_DRY;
      break;
    case 'F':
      mode = MODE_FAN;
      break;
    case 'S':
    case 'M':
      mode = MODE_MONEYSAVER;
      break;
  }

  int temp_idx = cmd.indexOf(',', mode_idx) + 1;
  int temp = cmd.substring(temp_idx).toInt();

  int fan_idx = cmd.indexOf(',', temp_idx) + 1;
  int fan_speed = cmd.substring(fan_idx).toInt();
  
  sendUpdate(mode, on, temp, fan_speed);
}

/* 
 * Build and send the update packet 
 */
void sendUpdate(ACMode mode, bool on, uint8_t temp, uint8_t fan_speed) {
  uint32_t data = 0x8820000;

  uint8_t enc_temp = (temp - 59) << 1;
  enc_temp = (enc_temp | enc_temp >> 5) & 0x1F;

  data |= (on & 0x1) << 15;
  data |= mode << 12;
  data |= enc_temp << 7;
  data |= ((1 << (fan_speed - 1)) & 0x6) << 4;

  int checksum = 0;
  for (int i = 4; i < 28; i += 4) {
      checksum += (data >> i) & 0xF;
  }
  data |= checksum & 0xF;
  irsend.sendNEC(data, 28);
}

void turnOff() {
  irsend.sendNEC(0x88C0051, 28);
}
