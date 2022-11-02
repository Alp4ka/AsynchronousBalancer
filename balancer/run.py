import uvicorn

from balancer import Balancer
from config import BalancerConfig
import views
import argparse

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--host', type=str, required=False, default='0.0.0.0')
    arg_parser.add_argument('--port', type=int, required=False, default=8000)
    arg_parser.add_argument('--config', type=str, required=False, default=None)
    args = arg_parser.parse_args()

    views.balancer = Balancer.from_config(BalancerConfig.from_xml(args.config))
    uvicorn.run(views.app, host=args.host, port=args.port, reload=False)
