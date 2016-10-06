# README - Message Application Tutorial #2

The purpose of this application tutorial is to take the very basic program created in the message application #1 and implement very basic upgrades that involve more advanced input and output.

1. Create a generic I/O interface
--* Should be FLASK in the final version, could be generic QUEUE for now
2. Support completely unrestricted fragmentation lengths
3. Support both text and binary data
--* Best way to do this is probably to just create and transfer a text file for a message
--* Will need to make a basic file input and export tool