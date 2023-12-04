from codelearn.example.gpts_action.api import app
from codelearn.storage.project_db import init_db



init_db()

# Dockerfile for containerization can be created separately

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)