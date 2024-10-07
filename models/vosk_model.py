import sys

if sys.platform == "win32":
    from vosk import Model, GpuInit, GpuThreadInit

elif sys.platform == "linux":
    from vosk import GpuInit, GpuThreadInit, BatchModel

elif sys.platform == "darwin":
    from vosk import Model, GpuInit, GpuThreadInit

else:
    raise TypeError("Unsupported platform")

from utils.pre_start_init import paths

GpuInit()
# GpuThreadInit()

model = BatchModel(str(paths.get("model_full_gpu")))

