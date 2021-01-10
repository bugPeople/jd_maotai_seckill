FROM centos:7

ENV LANG en_US.UTF8

COPY . /app

WORKDIR /app

RUN curl -o /etc/yum.repos.d/CentOS-Base.repo https://mirrors.aliyun.com/repo/Centos-7.repo && \
    curl -o /etc/yum.repos.d/epel.repo http://mirrors.aliyun.com/repo/epel-7.repo && \
    yum clean all && yum makecache && \
    yum -y install gcc python3-pip python3-devel zbar zbar-devel zlib-devel libjpeg-turbo-devel && \
    pip3 install -r requirements.txt && \
    chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
