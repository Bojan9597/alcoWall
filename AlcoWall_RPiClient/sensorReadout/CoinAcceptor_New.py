import time
from IPython.terminal.embed import InteractiveShellEmbed
import os
import serial
import time
from struct import unpack
import threading
from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication

from serial.tools import list_ports
from struct import unpack
#test for ota
def find_coin_acceptor():
    ports = list_ports.comports()
    print(ports)
    print("Finding coin acceptor...")
    for port in ports:
        if "ttyACM" in port.device:  # Filters tty devices (e.g., /dev/ttyACM0)
            return port.device
    return None
    raise Exception("Coin acceptor not found. Ensure it is connected.")

def make_msg(code, data=None, to_slave_addr=2, from_host_addr=1):

    if not data:
        seq = [to_slave_addr, 0, from_host_addr, code]
    else:
        seq = [to_slave_addr, len(data), from_host_addr, code] + data
    message_sum = 0
    for i in seq:
        message_sum += i
    end_byte = 256 - (message_sum%256)
    message = seq + [end_byte]
    return message

def read_message(serial_object):
    serial_object.timeout = 1
    serial_object.inter_byte_timeout = 0.1  # Should be 0.05 but Linux doesn't support it

    header = serial_object.read(4)
    if len(header) < 4:
        return False

    # header: destination, length, source, message_id
    message_length = header[1] + 1  # Use the integer value directly
    body = serial_object.read(message_length)

    if len(body) < message_length:
        return False

    reply = list(header + body)  # Combine and convert to a list of bytes

    # TODO: Add checksum validation here
    return reply

def send_message_and_get_reply(serial_object, message, verbose=False):
    if not serial_object.isOpen():
        msg = 'The serial port is not open.'
        raise UserWarning(msg, (serial_object.isOpen()))

    # Convert message to bytes
    packet = bytes(message['message'])  # Fix: Ensure message is bytes
    serial_object.reset_input_buffer()
    serial_object.reset_output_buffer()

    # Send message
    serial_object.write(packet)

    # Read and process response
    output = read_message(serial_object)
    reply = read_message(serial_object)

    if not reply or reply[0] != 1:
        return False 

    reply_length = reply[1]
    expected_length = message['bytes_expected']
    reply_type = message['type_returned']

    if len(reply) < 2:
        print('Received small message: {0}'.format(reply))
        return False

    if verbose:
        print("Received {0} bytes:".format(len(reply)))

    if expected_length != -1 and reply_length != expected_length:
        print('Expected {1} bytes but received {0}'.format(reply_length, expected_length))
        return False

    reply_data = reply[4:-1]
    
    # Return parsed data based on type
    if reply_type is str:
        return str().join(map(chr, reply_data))
    elif reply_type is int:
        return reply_data
    elif reply_type is bool:
        return True
    else:
        return list(map(chr, reply))


def make_serial_object(tty_port):
    return serial.Serial(port=tty_port,
                         baudrate=9600,
                         parity=serial.PARITY_NONE,
                         stopbits=serial.STOPBITS_ONE,
                         bytesize=serial.EIGHTBITS,
                         xonxoff=True,
                         )

def drop_to_ipython(local_variables, *variables_to_inspect):
    try:
        call_name = local_variables['self'].__module__
    except Exception:
        call_name = "Module"

    b = 'Dropping into IPython'
    em = 'Leaving Interpreter, back to program.'
    msg = '***Called from %s. Hit Ctrl-D to exit interpreter and continue program.'
    ipshell = InteractiveShellEmbed([], banner1=b, exit_msg=em)
    ipshell(msg %(call_name))



def log(message, verbose=False):
    if verbose:
        print('Requesting: {0}'.format(message['user_message']))

