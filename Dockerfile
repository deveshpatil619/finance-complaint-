# FROM python:3.8.2-slim-buster
##  the docker build command, it creates an image that can be run as a container.
FROM ubuntu:20.04  
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/
RUN apt-get update -y \
&& apt-get install -y software-properties-common \
&& add-apt-repository ppa:deadsnakes/ppa \
&& apt-get install openjdk-8-jdk -y \
&& apt-get install python3-pip -y \
&& export JAVA_HOME \
&& apt-get clean \
&& rm -rf /var/lib/apt/lists/*
ENV AIRFLOW_HOME="/app/airflow"
ENV AIRFLOW__CORE__DAGBAG_IMPORT_TIMEOUT=1000
ENV AIRFLOW__CORE__ENABLE_XCOM_PICKLING=True
ENV PYSPARK_PYTHON=/usr/bin/python3
ENV PYSPARK_DRIVER_PYTHON=/usr/bin/python3
USER root
RUN mkdir /app
COPY . /app/
WORKDIR /app/
RUN pip3 install -r requirements.txt
RUN airflow db init 
RUN airflow users create  -e avnish@ineuron.ai -f Avnish -l Yadav -p admin -r Admin  -u admin
RUN chmod 777 start.sh
ENTRYPOINT [ "/bin/sh" ]
CMD ["start.sh"]

### This Dockerfile starts with the FROM instruction, which specifies the base image to use for the container. In this case, it is using the ubuntu:20.04 image.

##The next instruction is ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/ is used to set environment variable JAVA_HOME to the specified path.

##The RUN instruction is used to run command on top of the base image. This Dockerfile runs several apt-get commands to update the package lists, install Java 8 and Python 3, and add an external repository to install python package.

##The next set of ENV instruction is used to set the environment variable for airflow.

##The USER instruction is used to set the default user for the container.

##The RUN instruction is used to create a directory, copy the contents of the host machine to the container, and install the python packages.

##RUN pip3 install -r requirements.txt is used to install the python packages specified in the requirements.txt file. This file typically lists all the dependencies that the application needs to run. The pip3 install command installs these packages in the container.

##The second command RUN airflow db init is used to initialize the airflow database. This command creates the necessary database tables for airflow to function properly.

##The third command RUN airflow users create -e avnish@ineuron.ai -f Avnish -l Yadav -p admin -r Admin -u admin is used to create a new user in the airflow with the information provided as arguments.

## The fourth command RUN chmod 777 start.sh is used to change the permissions of the file start.sh to 777 (read, write, execute permissions for all users) so that it can be executed when the container starts.

##The ENTRYPOINT instruction is used to configure the container to run as an executable.

##The CMD instruction is used to run a command when the container starts. In this case, it runs a script called "start.sh".

##When you run the container, it runs the script start.sh and start the airflow scheduler and web server.