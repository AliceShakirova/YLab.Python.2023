from src.app import app

if __name__ == '__main__':
    # from src.background_worker import celery_app
    # celery_app.worker_main(['worker'])

    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
