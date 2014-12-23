"use strict"

# load keys into environment if dev
if process.env.NODE_ENV is "dev"
  env = require("node-env-file")
  
  # only local environments should have keys.env
  env __dirname + "/keys.env"

# use for your api keys, secrets, etc.
module.exports =
  keys:
    aws:
      key: process.env.AWS_ACCESS_KEY
      keySecret: process.env.AWS_ACCESS_KEY_SECRET
    github:
      user: process.env.GITHUB_USER
      pass: process.env.GITHUB_PASS
  urls:
    s3:
      bucket: process.env.AWS_S3_BUCKET
