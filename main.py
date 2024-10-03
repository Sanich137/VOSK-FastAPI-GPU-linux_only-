import uvicorn
import config
from utils.pre_start_init import app
import routes, models

if __name__ == '__main__':
    uvicorn.run(app, host=config.host, port=config.port)
