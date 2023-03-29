// demo: CAN-BUS Shield, send data
// loovee@seeed.cc


#include <SPI.h>

#define CAN_2515
// #define CAN_2518FD

// Set SPI CS Pin according to your hardware
#define MAX_DATA_SIZE 8
#if defined(SEEED_WIO_TERMINAL) && defined(CAN_2518FD)
// For Wio Terminal w/ MCP2518FD RPi Hat：
// Channel 0 SPI_CS Pin: BCM 8
// Channel 1 SPI_CS Pin: BCM 7
// Interupt Pin: BCM25
const int SPI_CS_PIN  = BCM8;
const int CAN_INT_PIN = BCM25;
#else

// For Arduino MCP2515 Hat:
// the cs pin of the version after v1.1 is default to D9
// v0.9b and v1.0 is default D10
const int SPI_CS_PIN = 9;
const int CAN_INT_PIN = 2;
#endif


#ifdef CAN_2518FD
#include "mcp2518fd_can.h"
mcp2518fd CAN(SPI_CS_PIN); // Set CS pin
#endif

#ifdef CAN_2515
#include "mcp2515_can.h"
mcp2515_can CAN(SPI_CS_PIN); // Set CS pin
#endif

void setup() {
    SERIAL_PORT_MONITOR.begin(115200);
    Serial1.begin(115200);
    
    while(!Serial1){};

    while (CAN_OK != CAN.begin(CAN_1000KBPS)) {             // init can bus : baudrate = 500k
        //SERIAL_PORT_MONITOR.println("CAN init fail, retry...");
        delay(100);
    }
    SERIAL_PORT_MONITOR.println("CAN init ok!");
}

uint8_t stmp[8] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFC};
byte cdata[MAX_DATA_SIZE] = {0};
uint32_t id;
uint8_t  type; // bit0: ext, bit1: rtr
uint8_t  len;
void loop() {
  char prbuf[32 + MAX_DATA_SIZE * 3];
    int i, n;
    delay(100);
     
    int lenght = Serial1.available();
    
    if (lenght > 0) {
      
      for (int i = 0; i< lenght;i++){
        uint8_t data = Serial1.read();
        if (data == 0xAC){
          SERIAL_PORT_MONITOR.println("found");
          uint8_t a = Serial1.read();
          uint8_t b = Serial1.read();
          uint8_t c = Serial1.read();
          uint8_t d = Serial1.read();
          
          id  = a | (uint32_t(b) << 8) | (uint32_t(c) << 16) | (uint32_t(d) << 24);
          
          uint8_t msglen = Serial1.read();
          for (int i = 0; i < 3;i++){
            Serial1.read();}
          //SERIAL_PORT_MONITOR.println(msglen);
          for (uint8_t e = 0; e<msglen;e++){
            stmp[e]=Serial1.read();
            //SERIAL_PORT_MONITOR.println(stmp[e]);
          }
        break;}
 
      }

    /*stmp[7] = stmp[7] + 1;
    if (stmp[7] == 100) {
        stmp[7] = 0;
        stmp[6] = stmp[6] + 1;

        if (stmp[6] == 100) {
            stmp[6] = 0;
            stmp[5] = stmp[5] + 1;
        }
    }
    */

    CAN.sendMsgBuf(id,0,8,stmp);
                           // send data per 100ms
    }
    // send data:  id = 0x00, standrad frame, data len = 8, stmp: data buf
    
    if (CAN_MSGAVAIL != CAN.checkReceive()) {
      //SERIAL_PORT_MONITOR.println("No info");
        return;
    }

    // read data, len: data length, buf: data buf
    CAN.readMsgBufID(&id,&len, cdata);
    //delay(50);
    SERIAL_PORT_MONITOR.println(len);
    //Serial1.write(id);
    for (int i = 0; i<len;i++){
      Serial1.write(cdata[i]);
      SERIAL_PORT_MONITOR.println(cdata[i]);
    }
    
}

// END FILE
