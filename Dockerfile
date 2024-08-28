FROM python:3.9
# set work directory
WORKDIR /usr/src/tg_stat_bot/
# copy project
COPY . /usr/src/tg_stat_bot/
# install dependencies
#RUN pip install --upgrade pip
RUN pip install --user -r requirements.txt

FROM joyzoursky/python-chromedriver:3.8
WORKDIR /src
COPY requirements.txt /src
RUN pip install -r requirements.txt
COPY . /src

# run app
CMD ["python", "-m", "main"]
