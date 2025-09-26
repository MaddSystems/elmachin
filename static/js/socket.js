const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const userOnConected = document.getElementById('who-is-connected');
const chatID = document.getElementById('chat-id'); // Chat ID pasado desde el backend
const chatState = document.getElementById('chat-state');
// const socket = io();  // O puedes poner la URL si es necesario
let enRojo = 0;

const socket = io({
  transports: ['websocket', 'polling'],
  // upgrade: true
});

// const socket = io('https://elmachin.custodiayvigilancia.mx',{
  // transports: ['websocket', 'polling'],
// });

const sesionId = document.getElementById('session-id');  // Chat ID pasado desde el backend
let seller_id;
let chat_id;

//-----------------> Conexiones de wenSocket

socket.on('connect', () => {
  //seller_id=socket.id;
  session_id = sesionId.value;
  chat_id = chatID.value;
  socket.emit('join_as_vendedor', {chat_id: chat_id,session_id:session_id,seller_id: socket.id});
});

socket.on('connected', (data) => {
  console.log("El servidor confirmó conexión ", data);
});

socket.on('disconnect', (reason) => {
  console.log(`Desconectado: ${reason}`);
  if (reason === 'transport close') {
    console.log('Se cerró la ventana o se perdió la conexión.');
    // disconnect_dashboard
  } else if (reason === 'ping timeout') {
    console.log('Se desconectó por inactividad.');
  }
  
});        

// Reason	              |   Description	                                                                Automatic reconnection?
// io server disconnect	|   The server has forcefully disconnected the socket with socket.disconnect()	❌ NO
// io client disconnect	|   The socket was manually disconnected using socket.disconnect()	            ❌ NO
// ping timeout	        |   The server did not send a PING within the pingInterval + pingTimeout range	✅ YES
// transport close	    |   The connection was closed (example: the user has lost connection, or the network was changed from WiFi to 4G)	✅ YES
// transport error	    |   The connection has encountered an error (example: the server was killed during a HTTP long-polling cycle)	✅ YES


// //Unirse a una sala
// function joinRoom(roomName) {
    // socket.emit('join', { room: roomName });
    // currentRoom = roomName;
// }
 
// // Abandonar la sala actual
// function leaveRoom() {
    // if (currentRoom) {
        // socket.emit('leave', { room: currentRoom });
        // currentRoom = null;
    // }
// }

// Recibir mensajes
socket.on('receive_message', function(data) {
  console.log("Mensaje recibido:", data);
  addMessage(data.sender, data.message);
});

// Recibir mensajes
socket.on('seller_message', function(data) {
  console.log("Te has unido a un chat:", data);
  addMessage(data.sender, data.message);
});


socket.on('room_joined', function (data) {
  console.log(`Te has unido al chat ${data.chat_id}`);
});

socket.on('room_rejoined', function (data) {
  console.log(`Reconectado al chat ${data.chat_id}`);
});

socket.on('user_left', (data) => {
  console.log(`El usuario ${data.user_id} salió del chat`);
});

socket.on('suggested_responses_seller', (data) => {
  console.log("suggested_responses_seller:",data);

  var suggested_responses = []
  if("suggested_responses" in data){
    if(data.suggested_responses != [] ){
      console.log("DATA suggested_responses:",data.suggested_responses);
      suggested_responses = data.suggested_responses;
    }
    showQuickResponses(suggested_responses);
  }

});

// Desconectar manualmente el socket del usuario
function disconnectSocket() {
  console.log("Desconectando socket...");
  socket.disconnect();
}

function disconnectUser(user_id) {
  socket.emit('admin_disconnect_user', { user_id: user_id });
}


///----------------------->> Machi Pausa

