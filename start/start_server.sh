cd /home/sergio/Documentos/GitHub/mtron828.github.io/
#echo exit | xauth -f /home/sergio/.Xauthority
#export $(grep -v '^#' ./start/env.env | xargs)
export XAUTHORITY=$(xauth info | awk -F"Authority file:" '{print $2}' | tr -d ' ' | head -1)
export DISPLAY=:0
#google-chrome
./bin/python app.py
