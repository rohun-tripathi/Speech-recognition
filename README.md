audioCAPTCHA is a Python module that generates clips to be used Audio CAPTCHA from everyday audio sources. It has been tested for python 3.4-3.6 and will work with minimal tweaks for python 2.7.

audioCAPTCHA is shared for researchers interested in developing audio CAPTCHA clips for research purposes.
Shared under the MIT License.

It requires uses pydub, http://pydub.com, for audio file manipulation, watson-developer-cloud for Speech to Text conversion and nltk corpus for word validations.

Author (Might be removed for the review purpose) -
    Rohun Tripathi - rohun.tripathi.5@gmail.com
    Project repo - https://github.com/rohun-tripati/speech-recognition
    URL of the draft - are we sharing on arxiv?

Requirements:

Tested in python 3.3-3.6. Should work with minimal tweaks for python 2.7

Requirements:
    pydub - pip install pydub
    watson-developer-cloud - pip install watson-developer-cloud

    Our project uses IBM STT Service to generate audio CAPTCHAs. Credentials:
        Sign up on console.bluemix.net
        Set the work demographic to US South for best results
        Create a new Watson STT Service.
        Copy Credentials to IBM_password and IBM_username "global_constants.py"

    ffmpeg -
        From https://github.com/jiaaro/pydub - "You can open and save WAV files with pure python. For opening and saving non-wav files – like mp3 – you'll need ffmpeg or libav."
        Instructions on the site.

        For Ubuntu 14.04 -
            ffmpeg from  - https://www.faqforge.com/linux/how-to-install-ffmpeg-on-ubuntu-14-04/
                installation might require you to dump previously installed packages.

            libav has a limit of 5000000 microseconds - 1 hours, 23 minutes and 20 seconds.

        For Mac -
            brew install ffmpeg --with-fdk-aac --with-ffplay --with-freetype --with-frei0r --with-libass --with-libvo-aacenc --with-libvorbis --with-libvpx --with-opencore-amr --with-openjpeg --with-opus --with-rtmpdump --with-schroedinger --with-speex --with-theora --with-tools

    nltk corpora -
        The project uses nltk corpora to check for valid words from the english dictionary.
        Installation technique -
            Start a python console
            [1] : import nltk
            [2] : nltk.download()
            And NLTK Corpora download screen pops us. Download all the options avaliable.


Out of the box - Usage:
    The entry module to the code base is main.py

    A command line usage via example.py -
        python example.py --group "example" --data "/Users/rohuntripathi/speech-recognition-test/audio_data" --input "input_stage" --chunk "chunk_folder" --selected "selected" --audioclippeddata "more_audio"

    Values provided:
          -g GROUP, --group GROUP
                                data in example sub folder path/name/tag
          -d DATA, --data DATA  data folder path
          -i INPUT, --input INPUT
                                input sub folder
          -c CHUNK, --chunk CHUNK
                                chunk sub folder
          -a AUDIOCLIPPEDDATA, --audioclippeddata AUDIOCLIPPEDDATA
                                proposed clips for CAPTCHA selection
          -s SELECTED, --selected SELECTED
                                final selected CAPTCHA output, on which the STT fails, from the proposed values

    global_constants.py is the configuration file.
        Can set the CAPTCHA to be generated in global_constants.py
