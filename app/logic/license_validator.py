# ===== IMPORTS & DEPENDENCIES =====
import datetime
import ntplib
from socket import timeout
import base64

# ===== CONFIGURATION & CONSTANTS =====
BASE_DATE = datetime.datetime(2001, 1, 1)

# This is the only value you need to keep.
ENCODED_OFFSET_DAYS = 'OTA5NA==' 

# --- NTP SERVER for reliable time checking ---
NTP_SERVER = 'ir.pool.ntp.org'


# ===== CORE BUSINESS LOGIC =====
class LicenseValidator:
    """
    Handles the application's expiration check in a secure and robust way.
    """
    def __init__(self):
        self._expiration_date = self._decode_expiration_date()

    def _decode_expiration_date(self):
        """Decodes the obfuscated date string to a datetime object."""
        try:
            # Decode the base64 string to get the number of days
            decoded_days_str = base64.b64decode(ENCODED_OFFSET_DAYS).decode('utf-8')
            offset_days = int(decoded_days_str)
            
            # Calculate the final expiration date by adding the offset to the base date
            expiration = BASE_DATE + datetime.timedelta(days=offset_days)
            # Set time to the end of the day for consistency
            return expiration.replace(hour=23, minute=59, second=59)
        except Exception:
            # If decoding fails for any reason, default to a safe past date
            return datetime.datetime(2000, 1, 1)

    def _get_network_time(self):
        """
        Attempts to get the current time from a trusted NTP server.
        Returns a datetime object or None if it fails.
        """
        try:
            client = ntplib.NTPClient()
            response = client.request(NTP_SERVER, version=3, timeout=2)
            return datetime.datetime.fromtimestamp(response.tx_time)
        except (ntplib.NTPException, timeout, ConnectionRefusedError, OSError):
            return None

    def get_current_time(self):
        """
        Gets the current time, prioritizing network time and falling back to local time.
        Returns a tuple of (datetime, source_string).
        """
        network_time = self._get_network_time()
        if network_time:
            return network_time, "Network"
        else:
            return datetime.datetime.now(), "Local"

    def check_status(self):
        """
        Checks if the application license has expired.

        Returns:
            A tuple (is_expired: bool, message: str)
        """
        current_time, time_source = self.get_current_time()
        
        if self._expiration_date and current_time > self._expiration_date:
            expiration_date_str = self._expiration_date.strftime('%Y-%m-%d')
            message = (
                f"این نسخه از برنامه منقضی شده و نسخه جدید در دسترس است.\n"
                f"لطفاً برای دریافت نسخه جدید با سازنده برنامه تماس بگیرید"
            )
            return True, message
        
        return False, "OK"