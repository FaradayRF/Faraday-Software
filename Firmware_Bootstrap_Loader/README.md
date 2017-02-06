# Programming Faraday Firmware - Bootstrap Loader Tutorial

**Plan**

* Introduce JTAG/BSL
* Files Needed
* How BSL in invoked on Faraday
* Changing the BSL file (provided .txt and making a new .txt file)



Each Faraday digital radio has a CC430F6137 microcontroller that can be be reprogrammed using two main methods. 

### JTAG

The primary method using an MSP430-FET device or similar to both program and perform runtime debugging operations

###BSL - Bootstrap Loader

A BSL invokes a specific GPIO sequence (RESET and TEST GPIO's) that allows firmware to be programmed using ONLY a connected USB cable. Faraday's bootstrap loader cannot perform runtime debugging.








