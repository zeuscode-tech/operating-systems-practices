FROM python:3.12-alpine

RUN addgroup -S app && adduser -S -G app -u 10001 app
WORKDIR /app
COPY --chown=app:app app.py /app/app.py
USER app
EXPOSE 8080
HEALTHCHECK --interval=10s --timeout=2s --retries=3 CMD wget -q -O- http://127.0.0.1:8080/health || exit 1
CMD ["python3", "/app/app.py"]
