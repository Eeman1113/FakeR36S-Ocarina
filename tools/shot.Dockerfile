# build.sh shot's image: the build image plus Xvfb, ImageMagick and Mesa's llvmpipe for armhf, which the game runs on
# under qemu-arm
FROM glosports-harbourmasters

RUN apt-get update && apt-get install -y --no-install-recommends xvfb imagemagick \
    libegl-mesa0:armhf libgl1-mesa-dri:armhf libgles2:armhf \
    && rm -rf /var/lib/apt/lists/*
