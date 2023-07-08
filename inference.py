import os
import numpy as np
import onnx
import onnxruntime as ort

# Use GPU or CPU
use_GPU = False

# The date and time of the initial field
date = '2023-07-02'
time = '23:00'

# Uncomment the model to be used
model_used = 'models/pangu_weather_24.onnx' # 24h
# model_used = 'models/pangu_weather_6.onnx' # 6h
# model_used = 'models/pangu_weather_3.onnx' # 3h
# model_used = 'models/pangu_weather_1.onnx' # 1h

# The directory for forecasts
forecast_dir = 'forecasts/' + date + '-' + time + '/'

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

# Load the upper-air numpy arrays
input = np.load(os.path.join(forecast_dir, 'input_upper.npy')).astype(np.float32)
# Load the surface numpy arrays
input_surface = np.load(os.path.join(forecast_dir, 'input_surface.npy')).astype(np.float32)

# Run the inference session
output, output_surface = ort_session.run(None, {'input':input, 'input_surface':input_surface})
# Save the results
np.save(os.path.join(forecast_dir, 'output_upper'), output)
np.save(os.path.join(forecast_dir, 'output_surface'), output_surface)