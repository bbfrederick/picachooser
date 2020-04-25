# Use Ubuntu 18.04 LTS
FROM ubuntu:18.04

# Prepare environment
RUN df -h
RUN apt-get update
RUN apt-get install -y --no-install-recommends \
                    curl \
                    bzip2 \
                    ca-certificates \
                    xvfb \
                    build-essential \
                    autoconf \
                    libtool \
                    gnupg \
                    pkg-config \
                    xterm \
                    libgl1-mesa-glx \
                    libx11-xcb1 \
                    lsb-release \
                    git
RUN apt-get install -y --reinstall libqt5dbus5 
RUN apt-get install -y --reinstall libqt5widgets5 
RUN apt-get install -y --reinstall libqt5network5 
RUN apt-get install -y --reinstall libqt5gui5 
RUN apt-get install -y --reinstall libqt5core5a 
RUN apt-get install -y --reinstall libdouble-conversion1 
RUN apt-get install -y --reinstall libxcb-xinerama0
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

#ENV FSL_DIR="/usr/share/fsl/5.0" \
#    OS="Linux" \
#    FS_OVERRIDE=0 \
#    FIX_VERTEX_AREA="" \
#    FSF_OUTPUT_FORMAT="nii.gz" \
#    FREESURFER_HOME="/opt/freesurfer"

# Installing Neurodebian packages (FSL)
#RUN curl -sSL "http://neuro.debian.net/lists/$( lsb_release -c | cut -f2 ).us-ca.full" >> /etc/apt/sources.list.d/neurodebian.sources.list && \
#    apt-key add /usr/local/etc/neurodebian.gpg && \
#    (apt-key adv --refresh-keys --keyserver hkp://ha.pool.sks-keyservers.net 0xA5D32F012649A5A9 || true)

#RUN apt-get update && \
#    apt-get install -y --no-install-recommends \
#                    fsl-core=5.0.9-5~nd16.04+1 \
#                    fsl-mni152-templates=5.0.7-2 && \
#    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

#ENV FSLDIR="/usr/share/fsl/5.0" \
#    FSLOUTPUTTYPE="NIFTI_GZ" \
#    FSLMULTIFILEQUIT="TRUE" \
#    POSSUMDIR="/usr/share/fsl/5.0" \
#    LD_LIBRARY_PATH="/usr/lib/fsl/5.0:$LD_LIBRARY_PATH" \
#    FSLTCLSH="/usr/bin/tclsh" \
#    FSLWISH="/usr/bin/wish" \
#ENV PATH="/usr/lib/fsl/5.0:$PATH"


# Installing and setting up miniconda
RUN curl -sSLO https://repo.continuum.io/miniconda/Miniconda3-4.7.12.1-Linux-x86_64.sh && \
    bash Miniconda3-4.7.12.1-Linux-x86_64.sh -b -p /usr/local/miniconda && \
    rm Miniconda3-4.7.12.1-Linux-x86_64.sh


# Set CPATH for packages relying on compiled libs (e.g. indexed_gzip)
ENV PATH="/usr/local/miniconda/bin:$PATH" \
    CPATH="/usr/local/miniconda/include/:$CPATH" \
    LANG="C.UTF-8" \
    LC_ALL="C.UTF-8" \
    PYTHONNOUSERSITE=1

RUN conda install conda-build

# Installing precomputed python packages
RUN df -h
RUN conda config --add channels conda-forge
RUN df -h
RUN conda build purge-all
RUN df -h
RUN conda install -y python=3.7.4 \
                     pip=19.3.1 \
                     scipy=1.4.1 \
                     numpy=1.17.3 \
                     pillow=7.0.0 \
                     nibabel=2.5.1 \
                     pandas=0.25.3 \
                     pyqtgraph=0.10.0; sync && \
    chmod -R a+rX /usr/local/miniconda; sync && \
    chmod +x /usr/local/miniconda/bin/*; sync && \
    conda build purge-all; sync && \
    conda clean -tipsy && sync
RUN df -h


# Create a shared $HOME directory
RUN useradd -m -s /bin/bash -G users picachooser
WORKDIR /home/picachooser
ENV HOME="/home/picachooser"


# Installing PICAchooser
COPY . /src/picachooser
RUN cd /src/picachooser && \
    python setup.py install && \
    rm -rf /src/picachooser/build /src/picachooser/dist


ENV IS_DOCKER_8395080871=1

RUN ldconfig
WORKDIR /tmp/
ENTRYPOINT ["/usr/local/miniconda/bin/PICAchooser_dispatcher"]

# set a non-root user
USER picachooser

ARG BUILD_DATE
ARG VCS_REF
ARG VERSION
LABEL org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="picachooser" \
      org.label-schema.description="PICAchooser - a lightweight GUI tool for sorting MELODIC ICA components" \
      org.label-schema.url="http://nirs-fmri.net" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url="https://github.com/bbfrederick/picachooser" \
      org.label-schema.version=$VERSION \
      org.label-schema.schema-version="1.0.0rc4"
