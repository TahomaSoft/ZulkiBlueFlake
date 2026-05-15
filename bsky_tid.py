'''// SPDX-License-Identifier: GPL-3.0-or-later
Author: Erik Beck (bacon@tahomasoft.com)
Date last revised: 30 April 2024

A set of functions to create a time-based ID (TID) record identifier
as part of programs to use the atproto of the Bluesky Social app.

This is the more restrictive TID form of the record key

https://atproto.com/specs/record-key

'''

import time
import math
import string

STRING_LEN = 13

def bsky_convert2_b32 (TID_raw64bit_int):
    '''
    Function to encode a number into atproto-bsky base32 format
    Progressive divison method

    '''

    BASE = 32

    # TESTVAL = 8675309

    remainder = BASE *2 # goofy start
    quotient = BASE *2 #  GOOFY start

    remainder_list = []
    quotient_list = []


    dividend = TID_raw64bit_int
    divisor = BASE


    while quotient > 0:
        '''
        use successive division by 32
        store the quotient and remainder in a list
        Append both lists at the front
        Remainder list is the one that really matters
        Kept the quotient to check my work
        '''

        quotient = math.trunc(dividend/divisor)
        quotient_list.insert(0,quotient)

        remainder = dividend % divisor
        remainder_list.insert(0,remainder)
        
        dividend = quotient 

    b32_entry = remainder_list
    byte_string = ""

    for i in b32_entry:
        j = bskybase32_lookup (i)

        byte_string += j


    fixed_string = check_padding (byte_string)

    return fixed_string

def check_padding (byte_string2check):
    '''if byte string is less than 13 (STRING_LEN) characters, need
    to front pad with integer zero, or, in this encoding, '2'.

    '''
    

    if (len(byte_string2check))==STRING_LEN:
        # all good, return as is
        return byte_string2check

    elif (len(byte_string2check)) > STRING_LEN:
        # This is an error, stop program
        raise ValueError('byte string for TID over ', STRING_LEN)
        raise Exception('Stop program')

    elif (len(byte_string2check)) < STRING_LEN:
        # front pad with 2 
        pads  = STRING_LEN - len(byte_string2check)
        revised_string = byte_string2check
        
        while pads > 0:
            revised_string = '2' + revised_string
            pads = pads -1
        return revised_string
    
    else:
        raise Exception('Weird. Stop program')


def bskybase32_lookup (integer2map):
    '''
    Function to map the base32 power and remainder to the right character set
    for atproto
    '''
    b32_lookup = {
		  0:  '2',
		  1:  '3',
		  2:  '4',
		  3:  '5',
		  4:  '6',
		  5:  '7',
		  6:  'a',
		  7:  'b',
		  8:  'c',
		  9:  'd',
		  10: 'e',
		  11: 'f',
		  12: 'g',
		  13: 'h',
		  14: 'i',
		  15: 'j',
		  16: 'k',
		  17: 'l',
		  18: 'm',
		  19: 'n',
		  20: 'o',
		  21: 'p',
		  22: 'q',
		  23: 'r',
		  24: 's',
		  25: 't',
		  26: 'u',
		  27: 'v',
		  28: 'w',
		  29: 'x',
		  30: 'y',
		  31: 'z'
		  }

    mapped_int = b32_lookup.get(integer2map)

    return (mapped_int)



