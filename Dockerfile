FROM python:3.12.4-alpine

WORKDIR /haldis

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

VOLUME hlds_files/

ENTRYPOINT ["python", "main.py"]
CMD []

# docker build -t haldis-een-prijsje .
# docker run -v $(pwd)/hlds_files:/haldis/hlds_files haldis-een-prijsje
