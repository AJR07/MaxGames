#! /bin/sh

echo "Deploying from branch $(git branch --show-current) to Heroku."

if [ ! $(git branch --show-current) = "main" ]; then
    echo "Can only deploy from branch main. Abort."
    exit 1
fi

rm -f tar
tar cf tar serviceAccountKey.json serviceAccountKey2.json config.json >/dev/null 2>&1  # shh
s=$?
bruh=0  # bruh

function cleanup()
{
    if [ $bruh -eq 0 ]; then
        echo "Cleaning up, unarchiving configs."
        git reset --hard HEAD~ >/dev/null 2>&1  # oh, shut up
        tar xf tar >/dev/null 2>&1  # you shut up too
        rm -f tar
        echo "Cleaning up, unarchiving configs complete."
        bruh=1
    fi
}

trap cleanup SIGINT

if [ ! $s -eq 0 ]; then
    echo "Config files do not exist. Abort."
    exit 1
fi

git add -f serviceAccountKey.json serviceAccountKey2.json config.json >/dev/null 2>&1  # please just shut up
s1=$?
git commit --allow-empty -m heroku >/dev/null 2>&1  # please just shut up as well

if [ $s1 -eq 0 ]; then
    heroku restart >/dev/null 2>&1 
    heroku buildpacks:clear >/dev/null 2>&1 
    git push -fq heroku main | sed 's/^remote: //g'
else
    echo 'Failed to add config files. Abort.'
    cleanup
    exit 1
fi
cleanup
exit 0
