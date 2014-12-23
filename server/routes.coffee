###
Main application routes
###
"use strict"
errors = require "./components/errors"
express = require "express"
bodyParser = require "body-parser"

module.exports = (app) ->
  
  config = app.get "config"

  # config middleware
  app.use bodyParser.json()

  # partials
  app.get "/partials/:name", (req, res) ->
    res.render app.get("appPath") + "/app/partials/" + req.params.name
  
  # styles
  app.use "/css", express.static(app.get("appPath") + "/app/css/")
  app.use "/fonts", express.static(app.get("appPath") + "/app/fonts/")
  app.use "/js", express.static(app.get("appPath") + "/app/js/")
  app.use "/img", express.static(app.get("appPath") + "/app/img/")

  # update twitter stream word filter
  app.route("/search/:username").post (req, res) ->
    username = req.params.username
    console.log username
    # TODO return recommendations based on user
    res.json { uname: username }

  # all undefined asset or api routes should return a 404
  app.route("/:url(api|auth|components|app|bower_components|assets)/*").get errors[404]
  
  # all other routes should redirect to the index.html
  app.route("/*").get (req, res) ->
      res.render app.get("appPath") + "/index"

  return