function playMachain(){
  console.log("playMachain");

  const luzRoja = document.getElementById("luzRoja");
  const luzVerde = document.getElementById("luzVerde");
  const input = document.getElementById("user-input");

  if (enRojo==0) {
    luzRoja.classList.remove("encendido");
    luzVerde.classList.add("encendido");
    input.disabled = false;
    input.focus();
    socket.emit('join_whit_user_chat', {chat_id: chat_id, session_id:session_id, seller_id: socket.id});
    enRojo = 1;
  } else {
    luzRoja.classList.add("encendido");
    luzVerde.classList.remove("encendido");
    input.disabled = true;
    input.value = ""; // opcional: borra el texto      
    socket.emit('has_left_user_chat', {chat_id: chat_id, session_id:session_id, seller_id: socket.id});
    enRojo = 0;
  }
      session_id = sesionId.value;
      chat_id = chatID.value;
      fetch('/play_machin', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ session_id: session_id, chat_id:chat_id})
        })
        .then(response => response.json())
        .then(data => {
          console.log("Data:",data);
          // socket.emit('send_message', { session_id: socket.id, message: data.response, sender: 'Machín'});
          // socket.emit('join_whit_user_chat', {chat_id: chat_id, session_id:session_id, seller_id: socket.id});
          addMessage('Machín', data.response);
        })
        .catch(error => {
            console.error('Error:', error);
      });
}

// function addMessage(sender, message) {
  // console.log("Entre al new AddMessage SPEED PROM");
  // const typingSpeed = 30;
  // const chatMessages = document.getElementById('chat-messages');
  // const messageDiv = document.createElement('div');
  // messageDiv.className = `message ${sender}`;
  // chatMessages.appendChild(messageDiv);
  // const tempDiv = document.createElement('div');
  // chat_id = chatID.value;
  // session_id = sesionId.value;
  // 
  // if (sender === "Machín" || sender === "vendedor") {
    // messageDiv.innerHTML = message.substring(0, currentIndex + 1);
    // tempDiv.innerHTML = message;  
  // } else {
      // messageDiv.textContent = message.substring(0, currentIndex + 1);
      // tempDiv.textContent = message;
  // }
// 
  // function processNode(node, container) {
    // if (node.nodeType === Node.TEXT_NODE) {
      // Efecto de escritura solo para texto plano
      // return new Promise((resolve) => {
        // let text = node.textContent;
        // let charIndex = 0;
        // const interval = setInterval(() => {
          // if (charIndex < text.length) {
            // 
            // container.append(text[charIndex]);
            // charIndex++;
            // chatMessages.scrollTop = chatMessages.scrollHeight; // Mantener el scroll en la parte inferior
          // } else {
            // clearInterval(interval);
            // resolve();
          // }
        // }, typingSpeed);
      // });
    // } else if (node.nodeType === Node.ELEMENT_NODE) {
      // Renderizar inmediatamente elementos HTML
      // const element = document.createElement(node.tagName.toLowerCase());
      // for (const attr of node.attributes) {
        // element.setAttribute(attr.name, attr.value);
      // }
      // container.appendChild(element);
      // 
      // Procesar los hijos del elemento de manera recursiva
      // return Array.from(node.childNodes).reduce((promise, childNode) => {
        // return promise.then(() => processNode(childNode, element));
      // }, Promise.resolve());
    // }
    // return Promise.resolve(); // Ignorar otros tipos de nodos
  // }
// 
  // Procesar todos los nodos en el mensaje
  // return Array.from(tempDiv.childNodes)
    // .reduce((promise, node) => {
      // return promise.then(() => {
        // const span = document.createElement('span'); // Contenedor temporal
        // messageDiv.appendChild(span);
        // return processNode(node, span);
      // });
    // }, Promise.resolve())
    // .then(() => {
      // chatMessages.scrollTop = chatMessages.scrollHeight; // Ajustar el scroll después de procesar todo
      // console.log("Mensaje completo mostrado.");
    // });
// }


// function sendMessage(sender) {
  // console.log("Enviando Mensaje");
  // const message = userInput.value.trim();
  // const chat_id = chatID.value;
  // if (message) {
    // try {
        // const session_id = sesionId.value;
        // socket.emit('send_message', {chat_id: chat_id, session_id:session_id,message: message, sender: 'vendedor', seller_id: socket.id});
        // addMessage('vendedor', message);
      // } catch (error) {
          // console.error("Error:", error);
          // addMessage('Machín', '¡Ups! Lo siento, parece que algo no salió como esperábamos. Por favor, intenta más tarde o contacta al administrador para obtener ayuda. ¡Gracias!');
      // }
    // }
    // userInput.value = '';