class CoinMessenger(object):
    """This is an object used to talk with ccTalk coin validators.

    It provides functions for requesting and recieving data as
    well as changing the state of the coin validator.
    """
    
    r_info = dict(reset_device=(1, 0, bool),
                  comms_revision=(4, 3, int),              # Expected: 2, 4, 2
                  alarm_counter=(176,1,int),
                  bank_select=(178,1,int),
                  build_code=(192, -1, str),
                  reject_counter=(193,3,int),
                  fraud_counter=(194,3,int),
                  teach_status=(201,2,int),
                  option_flags=(213,1,int),
                  data_storage_availability=(216, 5, int),
                  accept_counter=(225,3,int),
                  insertion_counter=(226,3,int),
                  master_inhibit_status=(227, 1, int),
                  read_buffered_credit_or_error_codes=(229, 11, int),
                  inhibit_status=(230, 2, int),
                  perform_self_check=(232,-1,int),
                  software_revision=(241, -1, str),
                  serial_number=(242, 3, int),
                  database_version=(243, 1, int),
                  product_type=(244, -1, str),
                  equipment_category=(245, -1, str),      # Expected: Coin Acceptor
                  manufacturer_ID=(246, -1, str),
                  variable_set=(247, -1, int),
                  polling_priority=(249, 2, int),
                  simple_poll=(254, 0, bool),
                  )

    
    def __init__(self, serial_object, verbose = False):
        self.credit = 0
        self.serial_object = serial_object
        self.request_data = {}
        self.verbose = verbose
        for k, v in list(self.r_info.items()):
            self.request_data[k] = dict(message=make_msg(v[0]),
                                        request_code=v[0],
                                        bytes_expected=v[1],
                                        bytes_sent=0,
                                        type_returned=v[2],
                                        user_message=k,
                                        )

    def accept_coins(self, mask=[255,255]):
        """Change accept coin state.

        Parameters
        ----------
        state : bool
          State to change the coin validator too.

        Raises
        ------
        UserWarning
          -- If the state is not True or False.
          -- If self.serial_object.isOpen() is False.
        """

        if len(mask) != 2:
            msg = "accept_coins mask must be a 2-ple."
            raise UserWarning(msg, (self.serial_object.isOpen()))

        ph = dict(message=make_msg(231, mask),
                  request_code=231,
                  bytes_expected=0,
                  bytes_sent=2,
                  type_returned=bool,
                  user_message='modify_inhibit_status_{0}'.format(mask),
                  )

        log(ph, verbose=self.verbose)
        reply_msg = send_message_and_get_reply(self.serial_object, ph, verbose=self.verbose)
        return reply_msg

    def master_inhibit(self, state=True):
        if state:
            param = 0
        else:
            param = 1
 
        ph = dict(message=make_msg(228, [param]),
                  request_code=228,
                  bytes_expected=0,
                  bytes_sent=1,
                  type_returned=bool,
                  user_message='modify_master_inhibit_status_{0}'.format(state),
                  )
        log(ph, verbose=self.verbose)
        reply_msg = send_message_and_get_reply(self.serial_object, ph, verbose=self.verbose)
        return reply_msg

    def set_accept_limit(self, coins=1):
        if type(coins) != type(int()):
            msg = 'The number of coins must be an integer.'
            raise UserWarning(msg, (coins, type(coins)))

        ph = dict(message=make_msg(135, [coins]),
                  request_code=135,
                  bytes_expected=0,
                  bytes_sent=1,
                  type_returned=bool,
                  user_message='set_accept_limit_{0}'.format(coins),
                  )
        log(ph, verbose=self.verbose)
        reply_msg = send_message_and_get_reply(self.serial_object, ph, verbose=self.verbose)
        print(reply_msg)

    def read_buffer(self):
        """Shortcut for self.request('read_buffered_credit_or_error_codes')

        Returns
        -------
        output : output from self.request('read_buffered_credit_or_error_codes')
        """
        return self.request('read_buffered_credit_or_error_codes')

    def get_coin_id(self, slot):
        """Prints out the coin id for a slot number.

        Parameters
        ----------
        slot : int
          Slot number.
        """
        ph = dict(message=make_msg(184, [slot]),
                  request_code=184,
                  bytes_expected=6,
                  bytes_sent=1,
                  type_returned=str,
                  user_message='get_coin_id_{0}'.format(slot),
                  )
        log(ph, verbose=self.verbose)
        reply_msg = send_message_and_get_reply(self.serial_object, ph, verbose=self.verbose)
        return reply_msg

    def modify_coin_id(self, slot, text):
        text_raw = list(map(ord,'{:.<6}'.format(text)))
        ph = dict(message=make_msg(185, [slot] + text_raw),
                  request_code=185,
                  bytes_expected=0,
                  bytes_sent=7,
                  type_returned=bool,
                  user_message='modify_coin_id_{0}_{1}'.format(slot,text),
                  )
        log(ph, verbose=self.verbose)
        reply_msg = send_message_and_get_reply(self.serial_object, ph, verbose=self.verbose)
        return reply_msg

    def teach_mode_control(self, slot):
        ph = dict(message=make_msg(202, [slot]),
                  request_code=202,
                  bytes_expected=0,
                  bytes_sent=1,
                  type_returned=bool,
                  user_message='teach_mode_control_{0}'.format(slot),
                  )
        log(ph, verbose=self.verbose)
        reply_msg = send_message_and_get_reply(self.serial_object, ph, verbose=self.verbose)
        return reply_msg

    def request(self, request_key):
        r_dic = self.request_data.get(request_key, None)
        if not r_dic:
            msg = 'This request_key has not been implemented.'
            raise NotImplementedError(msg, (request_key))

        log(r_dic, verbose=self.verbose)
        reply_msg = send_message_and_get_reply(self.serial_object, r_dic, verbose=self.verbose)

        return reply_msg
      

