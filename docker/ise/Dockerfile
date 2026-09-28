# ISE 14.7 Linux support is Red Hat Enterprise Workstation 5 and 6, and
# SUSE Linux Enterprise 11 (UG631). CentOS 6 is the RHEL 6 rebuild.
FROM centos:6

RUN sed -i \
        -e 's/^mirrorlist=/#mirrorlist=/' \
        -e 's|^#baseurl=http://mirror.centos.org/centos/\$releasever|baseurl=http://vault.centos.org/6.10|' \
        /etc/yum.repos.d/CentOS-Base.repo \
    && yum -y install \
        glibc.i686 \
        glibc-devel.i686 \
        compat-libstdc++-33.i686 \
        compat-libstdc++-33.x86_64 \
        libstdc++.i686 \
        libgcc.i686 \
        ncurses-libs.i686 \
        ncurses-libs.x86_64 \
        zlib.i686 \
        libX11.i686 \
        libXext.i686 \
        libXext.x86_64 \
        libXrender.i686 \
        libXrender.x86_64 \
        libXtst.i686 \
        libXi.i686 \
        libXp.i686 \
        libXp.x86_64 \
        glib2.i686 \
        gtk2.i686 \
        libXft.i686 \
        libSM.i686 \
        libICE.i686 \
        freetype.i686 \
        fontconfig.i686 \
        openmotif \
        xorg-x11-fonts-75dpi \
        xorg-x11-fonts-100dpi \
        make \
        which \
        time \
        perl \
        tar \
        gzip \
        redhat-lsb \
        libusb \
        libusb1 \
        usbutils \
    && ln -sf /usr/bin/make /usr/local/bin/gmake \
    && yum clean all

# This target is the OS base. The ISE installer needs a terminal tall enough
# to show the license. scripts/ise_vnc_image.sh runs that once under VNC,
# then commits xilinx-ise-hil. The license is copied in at commit time, so
# the saved image stays on this machine.
