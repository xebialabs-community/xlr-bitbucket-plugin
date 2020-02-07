openssl aes-256-cbc -K $encrypted_e5bd312d25bf_key -iv $encrypted_e5bd312d25bf_iv
  -in deploy_key.enc -out /tmp/deploy_key -d
eval "$(ssh-agent -s)"
echo -e "Host $DIST_HOST\n\tStrictHostKeyChecking no\n" >> ~/.ssh/config
chmod 600 /tmp/deploy_key
ssh-add /tmp/deploy_key
rsync --update -raz -i $TRAVIS_BUILD_DIR/build/libs/*.jar $DIST_USER@$DIST_HOST:$DIST_PATH/${TRAVIS_REPO_SLUG#*/}/
