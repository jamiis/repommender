###*
github api handling
###
"use strict"

github = require 'octonode'

module.exports = (app) ->

    config = app.get "config"
    client = github.client
      username: config.keys.github.user
      password: config.keys.github.pass

    app.set "github",
      repo: (name, callback) ->
        client.repo(name).info(callback)
