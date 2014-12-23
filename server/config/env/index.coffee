###
Application configuration
###
"use strict"
path = require("path")
_ = require("lodash")

# all configurations will extend these options
# ============================================
all =
  env: process.env.NODE_ENV
  
  # root path of server
  root: path.normalize(__dirname + "/../../..")
  
  # server port
  port: process.env.PORT or 3000


# Export the config object based on the NODE_ENV.
# ==============================================
module.exports = _.merge.apply(_, [
  all
  require("./" + all.env + ".js") or {}
  require("./keys.js") or {}
])
