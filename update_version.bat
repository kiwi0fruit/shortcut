set tagname=0.1.0
git tag -d %tagname%
git push --delete origin %tagname%
git tag -a %tagname%
git push --tags
pause