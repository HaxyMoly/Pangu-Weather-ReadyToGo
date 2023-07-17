import os
from datetime import datetime
from forecast_decode_functions import surface, upper

# The date and time of the initial field
date_time = datetime(
    year=2023, 
    month=7, 
    day=11,
    hour=23,
    minute=0)
date_time_final = datetime(
    year=2023,
    month=7,
    day=17,
    hour=11,
    minute=0)
 
# The directory for results forecast
results_dir = os.path.join(
    os.path.join(os.getcwd(), "results"),
    date_time.strftime("%Y-%m-%d-%H-%M") + "to" + date_time_final.strftime("%Y-%m-%d-%H-%M")
)
# The results for output
outputs_dir = os.path.join(
        os.path.join(os.getcwd(), "outputs"),
        date_time.strftime("%Y-%m-%d-%H-%M" + "to" + date_time_final.strftime("%Y-%m-%d-%H-%M"))
)
# create dir if needed
os.makedirs(outputs_dir,exist_ok=True)

# get all files that need to be decoded
for file in os.listdir(results_dir):
    print(file)
    if file.endswith(".npy"):
        if file.startswith("output_surface"):
            # decode surface data
            surface(os.path.join(results_dir, file),file[:-4]+".nc",outputs_dir)
        elif file.startswith("output_upper"):
            # decode upper data
            upper(os.path.join(results_dir, file),file[:-4]+".nc",outputs_dir)