class CoinAcceptor:
    def __init__(self):
        port = find_coin_acceptor()
        if not port:
            QApplication.quit()
            
        coin_validator_connection = make_serial_object(port)
        self.coin_messenger = CoinMessenger(coin_validator_connection)
        self.coin_messenger.set_accept_limit(25)
        self.credit = 0
        self.coin_dic = {4: 100, 1: 10, 2: 20, 3: 50, 5: 200, 6: 500}

    def reject_all_coins(self):
        """Send command to the coin acceptor to reject all coins."""
        try:
            self.coin_messenger.master_inhibit(state=True)  # Disable coin acceptance
            print("Coin acceptor is now rejecting all coins.")
        except Exception as e:
            print(f"Error rejecting all coins: {e}")

    def accept_all_coins(self):
        """Send command to the coin acceptor to accept all coins."""
        try:
            self.coin_messenger.master_inhibit(state=False)  # Enable coin acceptance
            print("Coin acceptor is now accepting all coins.")
        except Exception as e:
            print(f"Error accepting all coins: {e}")

    def get_credit(self):
        with threading.Lock():
            return self.credit
        
    def update_credit(self, credit):
        with threading.Lock():
            self.credit += credit

    def set_credit(self, credit):
        with threading.Lock():
            self.credit = credit

    def get_coin_type(self):
        
        self.coin_messenger.accept_coins(mask=[255, 255])  # Enable all coins
        print("Coin validator enabled. Waiting for coins...")
        self.accept_all_coins()
        last_status_number = 0
        try:
            status = self.coin_messenger.request('read_buffered_credit_or_error_codes')
            if status and len(status) > 1:
                last_status_number = status[0]
            else:
                #exit application if no coin is inserted
                QApplication.quit()
                return
            while True:
                status = self.coin_messenger.request('read_buffered_credit_or_error_codes')
                if status and len(status) > 1 and status[0] != last_status_number:
                    last_status_number = status[0]
                    coin_code = status[1]  # Coin ID received
                    coin_value = self.coin_dic.get(coin_code, None)
                    if coin_value is not None:
                        print(f"Coin inserted: {coin_value}")
                        self.update_credit(coin_value)
                        

                time.sleep(0.1)  # Adjust polling interval for performance
        except KeyboardInterrupt:
            print("Exiting coin listening loop.")
            return



def main():
    try:
        # Start listening for coins
        coin_listener = CoinAcceptor()
        coin_listener.get_coin_type()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