// }

function typingMessage(sender) {
  console.log("typingMessage...");
  
  const chatMessages = document.getElementById('chat-messages');
  const dots = document.querySelector('.thinking-dots');
  
  // Control de los puntos en la cabecera
  // if (sender === "user") {
      // dots.classList.add('show-thinking');
  // } else {
      // dots.classList.remove('show-thinking');
  // }
  // Buscar si ya hay un mensaje de "escribiendo..."
  let existingTyping = document.querySelector(".typing-indicator");
  
  if (sender === "user") {
      if (existingTyping) return; // No agregar otro si ya existe
      
      const messageDiv = document.createElement('div');
      messageDiv.className = "typing-indicator";
      messageDiv.innerHTML = "<span>.</span><span>.</span><span>.</span>";
      chatMessages.appendChild(messageDiv);
  } else {
      // Eliminar el mensaje "escribiendo..." cuando el bot responde
      if (existingTyping) {
          existingTyping.remove();
      }
  }
  chatMessages.scrollTop = chatMessages.scrollHeight; // Auto-scroll
}

let videoCounter = 0; // Contador global para asignar IDs únicos a los videos
let currentVideoElement = null;

async function addMessage(sender, message, typingSpeed = 25) {
  console.log("Entre al new AddMessage SPEED PROMP");
  const chatMessages = document.getElementById('chat-messages');
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${sender}`;
  chatMessages.appendChild(messageDiv);

  typingMessage(sender);

  // Sanitizar el contenido si es HTML
  const tempDiv = document.createElement('div');
  // if (sender === "Machín" || sender === "vendedor") {
    // tempDiv.innerHTML = DOMPurify.sanitize(message); // Protección contra XSS
  // } else {
  tempDiv.innerHTML = message;
  // }

  // Array para almacenar referencias a los videos
  const videoElements = [];

  async function typeText(text, container) {
    return new Promise((resolve) => {
      let charIndex = 0;
      const interval = setInterval(() => {
        if (charIndex < text.length) {
          container.append(text[charIndex]);
          charIndex++;
          chatMessages.scrollTop = chatMessages.scrollHeight; // Desplazamiento gradual
        } else {
          clearInterval(interval);
          resolve();
        }
      }, typingSpeed);
    });
  }

  async function processNode(node, container) {
    if (node.nodeType === Node.TEXT_NODE) {
      await typeText(node.textContent, container);
    } else if (node.nodeType === Node.ELEMENT_NODE) {
      const element = document.createElement(node.tagName.toLowerCase());
      for (const attr of node.attributes) {
        element.setAttribute(attr.name, attr.value);
      }

      // Si es un video, asignamos ID y lo pausamos hasta que termine el mensaje
      if (element.tagName.toLowerCase() === "video") {
        videoCounter++;
        const videoId = `video-${videoCounter}`;
        element.setAttribute("id", videoId);
        element.setAttribute("controls", "true"); // Opcional
        element.setAttribute("preload", "auto");

        // Guardamos la referencia al video para reproducirlo más tarde
        videoElements.push(element);

        element.onloadedmetadata = () => console.log(`Video ${videoId} listo.`);
      }

      container.appendChild(element);

      // Procesamos hijos recursivamente antes de avanzar
      for (const child of node.childNodes) {
        await processNode(child, element);
      }
    }
  }

  
  // Procesar cada nodo del mensaje
  for (const node of tempDiv.childNodes) {
    await processNode(node, messageDiv);
  }

  // Auto scroll al final del mensaje
  chatMessages.scrollTop = chatMessages.scrollHeight;

  // Reproducir todos los videos después de que el mensaje haya terminado
  for (const videoElement of videoElements) {
    console.log(`Reproduciendo video: ${videoElement.id}`);
    try {
      // Detener el video anterior si existe
      if (currentVideoElement && !currentVideoElement.paused) {
        console.log(`Deteniendo video anterior: ${currentVideoElement.id}`);
        currentVideoElement.pause();
      }
      // Actualizar la referencia al video actual
      currentVideoElement = videoElement;

      await videoElement.play(); // Esperamos a que termine la reproducción de cada video
    } catch (error) {
      console.warn(`Error al reproducir el video ${videoElement.id}:`, error);
      videoElement.insertAdjacentHTML(
        "afterend",
        `<span style="color: red;">⚠️ Error al reproducir el video.</span>`
      );
    }
  }

}


function addVideo(gridId, targetInputId) {
  var rowId = $("#" + gridId).jqGrid('getGridParam', 'selrow');
  if (!rowId) {
      $.alert("Selecciona una fila", { autoClose: true, type: "warning" });
      return;
  }

  var rowData = $("#" + gridId).getRowData(rowId);
  var fileName = rowData['file_name'];  // o 'title' si prefieres usar el título
  var fileId = rowData['id'];
  var title_name = rowData['title'];

  // Asignar valores a inputs (ajusta los IDs reales)
  console.log(fileName);
  file_elemet = title_name + ' <br><br><video controls controlslist="nodownload"> <source src="/static/videos/' + fileName + '" type="video/mp4"> Tu navegador no soporta el video. </video><br>'
  document.getElementById("user-input").value = file_elemet;
}

function sendVideos(sender) {

  if (enRojo==0) {
    $.alert("Interacción no disponible", { autoClose: true, type: "warning" });
  } else {
      const winHeight = 500;
      const winWidth = 810;
      const gridId = 'jgGridModelFiles';
      const pagerId = 'jqGridPagerModelFiles';
      const $gridId = `#${gridId}`;
      const $pagerId = `#${pagerId}`;
      // Limpieza previa
      $($gridId).length && $($gridId).remove();
      $($pagerId).length && $($pagerId).remove();
      $("#ModelFilesForm").length && $("#ModelFilesForm").remove();
      // Crear nuevo div y HTML
      const newDiv = $("<div class='model-files-container'></div>");
      const html = `
          <div id="ModelFilesForm" title="Doble click para seleccionar">
              <table id="${gridId}"></table>
              <div id="${pagerId}"></div>
          </div>
      `;
      newDiv.html(html);

      // Crear el diálogo
      const dialog = newDiv.dialog({
          autoOpen: false,
          title: "Doble click para seleccionar",
          height: winHeight,
          width: winWidth,
          modal: true,
          buttons: {
               "Agregar": function () {
                  addVideo('jgGridModelFiles', "selectuser");
                   $('#ModelFilesForm').html("");
                   dialog.dialog("close");
               },
               "Cerrar": function () {
                   $('#ModelFilesForm').html("");
                   dialog.dialog("close");
               }
           },
           close: function () {
               $('#ModelFilesForm').html("");
           }               
      });
    
      // Listener de redimensionamiento con namespace
      $(window).off("resize.jqgridfiles").on("resize.jqgridfiles", function () {
          const $grid = $($gridId);
          const newWidth = $grid.closest(".ui-jqgrid").parent().width();
          $grid.jqGrid("setGridWidth", newWidth, true);
      });
    
      // Inicializar jqGrid
      const grid = $($gridId);
      grid.jqGrid({
          url: '/get_short_files',
          mtype: "GET",
          datatype: "json",
          page: 1,
          colModel: [
              { label: 'ID', name: 'id', width: 50, key: true },
              { label: 'Título', name: 'title', width: 100 },
              { label: 'Archivo', name: 'file_name', width: 150 },
              { label: 'Descripción', name: 'description', width: 150 },
              { label: 'Clasificación', hidden: true, name: 'clasification', width: 150, edittype: 'select', editoptions: { value: "internal:Interno;external:Externo" } },
              { label: 'Fecha de Creación', hidden: true, name: 'created_at', width: 150, formatter: 'date', formatoptions: { srcformat: 'Y-m-d H:i:s', newformat: 'd/m/Y H:i' } }
          ],
          loadonce: true,
          viewrecords: true,
          width: 780,
          height: 250,
          rowNum: 100,
          rowList: [100, 500, 1000],
          multiselect: false,
          pager: $pagerId,
          ondblClickRow: function (rowid) {
               const grid = $("#jgGridModelFiles");
               const rowData = grid.getRowData(rowid);
               // Asigna directamente los valores
               document.getElementById("file_migrate_form").value = rowData['file_name']; // o 'file_name'
               document.getElementById("file_migrate_form_id").value = rowData['id'];
               $('#ModelFilesForm').html("");
               dialog.dialog("close");
           }                          
      });
    
      // Toolbar y navGrid
      grid.jqGrid('navGrid', $pagerId, {
          search: true,
          add: false,
          edit: false,
          del: false,
          refresh: true
      });
      grid.jqGrid('filterToolbar', { stringResult: true, searchOnEnter: false });
    
      // Evento doble clic para seleccionar archivo
      grid.on("dblclickRow", function (rowid) {
          const rowData = grid.jqGrid("getRowData", rowid);
          console.log("Archivo seleccionado:", rowData);
          // Puedes insertar el archivo en un campo o input aquí
          dialog.dialog("close");
      });
    
      // Abrir el diálogo
      dialog.dialog("open");
    }
}


