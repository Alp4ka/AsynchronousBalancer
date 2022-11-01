import uvicorn
import views
import argparse

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--host', type=str, required=False, default='0.0.0.0')
    arg_parser.add_argument('--port', type=int, required=False, default=8000)
    args = arg_parser.parse_args()

    uvicorn.run(views.app, host=args.host, port=args.port, reload=False)
