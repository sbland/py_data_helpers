
[ -z "$1" ] && echo "make sure to input [patch|minor|major]" && exit 1;
source venv/bin/activate
if [ -z "$(git status --porcelain)" ]; then
    echo "Working directory is clean"
else
    echo "Working directory is not clean!"
    read -p "Stash changes and contiue(YES/no)? " stashchanges
    if [stashchanges]; then
        git stash save -u "hold_build_deploy"
    else
        echo "Working directory not clean. Commit changes or accept stashing changes." && exit 1;
    fi
fi
bumpversion $1
# python -m build
uv build
twine upload dist/*
git push

if [ -z "$(git status --porcelain)" ]; then
    echo "Working directory is clean"
else
    git stash pop
fi