class bsky_tid_obj:
    '''
    Blue Sky - ATProto TID Generator spec:
    https://atproto.com/specs/record-key#record-key-type-tid

    Generate unique record id for bluesky posts, following
    more restrictive TID (time stamp identifier) format
    '''

    # Setup constants

    MAX_TID = (2**63)
    FULL_MASK_64b = (2**63) 
    FINAL_STRING_LENGTH = 13
    FIRST_BIT = 0b0

    # Max value for epoch as microseconds since UNIX epoch
    EPOCH_MAX = (2**53)
    
    # Max value for random part appended to Epoch/time 53 bits
    RANDO_MAX = (2**10) -1   
    RANDO_MASK_10b = (2**9)  # 512

    # Setup class-wide variables
    obj_seq = 0
    tinytics=0
    tinytics_man=4
    epoch_fracSeconds = 0
    
    
    
    def __init__(self,time_in: time = None):

        '''
        Standard init for now; might need to put some variables
        here (counter?)
        '''
        if time_in !=None:
            self.epoch_fracSeconds = time_in
        else: 
            self.epoch_fracSeconds = time.time() # grab systemtime at init
        #print (epoch_fracSeconds = time.time())

    
    def time_update(self):
        self.epoch_fracSeconds = time.time() # update from systime
        # print ("test: ", self.epoch_fracSeconds)
        return

  
        
    @classmethod
    def class_debug (cls):
        print ('class debug')
        print ('class info: ', cls)
        print (cls.tinytics, cls.tinytics_man)
        print (bsky_tid_obj)
        return

    def method(self):
        print ('Instance Debug')
        print ('time: ', self.epoch_fracSeconds)
        print (self)
        return 

    def print_time_info(self):
        print("Time Generated is: ",self.tid_generate())
        return
    
    def export_time_info(self):
        return self.tid_generate()
    
    @staticmethod
    def static_test_method():
        print ('static method')
        return
    
    def instance_debug(self):
        print ('Time now: ', self.epoch_fracSeconds)
        return
        
    def tid_generate(self)-> string:
        
        # epoch_uSeconds = math.trunc (time.time() * (10**7))
        # Deci-microseconds since unix epoch 
        # Second factor of 10 is to pad out time a bit
        # Started with 10 **6 factor, but rando part was clobbering it
        # So extended to 10 ** 7
        # Safe to probably go to 10 ** 8
        epoch_deci_uSeconds = math.trunc (self.epoch_fracSeconds * (10**7)) 

        '''
        Counter to prevent generating multiple identical ids in
        the same microsecond.
        Rollover at 10. Probably not needed.
        '''
        
        self.obj_seq = self.obj_seq +1
        if self.obj_seq == 10:
            self.obj_seq =0
            
        # bit_make_rando = self.MAXY_MASK_64b | epoch_deci_uSeconds
        bit_make_rando = self.RANDO_MASK_10b | epoch_deci_uSeconds


        # Generate some more info for unique id
        # This part could use more thought and work
        # Especially to generalize more under
        # Concurrency strategies and situations
        # A Euclidian distance between two time samples is generated and appended
        # To the sequence number to provide more variablity
        # Could be simplified or eliminated in most scenarios
        # Might be helpful in currency situation with some addendums
        
        u_time_one = self.epoch_fracSeconds
        u_time_two = time.time()
        delta_tics = u_time_two - u_time_one
        tinytics=math.frexp(u_time_two - u_time_one)

        p = [tinytics[0],tinytics[1]]

        tinytics_man = math.frexp(tinytics[0]) # man for mantissa

        q = [tinytics_man[0],tinytics_man[1]]

        dist = math.trunc(math.dist(p,q))

                
        # Build a rando number less than 1024
        num_1 = self.obj_seq * 100
        num_2 = dist
        num_3 = num_1 + num_2

        # Prepare to append to the main number
        rando_bits =  self.RANDO_MASK_10b | num_3

        append_rando = self.FULL_MASK_64b | rando_bits

        add_timo = append_rando | bit_make_rando

        # Mask back off the first of 64 bits
        
        flip_off_leadingbit = add_timo  ^ self.FULL_MASK_64b
        interim_result_int = flip_off_leadingbit # checks?

        # run through coding function

        # update time stamp
        # print ('epoch_deci_microSeconds: ', epoch_deci_uSeconds)
        # print ('interim result: ', interim_result_int)
        # print ('len interim result: ', interim_result_int.bit_length())
        result = bsky_convert2_b32(interim_result_int)
        self.time_update()
        return result
    
    


