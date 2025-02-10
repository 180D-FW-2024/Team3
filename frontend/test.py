# from scale_reader import get_weight_in_grams
# from thermometer_reader import get_current_temperature_f

# # print(get_current_temperature_f())
# # print(get_weight_in_grams())

from recipe_handler import CountdownTimer
import time

timer = CountdownTimer(5)
timer.start()
time.sleep(2)
print(timer.time_left())