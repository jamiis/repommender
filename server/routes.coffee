###
Main application routes
###
"use strict"
errors = require "./components/errors"
express = require "express"
bodyParser = require "body-parser"
async = require "async"
_ = require "lodash"

module.exports = (app) ->
  
  config = app.get "config"
  github = app.get "github"

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
    # TODO lookup repositories from recommended db
    reposNames = [
      'Homebrew/homebrew',
      'jamiis/repommender',
      'jamiis/tweet-map',
      'jamiis/dotfiles',
      'jamiis/tweet-sentiment',
    ]

    repoJsonKeys = [
      "url", "stargazers_count", "name",
      "full_name", "language", "owner"]

    async.map reposNames,
      (name, callback) ->
        github.repo name, (err, data, headers) ->
          callback(err, data)
      (err, githubRepos) ->
        if err
          res.sendStatus 404
          return
        console.log githubRepos

        repos = _.map githubRepos, (repo) ->
          _.pick repo, (v,k) -> k in repoJsonKeys
        console.log repos

        app.render "repos",
          repos: repos
          (err, html) ->
            if err
              res.sendStatus 404
              return
            console.log html
            res.json
              username: username,
              reposPartial: html


  # all undefined asset or api routes should return a 404
  app.route("/:url(api|auth|components|app|bower_components|assets)/*").get errors[404]
  
  # all other routes should redirect to the index.html
  app.route("/*").get (req, res) ->
      res.render app.get("appPath") + "/index"

  return
