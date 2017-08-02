Requirements:

Works in python 3.3-3.6
Should work with minimal tweaks for for 2.7

Needs installation:
    pydub - pip install pydub
    watson-developer-cloud - pip install watson-developer-cloud

https://github.com/jiaaro/pydub
    You can open and save WAV files with pure python. For opening and saving non-wav files – like mp3 – you'll need ffmpeg or libav.
    Instructions on the site.

    For Ubuntu 14.04 -
        ffmpeg from  - https://www.faqforge.com/linux/how-to-install-ffmpeg-on-ubuntu-14-04/
            installation might require you to dump previously installed packages.

        libav has a limit of 5000000 microseconds - 1 hours, 23 minutes and 20 seconds.