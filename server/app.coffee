###
Main application file
###
"use strict"

# set default node env to dev
process.env.NODE_ENV = process.env.NODE_ENV or "prod"

config = require "./config/env"
http = require "http"
http.globalAgent.maxSockets = Infinity
_ = require "underscore"

aws = require "aws-sdk"
_.extend aws.config,
  region: "us-east-1"
  accessKeyId: config.keys.aws.key
  secretAccessKey: config.keys.aws.keySecret

# ... server setup ... //
express = require("express")
app = express()
server = http.createServer(app)
app.set "server", server
app.set "config", config
require("./config/express") app

# setup web socket
io = require("socket.io").listen(server)
app.set "io", io

# we want the configured-aws object to be a singleton
app.set "aws", aws

# setup server services and start listening
require("./github") app
require("./routes") app
server.listen config.port, ->
console.log "listening on %d, in %s mode", config.port, app.get("env")

# expose app
exports = module.exports = app
