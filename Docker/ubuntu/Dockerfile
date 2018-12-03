# FROM gcc:8.2
# FROM gcc:7.3
# FROM ubuntu:14.04
FROM ubuntu:16.04
WORKDIR /sources_docker
RUN apt-get update
RUN apt-get install -y build-essential python3 python3-pip zsh curl wget cmake ninja-build
RUN apt-get install -y software-properties-common
RUN add-apt-repository -y ppa:ubuntu-toolchain-r/test
RUN apt-get update
RUN apt-get install -y gcc-7 g++-7
RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-7 80 && \
    update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-7 80
RUN apt-get install -y git
RUN pip3 install click
RUN wget https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh -O - | zsh || true

# update cmake
RUN cd / && \
    wget --no-verbose https://github.com/Kitware/CMake/releases/download/v3.13.1/cmake-3.13.1-Linux-x86_64.tar.gz && \
    tar xvf cmake-3.13.1-Linux-x86_64.tar.gz && \
    echo "export PATH=/cmake-3.13.1-Linux-x86_64/bin:$PATH" >> /root/.zshrc

# add opengl support
RUN apt-get install -y libgl1-mesa-dev

RUN echo "export LC_ALL=C.UTF-8" >> /root/.zshrc && \
    echo "export LANG=C.UTF-8" >> /root/.zshrc && \
    echo "alias python=python3" >> /root/.zshrc
