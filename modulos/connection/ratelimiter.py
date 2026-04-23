import time
import threading

# ==============================================================================================
# CONTROLADOR DE RATE LIMITER
# ==============================================================================================
class RateLimiter:
    """Implementa un mecanismo de control de tasa para limitar,
    la cantidad de solicitudes realizadas en un período de tiempo determinado."""
    def __init__(self, rate=40, per=1):
        self.rate = rate
        self.per = per
        self.allowance = rate
        self.last_check = time.time()
        self.lock = threading.Lock()

    def wait(self):
        """Espera el tiempo necesario para cumplir con el límite de tasa antes de permitir la siguiente solicitud."""
        with self.lock:

            current = time.time()
            time_passed = current - self.last_check
            self.last_check = current

            self.allowance += time_passed * (self.rate / self.per)

            if self.allowance > self.rate:
                self.allowance = self.rate

            if self.allowance < 1:
                sleep_time = (1 - self.allowance) * (self.per / self.rate)
                time.sleep(sleep_time)
                self.allowance = 0
            else:
                self.allowance -= 1