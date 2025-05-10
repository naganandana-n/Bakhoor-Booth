# weight test
from hx711 import HX711
import time

hx = HX711(dout_pin=18, pd_sck_pin=15)
hx.reset()
hx.zero()

ratio = 21.81341463414634  # (your calibration ratio)
hx.set_scale_ratio(ratio)

while True:
    weight = hx.get_weight_mean()
    weight_kg = max(weight / 1000.0, 0.0)
    print(f"Weight: {weight_kg:.2f} kg")
    time.sleep(1)