function sendMessage(sender) {
  console.log("Enviando Mensaje");
  const message = userInput.value.trim();
  const chat_id = chatID.value;
  
  // console.log("Semaforo:", enRojo)
  // if (enRojo) {
    // console.log("Enviando mensaje:", enRojo)
    if (message) {
      const session_id = sesionId.value;
      // console.log("ENVIANDO MENSAJE:", "chat_id:", chat_id, "session_id:",session_id,"message:", message, ":", 'vendedor', "seller_id:",socket.id);
      socket.emit('send_message', {chat_id: chat_id, session_id:session_id,message: message, sender: 'vendedor', seller_id: socket.id});
      addMessage('vendedor', message);

        fetch('/chat_seller', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message, chat_id:chat_id})
        })
        .then(response => response.json())
        .then(data => {
          console.log("Respondiendo");
          console.log("Data:",data);

          var suggested_responses = []
          if("suggested_responses" in data){
            if(data.suggested_responses != [] ){
              console.log("DATA suggested_responses:",data.suggested_responses);
              suggested_responses = data.suggested_responses;
              // showQuickResponses(data.suggested_responses);
            }
          }

          if("response" in data){
            console.log("Data responses:", data.response);

            addMessage('Machín', data.response).then(() => {
              console.log("suggested_responses:",suggested_responses);
              showQuickResponses(suggested_responses);
            });
          }
        })
        .catch(error => {
          console.error("Error:", error);
          addMessage('Machín', '¡Ups! Lo siento, parece que algo no salió como esperábamos. Por favor, intenta más tarde o contacta al administrador para obtener ayuda. ¡Gracias!');
        });
        userInput.value = '';
    }
  // } else {
    // console.log("Mensaje NO enviando:", enRojo)
  // }
}


