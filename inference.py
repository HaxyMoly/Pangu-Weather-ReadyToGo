import os
import numpy as np
import onnx
import onnxruntime as ort
from datetime import datetime, timedelta
# Use GPU or CPU
use_GPU = False

# The date and time of the initial field
# date = '2023-07-03'
date_time = datetime(
    year=2023, 
    month=7, 
    day=11,
    hour=23,
    minute=0)
# time = '23:00'

# The date and time of the final approaches
date_time_final = datetime(
    year=2023, 
    month=7, 
    day=17,
    hour=11,
    minute=0)

final_result_dir = os.path.join(
    os.path.join(os.getcwd(), "results"),
    (date_time.strftime("%Y-%m-%d-%H-%M") + "to" + date_time_final.strftime("%Y-%m-%d-%H-%M"))
)
os.makedirs(final_result_dir,exist_ok=True)

temp_dir = os.path.join(os.getcwd(), "temp")
os.makedirs(temp_dir,exist_ok=True)
## copy forecast files to temp dir

model_24 = 'models/pangu_weather_24.onnx' # 24h
model_6 = 'models/pangu_weather_6.onnx' # 6h
model_3 = 'models/pangu_weather_3.onnx' # 3h
model_1 = 'models/pangu_weather_1.onnx' # 1h



# The directory for forecasts
forecast_dir = os.path.join(
    os.path.join(os.getcwd(), "forecasts"),
    ## replace to prevent invaild char ":"
    date_time.strftime("%Y-%m-%d-%H-%M")
)
# Calculate the order of models should be used to generate the final result
time_difference_in_hour = (date_time_final - date_time).total_seconds() / 3600
current_date_time = date_time
last_date_time = None
model_used = None
start = True
ort_session = None
jump = False
while time_difference_in_hour >= 1:
    print(time_difference_in_hour)
    last_model = model_used
    if time_difference_in_hour >= 24:
        model_used = model_24
        time_difference_in_hour -= 24
        current_date_time += timedelta(hours=24)
        print("24")
    elif time_difference_in_hour >= 6:
        model_used = model_6
        time_difference_in_hour -= 6
        current_date_time += timedelta(hours=6)
        print("6")
    elif time_difference_in_hour >= 3:
        model_used = model_3
        time_difference_in_hour -= 3
        current_date_time += timedelta(hours=3)
        print("3")
    elif time_difference_in_hour >= 1:
        model_used = model_1
        time_difference_in_hour -= 1
        current_date_time += timedelta(hours=1)
        print("1")
    if model_used == last_model:
        jump = True
    else:
        jump = False
    print(current_date_time.strftime("%Y-%m-%d-%H-%M"))

    if not jump:
        # Load the model
        model = onnx.load(model_used)

        # Set the behavier of onnxruntime
        options = ort.SessionOptions()
        options.enable_cpu_mem_arena=False
        options.enable_mem_pattern = False
        options.enable_mem_reuse = False
        # Increase the number for faster inference and more memory consumption
        options.intra_op_num_threads = 30

        # Set the behavier of cuda provider
        cuda_provider_options = {'arena_extend_strategy':'kSameAsRequested',}

        # Initialize onnxruntime session for Pangu-Weather Models
        if use_GPU:
            ort_session = ort.InferenceSession(model_used, sess_options=options, providers=[('CUDAExecutionProvider', cuda_provider_options)])
        else:
            ort_session = ort.InferenceSession(model_used, sess_options=options, providers=['CPUExecutionProvider'])

    print("start")
    # Load the upper-air numpy arrays
    # Load the surface numpy arrays
    input = None
    input_surface = None
    if start:
        input = np.load(os.path.join(forecast_dir, 'input_upper.npy')).astype(np.float32)
        input_surface = np.load(os.path.join(forecast_dir, 'input_surface.npy')).astype(np.float32)
    else:
        input = np.load(os.path.join(final_result_dir, 'output_upper_'+last_date_time.strftime("%Y-%m-%d-%H-%M")+'.npy')).astype(np.float32)
        input_surface = np.load(os.path.join(final_result_dir, 'output_surface_'+last_date_time.strftime("%Y-%m-%d-%H-%M")+'.npy')).astype(np.float32)

    # Run the inference session
    output, output_surface = ort_session.run(None, {'input':input, 'input_surface':input_surface})
    # Save the results
    np.save(os.path.join(final_result_dir, 'output_upper_'+current_date_time.strftime("%Y-%m-%d-%H-%M")), output)
    np.save(os.path.join(final_result_dir, 'output_surface_' + current_date_time.strftime("%Y-%m-%d-%H-%M")), output_surface)
    last_date_time = current_date_time
    start = False
