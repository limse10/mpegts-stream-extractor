# MPEG-TS Stream Extractor

Extracts video and klv streams simultaneously from a MPEG-TS udp stream.

# Dependencies

- Python 3.x
- ffmpeg

# Usage

## Streaming

- Download Sample Data

```
$ curl http://samples.ffmpeg.org/MPEG2/mpegts-klv/Day%20Flight.mpg -o data/day.mpg
```

- Begin Stream

```
$ ffmpeg -i "data/day.mpg" -map 0 -vcodec libx264 -f mpegts udp://localhost:12345 -map 0 -vcodec libx264 -f mpegts udp://localhost:1234
```

## Sanity Checks (optional)

- Test Stream

```
$ ffplay udp://localhost:1234
```

- Save Stream Data

```
$ ffmpeg -i udp://localhost:1234 -map 0:1 -f data -codec copy stream.klv
```

- Parse Downloaded KLV Data File

```
$ python parse.py < stream.klv > stream.txt
```

## Running Live

```
$ python stream.py
```

# Acknowlegements

- paratech's klvdata python package (repository [here](https://github.com/paretech/klvdata))
