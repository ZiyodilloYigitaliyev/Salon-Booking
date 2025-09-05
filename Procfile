web: gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --workers ${WEB_CONCURRENCY:-1} --timeout 120 --log-file -
# (ixtiyoriy) release bosqichida migratsiya
release: alembic upgrade head