function sendMessageSelected(message) {
  console.log("Enviando mensaje:", message)
  // const chat_id = chatID.value.trim();
  // if (enRojo) {
    const chat_id = chatID.value;
    const session_id = sesionId.value;
    socket.emit('send_message', {chat_id: chat_id, session_id:session_id,message: message, sender: 'vendedor', seller_id: socket.id});
    addMessage('vendedor', message);
    userInput.value = '';
  // }
}

function appendHistory(history){
  for (let i = 0; i < history.length; i++) {
    //console.log(history[i].usser,history[i].message);
    addMessage_last(history[i].sender,history[i].message);
  }
}

document.addEventListener('DOMContentLoaded', async () => {
    // try {
      const chat_id = chatID.value;
      const session_id = sesionId.value;
        // Llamar al endpoint de Flask para obtener la IP
        // const response = await fetch('/seller_conect');

        const response = await fetch(`/seller_conect?chat_id=${chat_id}&session_id=${session_id}`);
        // seller_id: socket.id
        // const response = await fetch('/seller_conect', {
          // method: 'POST',
          // headers: {
            // 'Content-Type': 'application/json'
          // },
          // body: JSON.stringify({ session_id: session_id, chat_id:chat_id}) // mandas el id en el cuerpo
          // 
        // });

        const data = await response.json();
        // console.log("Tu IP es:", data.ip); // Para depuración
        // userOnConected.value = data.ip;
        //chatID.value = data.chat_id;
        firts_message = data.message;
        // Mostrar el mensaje de bienvenida del chatbot
        var suggested_responses = []

        if("history_process" in data){
          // console.log(data.history_process);
          appendHistory(data.history_process);
        }

        if("suggested_responses" in data){
          if(data.suggested_responses != [] ){
            console.log("DATA suggested_responses:",data.suggested_responses);
            suggested_responses = data.suggested_responses;
          }
        }
        // Agrega el mensaje del bot con efecto de escritura
        console.log("Data responses:", firts_message);
        addMessage_last('Machín', firts_message);
        showQuickResponses(suggested_responses);

        // addMessage_last('Machín', firts_message).then(() => {
          // // //Después de terminar el efecto de escritura, muestra las preguntas sugeridas
          // console.log("DATA suggested_responses:",suggested_responses);
          // showQuickResponses(suggested_responses);
          // 
        // });
    // } catch (error) {
        // addMessage_last('Machín', '¡Ups! Lo siento, parece que algo no salió como esperábamos. Por favor, intenta nuevamente más tarde o contacta a uno de nuestros asesores para obtener ayuda. ¡Gracias por tu paciencia!');
    // }

});


