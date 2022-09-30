// Function when chat is started
function showChat(roomName, friend) {
  // Hide other chats
  $(".chat-pop").hide();

  // show the requested chat
  let chatId = "#chat_" + friend;
  $(chatId).show();

  // Scroll to the bottom of the chat
  $(chatId + " .chat-box").scrollTop(
    $(chatId + " .chat-box").prop("scrollHeight")
  );
  // Focus on the typing area
  $("#chatInput_" + friend).focus();

  // start a new WebSocket
  const chatSocket = new WebSocket(
    "ws://" + window.location.host + "/ws/chat/" + roomName + "/"
  );

  // When a message is sent to the WebSocket
  chatSocket.onmessage = function (e) {
    // Add the message to the chat area
    const data = JSON.parse(e.data);
    $(chatId + " .chat-box p").text(function (index, text) {
      return text + data.message + "\n";
    });

    // Scroll to the bottom of the chat
    $(chatId + " .chat-box").scrollTop(
      $(chatId + " .chat-box").prop("scrollHeight")
    );
  };

  // send an error message if WebSocket is closed
  chatSocket.onclose = function (e) {
    console.error("Chat socket closed unexpectedly");
  };

  // send the message if the user presses Enter
  $("#chatInput_" + friend).keyup(function (e) {
    if (e.key === "Enter") {
      // enter, return
      $("#chatSend_" + friend).click();
    }
  });

  // send the message if the user clicks the send button
  $("#chatSend_" + friend).click(function (e) {
    // Send the message and the friend id to the WebSocket to update the relevant database
    chatSocket.send(
      JSON.stringify({
        message: $("#chatInput_" + friend).val(),
        pk: roomName,
      })
    );

    // After sending clear the input field
    $("#chatInput_" + friend).val("");
  });
}

// Show options for a friend
function showOptions(name) {
  $(".friend-options").hide();
  let optionsId = "#options_" + name;
  $(optionsId).show();
}

// Show the relevant canvas
function showModal(pk) {
  $("#myModal_" + pk).show();
}


// Show uploaded images
function readURL(input) {
  if (input.files) {
    for (file of input.files) {
      var reader = new FileReader();
      reader.onload = function (e) {
        $(".image-area")
          .first()
          .append(
            $("<img></img>")
              .attr({ src: e.target.result })
              .addClass("img-fluid rounded shadow-sm mx-auto d-block")
          );
      };
      reader.readAsDataURL(file);
    }
  }
}

// functions to run when page finishes loading
jQuery(document).ready(function ($) {
  // make chats seperate elements
  $("body").append($(".chat-pop"));

  // hide chats
  $(".chat-pop").hide();
  // hide friends options
  $(".friend-options").hide();
  // $(".friend_list .friend-row").click(function () {
  //   window.location = $(this).data("href");
  // });

  
  $(document).click(function (e) {
    // If user clicks anywhere outside the options, hide the options
    if (!$(e.target).is(".friend-options")) {
      $(".friend-options").hide();
    }
    // If user clicks anywhere outside the chat, hide the chat
    if (!$(e.target).is(".friend-list *, .chat-pop *")) {
      $(".chat-pop").hide();
    }
  });

  // if friend options button is clicked, don't click the friend item
  $(".friendBtn").click(function (e) {
    e.stopPropagation();
  });

  // if friend options button is hovered over, don't hover over the friend item
  $(".friendBtn").each(function () {
    $(this).hover(
      function (e) {
        $(this).addClass("hover-effect");
        $(this).parent().mouseleave();
      },
      function (e) {
        $(this).removeClass("hover-effect");
        $(this).parent().mouseenter();
      }
    );
  });

  // if friend item is hovered over, apply special styling
  $(".friend-row").each(function () {
    $(this).hover(
      function (e) {
        $(this).addClass("hover-effect");
      },
      function (e) {
        $(this).removeClass("hover-effect");
      }
    );
  });

  // if the user enters the search bar, go to the search page
  $("#search-bar").focusin(function () {
    $("#search-form").submit();
  });

  // If current page is the search page, focus on the search bar
  $("#search-bar-active").focus();

  // Filter the search results according to the search value
  $("#search-bar-active").on("change input", function () {
    searchVal = $(this).val();
    $(".nonfriend").each(function () {
      $(this).parent().parent().parent().show();
      if ($(this).text().toLowerCase().indexOf(searchVal.toLowerCase()) < 0) {
        $(this).parent().parent().parent().hide();
      }
    });
  });

  //------------------------- Modal Part
  // When the user clicks on <span> (x), close the modal
  $(".close").click(function () {
    $(this).parent().hide();
  });

  // Make canvases on top of all elements except the title and navigation menu
  $(".container-fluid").first().append($(".modal"));

  // When the user selects images to add, show them, and their names
  $("#upload").on("change", function (event) {
    readURL($(this));

    let input = event.originalEvent.srcElement;
    $("#upload-label").text("File name: ");
    for (file of input.files) {
      $("#upload-label").text(function (index, currentcontent) {
        return currentcontent + file.name + ", ";
      });
    }
  });

  // When the page loads, activate one image only
  let items = document.querySelectorAll(".carousel-item");
  for (let item of items) {
    item.classList.remove("active");
  }
  document.querySelector(".carousel-item").classList.add("active");
});
