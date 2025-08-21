# Start from the fredericklab base container
FROM fredericklab/basecontainer:latest-release

# get build arguments
ARG BUILD_TIME
ARG BRANCH
ARG GITVERSION
ARG GITDIRECTVERSION
ARG GITSHA
ARG GITDATE

# set and echo environment variables
ENV BUILD_TIME=$BUILD_TIME
ENV BRANCH=$BRANCH
ENV GITVERSION=${GITVERSION}
ENV GITSHA=${GITSHA}
ENV GITDATE=${GITDATE}
ENV GITDIRECTVERSION=${GITDIRECTVERSION}

RUN echo "BRANCH: "$BRANCH
RUN echo "BUILD_TIME: "$BUILD_TIME
RUN echo "GITVERSION: "$GITVERSION
RUN echo "GITSHA: "$GITSHA
RUN echo "GITDATE: "$GITDATE
RUN echo "GITDIRECTVERSION: "$GITDIRECTVERSION

# Installing precomputed python packages
RUN uv pip install pillow 

# copy PICAchooser into container
COPY . /src/picachooser
RUN echo $GITVERSION > /src/picachooser/VERSION

# init and install picachooser
RUN uv pip install --upgrade pip
RUN cd /src/picachooser && \
    uv pip install .
RUN chmod -R a+r /src/picachooser

# clean up install directories
RUN rm -rf /src/picachooser/build /src/picachooser/dist

# security patches
RUN uv pip install "cryptography>=42.0.4" "urllib3>=1.26.17"

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
RUN chown -R $USER /src/$USER
RUN cp ~/.bashrc /home/$USER/.bashrc; chown $USER /home/$USER/.bashrc

WORKDIR /home/$USER
ENV HOME="/home/picachooser"

ENV IN_DOCKER_CONTAINER=1

RUN ldconfig
WORKDIR /tmp/

# set to non-root user and initialize mamba
USER picachooser
RUN /opt/miniforge3/mamba shell
RUN echo "mamba activate science" >> /home/picachooser/.bashrc

ENTRYPOINT ["/opt/miniforge3/envs/science/bin/PICAchooser_dispatcher"]

LABEL org.label-schema.build-date=$BUILD_TIME \
      org.label-schema.name="picachooser" \
      org.label-schema.description="PICAchooser - a lightweight GUI tool for sorting MELODIC ICA components" \
      org.label-schema.url="http://nirs-fmri.net" \
      org.label-schema.vcs-ref=$GITVERSION \
      org.label-schema.vcs-url="https://github.com/bbfrederick/picachooser" \
      org.label-schema.version=$GITVERSION
