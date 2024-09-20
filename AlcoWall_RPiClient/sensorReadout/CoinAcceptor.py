import time
import RPi.GPIO as GPIO
import threading

class CoinAcceptor:
    def __init__(self, input_pin=17):
        self.input_pin = input_pin
        self.pulse_count = 0
        self.credit = 0
        self.last_pulse_time = time.time()

        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.input_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.input_pin, GPIO.RISING, callback=self.coin_detected, bouncetime=5)

    def coin_detected(self, channel):
        current_time = time.time()
        if current_time - self.last_pulse_time > 0.5:
            self.pulse_count = 0  # Reset pulse count after timeout
        self.pulse_count += 1
        self.last_pulse_time = current_time

    def check_credits(self):
        if self.pulse_count == 1:
            self.update_credit(0.5)
            print("added 0.5 coins")
        elif self.pulse_count == 5:
            self.update_credit(1)
            print(f"Added 1 credit")
        elif self.pulse_count == 10:
            self.update_credit(2)
            print(f"Added 2 credits.")
        self.pulse_count = 0  # Reset pulse count after updating credits
    
    def get_credit(self):
        with threading.Lock():
            return self.credit
        
    def update_credit(self, credit):
        with threading.Lock():
            self.credit += credit

    def set_credit(self, credit):
        with threading.Lock():
            self.credit = credit

    def run(self):
        try:
            while True:
                time.sleep(0.1)  # Reduced sleep time for more responsive checks
                if time.time() - self.last_pulse_time > 0.5 and self.pulse_count > 0:
                    self.check_credits()

        except KeyboardInterrupt:
            GPIO.cleanup()  # Clean up GPIO on CTRL+C exit

    def cleanup(self):
        GPIO.cleanup()  # Clean up GPIO on normal exit



# Usage
if __name__ == "__main__":
    acceptor = CoinAcceptor()
    acceptor.run()
