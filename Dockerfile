FROM python:3.7.0-alpine
RUN pip install -q requests==2.18.4 
RUN mkdir /code /tmp/out
ENV DISCOVERY_URL= \
	SERVICE_REPO_NAME= \
	INITIAL_DELAY=1 \
	REFRESH_INTERVAL=10
VOLUME /tmp/out
ADD ./download_sd.py /code/
CMD python /code/download_sd.py $DISCOVERY_URL $SERVICE_REPO_NAME /tmp/out/file_sd $INITIAL_DELAY $REFRESH_INTERVAL