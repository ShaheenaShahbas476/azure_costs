FROM python:3.12.0-alpine

ADD vmsamp.py .
RUN pip install requests psycopg2-binary schedule pystackql 



CMD ["python", "./vmsamp.py" ]