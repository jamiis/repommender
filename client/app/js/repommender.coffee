this.repommender = ->

  self = this

  this.document.getElementById("search").addEventListener "keyup", ((ev) ->
      
      username = self.document.getElementById("search").value
      console.log "username: ", username
      if not username then return
 
      $.ajax "/search/" + username,
        type: "POST"
        success: (data, textStatus, jqXHR) ->
          console.log "success ", data, textStatus, jqXHR
          $(".reel").html data.reposPartial
          return

        error: (jqXHR, textStatus, error) ->
          console.log textStatus, error
          return

      return
    ), false
