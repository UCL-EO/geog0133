#!/bin/bash 

# shell to sort nb
# documentation
# run bin/notebook-run.sh


here=$(pwd)
base="$(cd $(dirname "$0") &&  cd .. &&  pwd -P && cd "$here")"
repo=$(echo $base | awk -F/ '{print $NF}')

cd $base
here=$base
echo "----> running $0 from $here"
echo "--> location: $base"
echo "--> repo: $repo"

# HOME may not be set on windows
if [ -z "$HOME" ] ; then
  cd ~
  HOME=$(pwd)
  echo "--> HOME $HOME"
  cd "$base"
fi

cd "$base"

echo "--> re-making docs"
rm -rf docs
mkdir -p docs
mkdir -p docs/images docs/geog0133 docs/data
mkdir -p docs/javascripts

cd "$base/notebooks"
cp images/* "$base/docs/images"
cp geog0133/* "$base/docs/geog0133"
cp data/* "$base/docs/data"

cd $base
echo "--> re-making notebooks_lab"
rm -rf notebooks_lab
mkdir -p notebooks_lab
#
# get the theme from config/mkdocs.yml
# and update ${base}/config/requirements.txt
#
theme=$(grep 'name:' config/mkdocs.yml | grep -v '#' | tail -1 | awk '{print $NF}' | sed 's/'\''//g' | sed 's/'\"'//g')
echo "theme: $theme"
grep -v $theme ${base}/config/requirements.txt | grep -v GEOG0133 > tmp.$$; mv tmp.$$  ${base}/config/requirements.txt; 
extras=$(grep $theme config/mkdocs.yml | awk '{print "mkdocs-"$NF}' | sed 's/://g' | sed 's/'\''//g' | sed 's/'\"'//g' )
echo "installing $extras"
echo $extras | awk '{for(i=1;i<=NF;i++)x[$i]=$i} END{for(i in x)print i}'  >> ${base}/config/requirements.txt
cat ${base}/config/requirements.txt

if [ $theme == "readthedocs" ]; then
  grep -v readthedocs <  ${base}/config/requirements.txt > /tmp/tmp.$$
  mv /tmp/tmp.$$ ${base}/config/requirements.txt 
fi

pip3 install -r ${base}/config/requirements.txt --user

# now add these to "${base}"/Docker/small_environment.yml
req=$(grep -v pip < ${base}/config/requirements.txt)
cp "${base}"/config/small_environment.yml "${base}"/Docker/small_environment.yml 
for n in ${req[@]}
do
  grep -v $n < "${base}"/Docker/small_environment.yml > /tmp/tmp2.$$
  mv /tmp/tmp2.$$ "${base}"/Docker/small_environment.yml
done
awk < ${base}/config/requirements.txt '{print "    - "$0}' >> "${base}"/Docker/small_environment.yml

# test it
#conda env create -n small  --force -f "${base}"/Docker/small_environment.yml



#rm -rf "$base/docs/sphinx"
#mkdir -p "$base/docs/sphinx"
cd "$base"
#sphinx-quickstart -q -p "GEOG0133 Scientific Computing" -a "P. Lewis and J. Gomez-Dans" -v "1.0.1" -l "en" --ext-autodoc --ext-doctest --ext-viewcode --ext-githubpages --ext-intersphinx docs/sphinx

cd $base
echo "--> re-making notebooks_lab"
rm -rf site
rm -rf */*nbconvert*
rm -rf notebooks_lab/*_files notebooks_lab/*ipynb notebooks_lab/*md
# filter notebooks from notebooks into notebooks_lab
geog0133/edit_notebook.py

#bin/link-set.sh


echo "--> creating markdown files in notebooks_lab"
# make markdown from the ipynb in notebooks_lab/???_*ipynb
jupyter nbconvert --ExecutePreprocessor.timeout=600 --ExecutePreprocessor.allow_errors=True \
    --nbformat=4 --ExecutePreprocessor.store_widget_state=True --to markdown notebooks_lab/???_*ipynb

echo "--> staging markdown files into docs"
# mv into docs
mv notebooks_lab/*_files docs
mv notebooks_lab/*md docs
#rm -f docs/README.md
# buggy bit
rm -rf docs/*' 3' docs/*' 2'  docs/*' 4' 
rm -f docs/*/*' 3'.* docs/*/*' 2'.*  docs/*/*' 4'.* 
rm -f docs/*' 3.md' docs/*' 2.md' docs/*' 4.md'
rm -f docs/*/*/*' 2'* docs/*/*/*' 3'* docs/*/*/*' 4'* 

rm -rf notebooks_lab/*' 3' notebooks_lab/*' 2'  /*' notebooks_lab4' 
rm -f notebooks_lab/*/*' 3'.* notebooks_lab/*/*' 2'.*  notebooks_lab/*/*' 4'.* 
rm -f notebooks_lab/*' 3.'* notebooks_lab/*' 2.'* notebooks_lab/*' 4.'*
rm -f notebooks_lab/*/*/*' 2'* notebooks_lab/*/*/*' 3'* notebooks_lab/*/*/*' 4'* 
rm -f docs/copy/*' '2
rm -f docs/*/*' '2.* docs/*/*' '4.* docs/*/*' '3.* 
for i in docs/*md
do
  sed < $i > /tmp/$$ 's/.ipynb/.md/g'
  mv /tmp/$$ $i
done

echo "--> adding to docs/index.md"

# get files
cd "$base"
files=docs/*_files
filedirs=$(echo $files | sed 's/docs\///g')
#cd "$base"/docs/sphinx
#for n in ${filedirs[@]}
#do
#  ln -s ../$n $n
#done

cd "$base"
echo "--> generating mkdocs files for docs"
geog0133/mkdocs_prep.py --dev
echo "--> building mkdocs"


cd $base/notebooks
for i in *md ; do
  sed < $i 's/ipynb/md/g' > $base/docs/$i
done

# only copy the data files we really need for links
cd $base/docs
rm -f data
cp $base/notebooks/data/*  data

#cp $base/notebooks/data/
#ln -s $base/notebooks notebooks

sed < index.md 's/notebooks\///g'| sed  's/docs\///g' > /tmp/tmp.$$
mv  /tmp/tmp.$$ index.md

cp ../config/requirements.txt .

# avoid conflict with index.md
sed < README.md 's/docs\///g' | sed 's/notebooks\///g' > /tmp/tmp.$$
mv /tmp/tmp.$$ GEOG0133.md
#mv GEOG0111.md index.md

#rm -f README.md

#sed < index.md 's/docs\///g' | sed 's/notebooks\///g' > /tmp/tmp.$$
#mv /tmp/tmp.$$ index.md

# mathjax for rendering latex
# see https://squidfunk.github.io/mkdocs-material/reference/mathjax/#arithmatex

cat << EOF > javascripts/config.js
window.MathJax = {
  tex: {
    inlineMath: [["\\(", "\\)"]],
    displayMath: [["\\[", "\\]"]],
    processEscapes: true,
    processEnvironments: true
  },
  options: {
    ignoreHtmlClass: ".*|",
    processHtmlClass: "arithmatex"
  }
};
EOF

# deal with animated notebook
#echo "--> dealing with special case of 042_Weighted_smoothing_and_interpolation.ipynb"
#cd $base
#geog0133/filter_movies.py 
#sed < $base/work/042_Weighted_smoothing_and_interpolation.md > $base/docs/042_Weighted_smoothing_and_interpolation.md 's/.ipynb/.md/g'
#echo "--> done dealing with special case of 042_Weighted_smoothing_and_interpolation.ipynb"


cd $base/docs

rm -f $base/docs/copy
mkdir $base/docs/copy
cp $base/bin/copy/* $base/docs/copy
cd $base
mkdocs build -v


#sed < $base/docs/index.rst 's/index.md/docindex.md/' > tmp.$$
#mv tmp.$$ index.rst
#rm -f index.md
#cp ../*.md ../*.html .

# dont confuse index.md with index.rst
#if [ -f "index.md" ]; then
#  mv index.md docindex.md
#else
#  cp ../index.md docindex.md
#fi

#cp ../index.rst .
#make clean html
cd $base
echo "----> done running $0 from $base"
echo "to upload, run:  mkdocs gh-deploy --force"