// Web Speech API para reconocimiento de voz
const micButton = document.getElementById('mic-button');

// Verifica si el navegador soporta SpeechRecognition
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (SpeechRecognition) {
  const recognition = new SpeechRecognition();
  recognition.lang = 'es-MX'; // Idioma: español de México
  recognition.interimResults = false; // Solo resultados finales
  recognition.continuous = false; // Detiene automáticamente tras un reconocimiento

  micButton.addEventListener('click', () => {
    if (micButton.classList.contains('recording')) {
      recognition.stop(); // Detener reconocimiento si ya está en marcha
      micButton.classList.remove('recording');
    } else {
      recognition.start(); // Iniciar reconocimiento
      micButton.classList.add('recording');
    }
  });

  // Cuando se detecta texto
  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    console.log("Texto reconocido:", transcript);

    // Inserta el texto en el campo de entrada
    userInput.value = transcript;

    // Opcional: simula enviar el mensaje automáticamente
    sendMessage("user");
  };

  // Maneja errores
  recognition.onerror = (event) => {
    console.error("Error en reconocimiento:", event.error);
    alert("Hubo un problema al usar el reconocimiento de voz. Intenta de nuevo.");
  };
} else {
  alert("Tu navegador no soporta Speech Recognition. Usa Chrome o Edge para esta funcionalidad.");
}


// addTypingEffect
function addMessage_legacy(sender, message, typingSpeed = 30) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    let currentIndex = 0;

    function type() {
        if (currentIndex < message.length) {
            // messageDiv.textContent += message[currentIndex];
            messageDiv.innerHTML += message[currentIndex];
            currentIndex++;
            chatMessages.scrollTop = chatMessages.scrollHeight; // Scroll al final
            setTimeout(type, typingSpeed);
        }
    }
    type();
}

