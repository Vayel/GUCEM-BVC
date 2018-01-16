FROM grahamdumpleton/mod-wsgi-docker:python-3.5
RUN apt-get -y update
RUN apt-get -y install wget sqlite3 cron

ADD gdrive /usr/bin
RUN chmod +x /usr/bin/gdrive

RUN git clone https://github.com/Vayel/GUCEM-BVC /GUCEM-BVC
WORKDIR /GUCEM-BVC

RUN pip3.5 install virtualenv
RUN virtualenv tools/bvc -p python3

EXPOSE 8000

CMD ["/bin/bash"]
