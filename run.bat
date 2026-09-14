@echo off
set KMP_DUPLICATE_LIB_OK=TRUE
set TF_ENABLE_ONEDNN_OPTS=0
python run.py
pause
