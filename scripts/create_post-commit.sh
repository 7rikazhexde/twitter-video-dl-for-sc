#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

create_post_commit() {
    cat > "$1" << EOF
#!/usr/bin/env bash

source "$SCRIPT_DIR/../.venv/bin/activate"
poetry run python "$SCRIPT_DIR/../ci/run_git_tag_base_pyproject.py"
if [ \$? -ne 0 ]; then
    printf "Error occurred in run_git_tag_base_pyproject.py. Exiting post-commit.\n"
    exit 1
fi

git push origin main:main
git push --tags
printf ".git/hooks/post-commit end!!!\n"
EOF

    if [ "$2" == "execute" ]; then
        chmod +x "$1"
        echo "$1 created with execution permission."
    else
        echo "$1 created."
    fi
}

if [ -f "$SCRIPT_DIR/.git/hooks/post-commit" ]; then
    read -p "$SCRIPT_DIR/../.git/hooks/post-commit already exists. Do you want to create $SCRIPT_DIR/.git/hooks/post-commit.second instead? (y/N): " choice
    if [[ $choice == "y" || $choice == "Y" ]]; then
        create_post_commit "$SCRIPT_DIR/../.git/hooks/post-commit.second"
        exit 0
    else
        create_post_commit "$SCRIPT_DIR/../.git/hooks/post-commit" "execute"
        exit 0
    fi
fi

create_post_commit "$SCRIPT_DIR/../.git/hooks/post-commit" "execute"
exit 0
