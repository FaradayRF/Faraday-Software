
// function for checking valid hexadecimal string
function isHex(string)
{
  for (i=0; i<string.length; i++)
  {
    if (isNaN(parseInt(string.charAt(i), 16)))
    {
	  return false;
	}
  }
  return true;
}

// MSP430 BSL calculate function
function MSP430BslChksmCalc(bsl_type, bsl_bytes)
{
  // get bsl packet data string
  var data  = bsl_bytes.value.replace (/\s+/g, '')
  var ckh, ckl;
  
  // check if string has even length
  if(data.length & 0x01)
  {
    alert("BSL Packet data should have even length");
  }
  else if (isHex(data) == false)
  {
    alert("Invalid hexadecimal string");
  }
  else
  {
    // initialize checksum
	ckl = ckh = 0;
  
    // check BSL type
    if(bsl_type[0].checked)
    {
      // ROM based BSL
	  var even = 0;
	  var byte_string = new String;
	  for(i=0 ; i<data.length ; i+=2)
	  {
	    // read every two characters from the string to form a byte
	    byte_string = data[i] + data [i+1]
		
		// parse the byte string and do the XOR
		if(even == 0)
		{
		  ckl ^= parseInt(byte_string, 16);
		}
		else
	    {
		  ckh ^= parseInt(byte_string, 16);
		}
		
		// toggle flag
	    even ^= 0x01;
	  }
	  
	  // invert the result
	  ckl ^= 0xFF;
	  ckh ^= 0xFF;
	  
	  // shows the checksum
	  alert("CKL=0x" + ckl.toString(16).toUpperCase()  + ", CKH=0x" + ckh.toString(16).toUpperCase());
    }
    else
    {
      // Flash based BSL
      var CRC = 0xFFFF;
	  var byte_string = new String;
	  for(i=0 ; i<data.length ; i+=2)
	  {
	    var x;
		
	    // read every two characters from the string to form a byte
	    byte_string = data[i] + data [i+1];
		data_byte = parseInt(byte_string, 16);
		
		// calculate
        x = ((CRC>>8) ^ data_byte) & 0xff;
        x ^= x>>4;
        CRC = (CRC << 8) ^ (x << 12) ^ (x <<5) ^ x;
      }
	  
	  // shows the checksum
	  alert("CKL=0x" + (CRC & 0xFF).toString(16).toUpperCase()  + ", CKH=0x" + ((CRC>>8)&0xFF).toString(16).toUpperCase());
    }
  }
}
