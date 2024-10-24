# Start from the fredericklab base container
FROM fredericklab/basecontainer:latest-release

# get build arguments
ARG BUILD_TIME
ARG BRANCH
ARG GITVERSION
ARG GITSHA
ARG GITDATE

# set and echo environment variables
ENV BUILD_TIME=$BUILD_TIME
ENV BRANCH=$BRANCH
ENV GITVERSION=${GITVERSION}
ENV GITSHA=${GITSHA}
ENV GITDATE=${GITDATE}

RUN echo "BRANCH: "$BRANCH
RUN echo "BUILD_TIME: "$BUILD_TIME
RUN echo "GITVERSION: "$GITVERSION
RUN echo "GITSHA: "$GITSHA
RUN echo "GITDATE: "$GITDATE

# Switch to root
USER root

# Installing precomputed python packages
RUN uv pip install pillow 

# Install PICAchooser
COPY . /src/picachooser
RUN echo $GITVERSION > /src/picachooser/VERSION
RUN cd /src/picachooser && \
    uv pip install . && \
    rm -rf /src/picachooser/build /src/picachooser/dist

# clean up
RUN pip cache purge

# Create a shared $HOME directory
ENV USER=picachooser
RUN useradd \
    --create-home \
    --shell /bin/bash \
    --groups users \
    --home /home/$USER \
    $USER
RUN cp ~/.bashrc /home/$USER/.bashrc; chown $USER /home/$USER/.bashrc

WORKDIR /home/$USER
ENV HOME="/home/$USER"

ENV IS_DOCKER_8395080871=1

RUN ldconfig
WORKDIR /tmp/

# set to non-root user and initialize mamba
USER $USER
RUN /opt/miniforge3/bin/mamba init

ENTRYPOINT ["/opt/miniforge3/envs/science/bin/PICAchooser_dispatcher"]

LABEL org.label-schema.build-date=$BUILD_TIME \
      org.label-schema.name="picachooser" \
      org.label-schema.description="PICAchooser - a lightweight GUI tool for sorting MELODIC ICA components" \
      org.label-schema.url="http://nirs-fmri.net" \
      org.label-schema.vcs-ref=$GITVERSION \
      org.label-schema.vcs-url="https://github.com/bbfrederick/picachooser" \
      org.label-schema.version=$GITVERSION
