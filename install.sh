sudo apt-get -y install tesseract-ocr==4;
wget https://github.com/tesseract-ocr/tessdata_best/raw/main/spa.traineddata;
sudo mv spa.traineddata /usr/share/tesseract-ocr/4.00/tessdata/;