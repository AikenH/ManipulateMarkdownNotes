# using sed to replace thoes index of post.

# input params
dirpath=$1
newest_n_file=$2
newest_n_file=$((newest_n_file))
img_num=41

# calculate which one we need to modify
total=`ls -l ${1}/*.md | grep "^-" | wc -l`
total=$((total))
echo $total
start_idx=$(expr $total - $newest_n_file + 4)
echo $start_idx

# start to loop and process.
idx=0
for file in `ls -rt ${dirpath}/*.md`;do
  echo "$idx $file"
  if [[ $idx -lt  ${start_idx} ]];then
    echo "continue"
  else
    new_idx=`expr $idx % $img_num`
    echo "start to process at $idx $file, new idx is $new_idx"
    # linux support 
    sed -i "s/lml_bg.*.jpg/lml_bg${new_idx}.jpg/g" $file
    #mac
    #sed -i.bak "s/lml_bg.*.jpg/lml_bg${new_idx}.jpg/g" $file

  fi
  ((idx++))
done
