# Start from the fredericklab base container
FROM fredericklab/basecontainer:v0.2.1

# Installing precomputed python packages
RUN mamba install -y pillow 

# Install PICAchooser
COPY . /src/picachooser
RUN cd /src/picachooser && \
    pip install . && \
    rm -rf /src/picachooser/build /src/picachooser/dist

# clean up
RUN mamba clean -y --all
RUN pip cache purge

# Create a shared $HOME directory
RUN useradd -m -s /bin/bash -G users picachooser
WORKDIR /home/picachooser
ENV HOME="/home/picachooser"

ENV IS_DOCKER_8395080871=1

RUN ldconfig
WORKDIR /tmp/
ENTRYPOINT ["/usr/local/miniconda/bin/PICAchooser_dispatcher"]

# set a non-root user
USER picachooser

ARG VERSION
ARG BUILD_DATE
ARG VCS_REF

LABEL org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="picachooser" \
      org.label-schema.description="PICAchooser - a lightweight GUI tool for sorting MELODIC ICA components" \
      org.label-schema.url="http://nirs-fmri.net" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url="https://github.com/bbfrederick/picachooser" \
      org.label-schema.version=$VERSION 
