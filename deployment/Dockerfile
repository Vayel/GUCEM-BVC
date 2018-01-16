FROM grahamdumpleton/mod-wsgi-docker:python-3.5
RUN apt-get -y update
RUN apt-get -y install wget sqlite3 cron
RUN pip3.5 install virtualenv

ADD gdrive /usr/bin
RUN chmod +x /usr/bin/gdrive

RUN useradd -ms /bin/bash bvc
USER bvc

RUN git clone https://github.com/Vayel/GUCEM-BVC /home/bvc/GUCEM-BVC
WORKDIR /home/bvc/GUCEM-BVC

RUN virtualenv tools/bvc -p python3

EXPOSE 8000

CMD ["/bin/bash"]