function addMessage_(sender, message, typingSpeed = 30) {
  const chatMessages = document.getElementById('chat-messages');
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${sender}`; // Asegúrate de que las clases sean correctas ('Machín' o 'user')
  chatMessages.appendChild(messageDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight; // Asegura que el scroll esté siempre al final

      // Detectar si el mensaje contiene HTML
      const isHTML = /<.*?>/.test(message);

      if (isHTML) {
          // Insertar HTML directamente sin efecto de escritura
          messageDiv.innerHTML = message;
          chatMessages.scrollTop = chatMessages.scrollHeight;
      } else {

        let currentIndex = 0;
        function type() {
            if (currentIndex < message.length) {
              if (sender === "Machín" || sender === "vendedor") {
                  messageDiv.innerHTML = message.substring(0, currentIndex + 1);
                  
                } else {
                    messageDiv.textContent = message.substring(0, currentIndex + 1);
                    //messageDiv.innerHTML = message.substring(0, currentIndex + 1);
                }
                currentIndex++;
                chatMessages.scrollTop = chatMessages.scrollHeight;
                setTimeout(type, typingSpeed);
            }
        }
        type();
      }
}


function addMessage_last(sender, message) {
  const chatMessages = document.getElementById('chat-messages');
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${sender}`;
  //messageDiv.textContent = message;
  if (sender === "Machín" || sender === "vendedor") {
    messageDiv.innerHTML = message;
  } else {
      messageDiv.textContent = message;
  }
  chatMessages.appendChild(messageDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight; // Scroll al final
}

// Inserta una respuesta rápida en el chat y oculta las sugerencias
function selectQuickResponse(response) {
  // Agregar la respuesta al chat usando sendMessageSelected()

    console.log("Enviando:",response)
    // Desaparecer las respuestas rápidas
    const quickResponses = document.getElementById("quick-responses");
    quickResponses.classList.add("fade-out");

    // Limpiar las respuestas rápidas después de la animación
    setTimeout(() => {
        quickResponses.innerHTML = "";
        quickResponses.classList.remove("fade-out");
    }, 500);
    // addMessage('user',response); // Envía el mensaje como si lo hubiera escrito el usuario
    sendMessageSelected(response);
}

// Generar respuestas sugeridas dinámicamente
function showQuickResponses(responses) {
  const quickResponses = document.getElementById("quick-responses");
  quickResponses.innerHTML = ""; // Limpiar respuestas previas

  responses.forEach(response => {
      const button = document.createElement("button");
      button.classList.add("response");
      button.textContent = response;
      button.onclick = () => selectQuickResponse(response);
      quickResponses.appendChild(button);
  });

  quickResponses.classList.add("fade-in");
}


function addMessage_ok(sender, message) {
  console.log("entre al new AddMessage")
  const typingSpeed = 30;
  const chatMessages = document.getElementById('chat-messages');
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${sender}`;
  chatMessages.appendChild(messageDiv);

  const tempDiv = document.createElement('div');
  tempDiv.innerHTML = message;

  function processNode(node, container) {
    if (node.nodeType === Node.TEXT_NODE) {
      // Aplicar efecto de escritura solo en texto puro
      return new Promise((resolve) => {
        let text = node.textContent;
        let charIndex = 0;
        const interval = setInterval(() => {
          if (charIndex < text.length) {
            container.append(text[charIndex]);
            charIndex++;
            chatMessages.scrollTop = chatMessages.scrollHeight;
          } else {
            clearInterval(interval);
            resolve();
          }
        }, typingSpeed);
      });
    } else if (node.nodeType === Node.ELEMENT_NODE) {
      // Procesar elementos HTML inmediatamente
      const element = document.createElement(node.tagName.toLowerCase());
      for (const attr of node.attributes) {
        element.setAttribute(attr.name, attr.value);
      }
      container.appendChild(element);

      // Procesar nodos hijos del elemento
      return Array.from(node.childNodes).reduce((promise, childNode) => {
        return promise.then(() => processNode(childNode, element));
      }, Promise.resolve());
    }
    return Promise.resolve(); // Ignorar otros nodos
  }

  // Procesar los nodos del mensaje uno por uno
  Array.from(tempDiv.childNodes)
    .reduce((promise, node) => {
      return promise.then(() => {
        // Crear un contenedor temporal para cada nodo
        const span = document.createElement('span');
        messageDiv.appendChild(span);
        return processNode(node, span);
      });
    }, Promise.resolve())
    .then(() => {
      chatMessages.scrollTop = chatMessages.scrollHeight;
    });
  //showQuickResponses(suggested_responses);
}

// // ejemplo de funciones asicronas con promesas de manera simple
// async function obtenerDatos() {
  // try {
      // let usuario = await fetch('https://jsonplaceholder.typicode.com/users/1').then(res => res.json());
      // console.log('Usuario obtenido:', usuario);

      // let posts = await fetch(`https://jsonplaceholder.typicode.com/posts?userId=${usuario.id}`).then(res => res.json());
      // console.log('Posts del usuario:', posts);

      // let comentarios = await fetch(`https://jsonplaceholder.typicode.com/comments?postId=${posts[0].id}`).then(res => res.json());
      // console.log('Comentarios del post:', comentarios);

  // } catch (error) {
      // console.error('Error en el proceso:', error);
  // }
// }

// <img src="{{ url_for('static', filename='images/logo.png') }}" alt="Logo">
// <video src="{{ url_for('static', filename='videos/v1-machin-good.mp4') }}" controls></video>