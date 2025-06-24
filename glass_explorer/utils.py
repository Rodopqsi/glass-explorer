import screen_brightness_control as sbc
import pywifi
from PIL import Image

# BRILLO
def set_brightness(level: int):
    sbc.set_brightness(level)

def get_brightness():
    return sbc.get_brightness(display=0)

# WIFI
def scan_wifi():
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]
    iface.scan()
    return iface.scan_results()

def connect_wifi(ssid, password):
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]
    profile = pywifi.Profile()
    profile.ssid = ssid
    profile.key = password
    profile.auth = pywifi.const.AUTH_ALG_OPEN
    profile.akm.append(pywifi.const.AKM_TYPE_WPA2PSK)
    profile.cipher = pywifi.const.CIPHER_TYPE_CCMP
    iface.remove_all_network_profiles()
    iface.connect(iface.add_network_profile(profile))

def get_current_wifi():
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]
    return iface.status()

def image_to_ascii(path, width=40):
    img = Image.open(path)
    img = img.convert('L')
    aspect = img.height / img.width
    img = img.resize((width, int(width * aspect / 2)))
    chars = "@%#*+=-:. "
    pixels = img.getdata()
    ascii_str = ""
    for i, pixel in enumerate(pixels):
        ascii_str += chars[pixel // 25]
        if (i + 1) % width == 0:
            ascii_str += "\n"
    return ascii_str