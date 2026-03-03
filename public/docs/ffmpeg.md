# FFMPEG

## Remuxing

```sh
ffmpeg -i in.m4b -c:a copy -vn -map_metadata -1 out.m4a
ffprobe out.m4a
```

```sh
ffmpeg -i in.m4a -c:a copy -vn -map_metadata -1 out.m4b
ffprobe out.m4b
```

## Transcodage

To M4A (AAC) with good quality (VBR)

```sh
ffmpeg -i in.mp3 -c:a aac -q:a 2 out.m4a
```

To MP3 with good quality

```sh
ffmpeg -i in.m4a -c:a libmp3lame -q:a 2 out.mp3
ffmpeg -i in.m4b -c:a libmp3lame -q:a 2 -vn -map_metadata -1 out.mp3
```

```sh
ffmpeg -i in.mp3 -c:a aac -b:a 128k -vn -map_metadata -1 out.m4b
```

### Find bitrate

```sh
ffprobe -v error -show_entries format=bit_rate -of default=noprint_wrappers=1:nokey=1 in.mp3
```

```sh
ffmpeg -i in.mp3 -c:a aac -b:a 128k -vn -map_metadata -1 out.m4b
ffmpeg -i in.m4b -c:a libmp3lame -b:a 192k -vn -map_metadata -1 out.mp3
```

### Equivalent quality

Instead of forcing a fixed bitrate (CBR), the encoder is asked to maintain equivalent perceived quality.

- For MP3 (`-q:a 2`): It will aim for around 190 kbps. If it doesn't need to (silence or simple voice), it will lower itself.
- For AAC/M4B (`-q:a 2`): FFmpeg's native encoder will try to stick to very good fidelity without wasting space.

```sh
ffmpeg -i in.m4b -c:a libmp3lame -q:a 2 -vn -map_metadata -1 out.mp3
ffmpeg -i in.mp3 -c:a aac -q:a 2 -vn -map_metadata -1 out.m4b
```

## Errors

### Find errors

```sh
ffmpeg -v error -i entree.m4b -f null -
```

```sh
ffmpeg -v info -i entree.m4b -f null - 2>&1 | grep -i "error"
```

### Referenced QT chapter track not found

```sh
ffmpeg -i in.m4b -f ffmetadata metadata.txt
ffmpeg -i in.m4b -i metadata.txt -map 0:a -map_metadata 1 -c copy -vn out.m4b
```

```sh
ffprobe -show_chapters out.m4b
```

### submitting packet to decoder: Invalid data found when processing input / Header missing

Ignoring

```sh
ffmpeg -err_detect ignore_err -i in.m4b -c:a aac -q:a 2 out.m4b
```

Sanitizer

- Stream reconstruction: Instead of copying a broken header, FFmpeg generates a new one that complies with current standards.
- Package cleaning: If the original file has a micro-cut (a binary "glitch"), the encoder will smooth out the transition so that your audio player does not stop abruptly in the middle of playback.
- Chapter indexing: By using `-map_chapters 0`, you re-inject the table of contents into a newly created container structure, which permanently fixes the "Referenced QT chapter track" error.

```sh
ffmpeg -err_detect ignore_err -i in.m4b -c:a aac -q:a 2 -map_chapters 0 -vn out.m4b
```

Clear metadata

```sh
ffmpeg -err_detect ignore_err -i in.m4b -c:a aac -q:a 2 -map_chapters 0 -vn -map_metadata -1 out.m4b
```
