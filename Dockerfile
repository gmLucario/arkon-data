FROM python:3.8 AS artifact

ENV TZ=America/Mexico_City
RUN ln -snf /usr/share/zoneinfo/America/Mexico_City /etc/localtime \
        && echo America/Mexico_City > /etc/timezone

RUN useradd --create-home arkondata

RUN apt-get update \
    && apt-get install -y \
    ipython \
    bc \
    && rm -rf /var/lib/apt/lists/*


FROM artifact
COPY assets/requirements.txt /
RUN pip install -r requirements.txt --no-cache-dir
COPY src/ /src
RUN chown -R 1000:1000 /src
USER 1000:1000
WORKDIR /src
CMD ["uvicorn", "main:app", "--app-dir","./","--host", "0.0.0.0", "--port", "8000"]