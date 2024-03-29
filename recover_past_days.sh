#!/bin/bash

function run_ffmpeg() {
  # see this SO answer https://video.stackexchange.com/a/7913 and these docs http://ffmpeg.org/faq.html#How-do-I-encode-single-pictures-into-movies_003f
  # generate high quality video from pictures
  cat *.jpg | ffmpeg -r 96 -f image2pipe -c:v mjpeg -i - -y "$DAY"_full_quality.mp4
  # generate lower quality (<10MB) video from high quality video
  ffmpeg -i "$DAY"_full_quality.mp4 -r 45 -b:v 2500000 -c:v libx264 -profile:v high -pix_fmt yuv420p -y "$DAY"_for_tg.mp4
}

function remove_jpgs_if_video_exists() {
  # check if video exists and has size greater than 0 bytes
  if [ -f "$DAY"_full_quality.mp4 ] && [ $(wc -c "$DAY"_full_quality.mp4 | awk '{print $1}') -gt 0 ]; then
    echo "ffmpeg has run, now removing .jpgs..."
    rm *.jpg
    echo "Removed all .jpgs for $DAY"
  else
    echo "There have been some errors in creating the video, skipping picture removal..."
  fi
}

function log_info() {
  LOG_FILE="$DAY"_info.txt
  NUM_PICS=$(ls -1 *.jpg | wc -l)
  echo "Writing log file to $LOG_FILE"
  echo "Number of pictures: $NUM_PICS" >> $LOG_FILE
  echo "List of pictures:\n$(ls -1 *.jpg)" >> $LOG_FILE
}

function make_timelapse() {
  run_ffmpeg
  log_info
  remove_jpgs_if_video_exists
}

DAYS=()
TODAY=$(date +%Y-%m-%d)

# add only days before today to array
for item in *.jpg ; do
    DAY="${item:0:10}"
    if [[ $DAY != $TODAY ]]; then
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
		    make_timelapse
        cd ..
    done
fi


DAYS=()

for dir in */ ; do
    dir=${dir%*/}
    cd "$dir"
    if [ ! -f "$dir"_for_tg.mp4 ]; then
        pics=()
        for pic in *.jpg ; do
            pics+=($pic)
        done
        if [ ${#pics[@]} -gt 1 ]; then
            DAYS+=("$dir")
        fi
    fi
    cd ..
done

if [ ${#DAYS[@]} -eq 0 ]; then
    echo "Missing video for telegram: There are no past days to make the timelapse for."
    exit 42
fi

# for debugging
#echo "${DAYS[@]}"
#exit 0

for DAY in "${DAYS[@]}"; do
    cd "$DAY"
    make_timelapse
    cd ..
done

exit 0
