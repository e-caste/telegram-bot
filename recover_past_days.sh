#!/bin/bash

DAYS=()
TODAY=$(date +%Y-%m-%d)

# add only days before today to array
for item in *.jpg ; do
    DAY="${item:0:10}"
    if [ $DAY != $TODAY ]; then
        if [[ ! " ${DAYS[*]} " == *"$DAY"* ]]; then
            DAYS+=("$DAY")
        fi
    fi
done

# for debugging
# echo "${DAYS[@]}"
# exit 0

if [ ${#DAYS[@]} -eq 0 ]; then
    echo "Missing both videos: There are no past days to make the timelapse for."
else
    # make 2 timelapses (high quality and for telegram) for each of past days
    for DAY in "${DAYS[@]}"; do
        mkdir "$DAY"
        echo "Made directory $DAY"
        mv "$DAY"*.jpg $DAY
        echo "Moved all $DAY*.jpgs to $DAY directory, now running ffmpeg..."
        cd $DAY
        ffmpeg -r 96 -f image2 -pattern_type glob -i '*.jpg' -c:v libx264 -b:v 31457280 -y "$DAY"_full_quality.mp4 && ffmpeg -i "$DAY"_full_quality.mp4 -r 60 -b:v 2500000 -c:v libx264 -profile:v high -pix_fmt yuv420p "$DAY"_for_tg.mp4
        echo "ffmpeg has run, now removing .jpgs..."
        rm *.jpg
        echo "Removed all .jpgs for $DAY"
        cd ..
    done
fi


DAYS=()

for dir in */ ; do
    cd "$dir"
    if [ ! -f "$dir_for_tg.mp4" ]; then
        DAYS+=("$dir")
    fi
    cd ..
done

if [ ${#DAYS[@]} -eq 0 ]; then
    echo "Missing video for telegram: There are no past days to make the timelapse for."
    exit 42
fi

for DAY in "${DAYS[@]}"; do
    cd "$DAY"
    ffmpeg -r 96 -f image2 -pattern_type glob -i '*.jpg' -c:v libx264 -b:v 31457280 -y "$DAY"_full_quality.mp4 && ffmpeg -i "$DAY"_full_quality.mp4 -r 60 -b:v 2500000 -c:v libx264 -profile:v high -pix_fmt yuv420p "$DAY"_for_tg.mp4
    echo "ffmpeg has run, now removing .jpgs..."
    rm *.jpg
    echo "Removed all .jpgs for $DAY"
    cd ..
done

exit 0