# The build image: Debian with the armhf cross compiler and the libraries both games link (armhf), the native ones for
# their asset tools (Torch, ZAPD) and the native build, and qemu-arm. spdlog, tinyxml2 and libzip are left out on
# purpose: they are fetched (Torch, cmake/2ship-deps.cmake) or built (build.sh) and linked statically.
FROM debian:trixie

RUN dpkg --add-architecture armhf && apt-get update && apt-get install -y --no-install-recommends \
    build-essential crossbuild-essential-armhf pkg-config git ca-certificates curl file zip unzip python3 \
    cmake ninja-build qemu-user lsb-release \
    zlib1g-dev libbz2-dev libpng-dev nlohmann-json3-dev libzip-dev \
    libsdl2-dev libsdl2-net-dev libogg-dev libvorbis-dev libopus-dev libopusfile-dev libegl-dev libgles-dev \
    zlib1g-dev:armhf libbz2-dev:armhf libpng-dev:armhf libsdl2-dev:armhf libsdl2-net-dev:armhf libsdl2-ttf-dev:armhf \
    libogg-dev:armhf libvorbis-dev:armhf libopus-dev:armhf libopusfile-dev:armhf libegl-dev:armhf libgles-dev:armhf \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /repo
