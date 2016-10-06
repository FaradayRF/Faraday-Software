# from construct import *


def freq0_carrier_calculation(fxosc, freq_desired, debug):
    """
    Calculates the FREQ0, FREQ1, and FREQ2 24 bit word for main carrier frequency of the CC430.

    :param fxosc: CC430 High Frequency crystal frequency in MHZ  (Integer or float)
    :param freq_desired: Frequency in MHz that is desired to tune to (Integer or float)
    :param debug: If True then the function will print additional information about the calculation process

    :return: A list\: [FREQ2, FREQ1, FREQ0, STR(actual frequency of carrier in MHz)]


    .. note:: The CC430 high frequency crystal for Faraday is 26.0 MHz


     .. warning:: Faraday only supports the Amateur Radio 900MHz band (902-928MHz).

    """

    # Calculate the smallest bit resolution in VC0 based on crystal
    vco_step_float = float(fxosc * 10 ** 6) / 2 ** 16

    # Calculate 24 bit word needed for desired frequency nd return INT
    desired_freq_word_int = int((float(freq_desired) * 10 ** 6) / vco_step_float)
    desired_freq_step_count_int = int(desired_freq_word_int) * vco_step_float

    actual_freq_step_count_float = int(desired_freq_step_count_int) / float((10 ** 6))

    # Convert 24 bit word into hex string and parse into FREQ2, FREQ1, and FREQ0
    desired_freq_word_int_hex = hex(desired_freq_word_int)
    cc430_freq_reg_list = [desired_freq_word_int_hex[i:i + 2] for i in range(0, len(desired_freq_word_int_hex), 2)]

    # Create list of INT's of the 3 bytes for FREQx's
    cc430_freq_reg_list[0] = int(cc430_freq_reg_list[1], 16)  # FREQ2
    cc430_freq_reg_list[1] = int(cc430_freq_reg_list[2], 16)  # FREQ1
    cc430_freq_reg_list[2] = int(cc430_freq_reg_list[3], 16)  # FREQ0
    cc430_freq_reg_list[3] = actual_freq_step_count_float  # append actual frequency for reference

    if debug:
        print "vco_step_float (Hz) =", vco_step_float
        print "24-bit word for desired frequency (int): ", int(desired_freq_step_count_int)
        print "24-bit word for desired frequency (hex): ", hex(desired_freq_word_int)
        # Calculate actual achieved frequency due to VCO step size
        print "Actual result frequency (MHz): ", actual_freq_step_count_float
    else:
        pass

    # RETURN list of FREQx bytes and actual achieved frequency
    return cc430_freq_reg_list


def freq0_reverse_carrier_calculation(fxosc, freq0, freq1, freq2, debug):
    """
    This function reverse calculates the CC430 frequency in MHz from the known freq[] bytes in the
    CC430 radio registers.

    :param fxosc: CC430 High Frequency crystal frequency in MHZ  (Integer or float)
    :param freq0: Frequency byte index 0
    :param freq1: Frequency byte index 1
    :param freq2: Frequency byte index 2
    :param debug: If True then the function will print additional information about the calculation process

    :return: Returns the calculated frequency in MHz as a float.

    .. note:: The CC430 high frequency crystal for Faraday is 26.0 MHz
    """
    # Calculate the smallest bit resolution in VC0 based on crystal
    vco_step_float = float(fxosc * 10 ** 6) / 2 ** 16

    # print steps for rebuild
    freq0_shifted = freq0 << 16
    freq1_shifted = freq1 << 8
    freq2_shifted = freq2

    actual_freq_mhz = (int(hex(freq0_shifted + freq1_shifted + freq2_shifted), 16) * vco_step_float) / float(10 ** 6)
    if debug == 1:
        print freq0_shifted, freq1_shifted, freq2_shifted
        print actual_freq_mhz
    return actual_freq_mhz
