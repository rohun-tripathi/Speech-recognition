### AudioCAPTCHA

audioCAPTCHA is a Python module that generates clips to be used Audio CAPTCHA from everyday audio sources. It has been tested for python 3.4-3.6 and will work with minimal tweaks for python 2.7.

audioCAPTCHA is shared for researchers interested in developing audio CAPTCHA clips for research purposes.
Shared under the MIT License.

### Installation

It requires uses pydub, http://pydub.com, for audio file manipulation, watson-developer-cloud for Speech to Text conversion and nltk corpus for word validations.

### Requirements:
    python 3.3-3.6. Should work with minimal tweaks for python 2.7
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


### Out of the box - Usage:

    The entry module to the code base is main.py and example.py.

    A command line usage via example.py -
        python example.py --group "youtube_lecture" --data "reboot_rerun" --input "input" --chunk "chunk_folder" --selected "selected" --audioclippeddata "other_audio" --produce_chunk

    Values to be provided:
      -d / --data, Data is the root folder where the input data subfolder should already be stored. All other folders, Input, chunk, selected and audioclippeddata will be RELATIVE to the data folder path.
      -p --produce_chunk, Whether to produce chunks from the input data or not. Not needed after first run. It's default value is FALSE
      -g / --group, Group is a name for the data grouping we use in the paper. For example, a group can be youtube_lecture and another can be podcasts.
      -i / --input, The input sub folder which should already be created and be relative to the folder in Data.
      -c / --chunk. The chunk sub folder which should be relative to the folder in Data.
      -a / --audioclippeddata, Proposed clips for CAPTCHA selection before they are sent to IBM for filtering. It should be relative to the folder in Data.
      -s / --selected, The final selected CAPTCHA output. These are the files to be used for CAPTCHA.

    global_constants.py is the configuration file.
        Can set the CAPTCHA to be generated in global_constants.py

### The MIT License
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
