FROM python:3-slim AS builder
COPY src/main.py requirements.txt /
RUN chmod 0755 /main.py

# The builder stage saves us only the chmod
FROM python:3-slim
COPY --from=builder /main.py /requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt
ENTRYPOINT ["/main.py"]