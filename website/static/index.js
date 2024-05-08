document.addEventListener("DOMContentLoaded", function () {
  let client_id = "";
  const socket = io();

  const sendBtn = document.getElementById("sendBtn");
  const msgInput = document.getElementById("msgInput");

  sendBtn.addEventListener("click", function () {
    const message = msgInput.value.trim();
    if (message !== "") {
      console.log(client_id);
      socket.emit("message", { message }); // Send message to the server
      msgInput.value = ""; // Clear input field after sending message
    }
  });
  socket.on("connection_response", ({ client_id: id }) => {
    client_id = id;
  });

  socket.on("chat_message", function (data) {
    const chatDiv = document.getElementById("chatDiv");
    const messageElement = document.createElement("div");
    const senderElement = document.createElement("span");
    const contentElement = document.createElement("p");
    if (data.sender == "System") {
      messageElement.classList.add("message", "system");
      contentElement.textContent = `${data.message}`;
      messageElement.appendChild(contentElement);
      chatDiv.appendChild(messageElement);
    } else {
      const sentByCurrentUser = client_id == data.client_id;
      if (sentByCurrentUser) {
        messageElement.classList.add("message", "sent"); // Add a CSS class to indicate that the message was sent by the current user
      } else {
        messageElement.classList.add("message", "received"); // Add a CSS class to indicate that the message was received
      }
      senderElement.textContent = `${data.sender}`;
      contentElement.textContent = `${data.message}`;

      // chatDiv.appendChild(messageElement);
      messageElement.appendChild(senderElement);
      messageElement.appendChild(contentElement);
      chatDiv.appendChild(messageElement);
    }
  });
});
