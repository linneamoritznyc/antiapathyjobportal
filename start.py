import uvicorn
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'v2', 'api'))

if __name__ == "__main__":
    uvicorn.run(
        "index:app",
        host="0.0.0.0",
        port=5000,
        reload=False,
        app_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'v2', 'api')
    )
