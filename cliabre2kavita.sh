# File Name: cliabre2kavita.sh
# Author: AikenHong
# mail: h.aiken.970@gmail.com
# Created Time: Mon Nov 27 00:03:59 2023

# methos one.
lib_path=$1
sudo find $lib_path -name "*.original_epub" -exec rm -v {} \;

# method two.
#target_path=$2
#sudo find $lib_path -name "*.epub" -exec cp {} $target_path \;
