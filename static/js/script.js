const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const userOnConected = document.getElementById('who-is-connected');
const chatID = document.getElementById('chat-id');
const chatState = document.getElementById('chat-state');
let tiempoVisualizado = {};

// const socket = io();  // O puedes poner la URL si es necesario
// const socket = io('https://elmachin.custodiayvigilancia.mx');

// const socket = io.connect('wss://elmachin.custodiayvigilancia.mx/socket.io/?EIO=4&transport=websocket');

// const socket = io("wss://elmachin.custodiayvigilancia.mx", {
    // transports: ["websocket"]
// });

// const socket = io({
  // transports: ['websocket', 'polling'],
  // upgrade: true
// });

const socket = io({
  transports: ['websocket', 'polling'],
});

// const socket = io({
  // reconnection: true,
  // reconnectionAttempts: 10,  // Intentar reconectar 10 veces
  // reconnectionDelay: 5000,   // Esperar 5 segundos entre intentos
  // timeout: 60000             // Esperar 60 segundos antes de desconectar
// });

// let chatId = localStorage.getItem('chat_id'); // Guardamos el chat_id en localStorage
// let message_sanitized;
let chat_id;
let session_id;

socket.on('connect', () => {
  // console.log("Cliente conectado con ID (cliente):", socket.id);
  session_id = socket.id;
  chat_id = chatID.value;

  // Si el usuario ya tenía un chat en curso, lo volvemos a unir a su sala
  console.log("Conected ID:", chat_id)

  if (chat_id != "" || chat_id != "undefined" || chat_id != " ") {
      numb_= numberValidate(chat_id);

      if (numb_ == true) {
        socket.emit('rejoin_room', {chat_id:chat_id,session_id:session_id});
      }
  } else {
    console.log("chat_id no reconocido");
  }
});

socket.on('connected', (data) => {
  console.log("El servidor confirmó conexión ", data);
});

socket.on('disconnect', (reason) => {
  console.log(`Desconectado: ${reason}`);
  if (reason === 'transport close') {
    console.log('Se cerró la ventana o se perdió la conexión.');

  } else if (reason === 'ping timeout') {
    console.log('Se desconectó por inactividad.');

  }
  
  if (reason === "io server disconnect") {
    socket.connect();  // Intentar reconectar manualmente si el servidor lo desconectó
  }
});


// Recibir mensajes
socket.on('receive_message', function(data) {
  console.log("Mensaje recibido:", data);
  // console.log("Mensaje:",data.msg);
  // console.log("Sender:",data.sender);
  addMessage(data.sender, data.message);
});

socket.on('vendedor_joined', function(data) {  
  const seller_conected = `El vendedor ${data.vendedor} se ha unido al chat.`;
  console.log("DTA: ",data.message)
  addMessage("Machín", data.message);
  // document.getElementById('messages').appendChild(li);
});

socket.on('vendedor_joined_it', function(data) {  
  const seller_conected = `El vendedor ${data.vendedor} se ha unido al chat.`;
  console.log("DTA: ",data.message)
  addMessage("Machín", data.message);
  // document.getElementById('messages').appendChild(li);
});

socket.on('room_joined', function (data) {
  console.log(`Te has unido al chat ${data.chat_id}`);
});

socket.on('room_rejoined', function (data) {
  session_id = data.session_id;
  console.log(`Reconectado con éxito al chat ${data.session_id}`);
});

window.addEventListener("beforeunload", () => {
  socket.emit("manual_disconnect");
});

// Desconectar manualmente el socket del usuario
function disconnectSocket() {
  console.log("Desconectando socket...");
  socket.disconnect();
}

///-------------------------------------------------------------------->>

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
  if (sender === "Machín" || sender === "vendedor") {
    tempDiv.innerHTML = DOMPurify.sanitize(message); // Protección contra XSS
  } else {
    tempDiv.textContent = message;
  }

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


function addMessage_speed_legacy(sender, message) {
  console.log("Entre al new AddMessage SPEED PROMP");

  const typingSpeed = 30;
  const chatMessages = document.getElementById('chat-messages');
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${sender}`;
  chatMessages.appendChild(messageDiv);
  const tempDiv = document.createElement('div');
  
  if (sender === "Machín" || sender === "vendedor") {
    // messageDiv.innerHTML = message.substring(0, currentIndex + 1);
    tempDiv.innerHTML = message;  
  } else {
      // messageDiv.textContent = message.substring(0, currentIndex + 1);
      tempDiv.textContent = message;
  }

  function processNode(node, container) {
    if (node.nodeType === Node.TEXT_NODE) {
      // Efecto de escritura solo para texto plano
      return new Promise((resolve) => {
        let text = node.textContent;
        let charIndex = 0;
        const interval = setInterval(() => {
          if (charIndex < text.length) {
            
            container.append(text[charIndex]);
            charIndex++;
            chatMessages.scrollTop = chatMessages.scrollHeight; // Mantener el scroll en la parte inferior
          } else {
            clearInterval(interval);
            resolve();
          }
        }, typingSpeed);
      });
    } else if (node.nodeType === Node.ELEMENT_NODE) {
      // Renderizar inmediatamente elementos HTML
      const element = document.createElement(node.tagName.toLowerCase());
      for (const attr of node.attributes) {
        element.setAttribute(attr.name, attr.value);
      }
      container.appendChild(element);
      
      // Procesar los hijos del elemento de manera recursiva
      return Array.from(node.childNodes).reduce((promise, childNode) => {
        return promise.then(() => processNode(childNode, element));
      }, Promise.resolve());
    }
    return Promise.resolve(); // Ignorar otros tipos de nodos
  }

  // Procesar todos los nodos en el mensaje
  return Array.from(tempDiv.childNodes)
    .reduce((promise, node) => {
      return promise.then(() => {
        const span = document.createElement('span'); // Contenedor temporal
        messageDiv.appendChild(span);
        return processNode(node, span);
      });
    }, Promise.resolve())
    .then(() => {
      chatMessages.scrollTop = chatMessages.scrollHeight; // Ajustar el scroll después de procesar todo
      // console.log("Mensaje completo mostrado.");
    });
}


function sendMessage_Legacy(sender) {
  console.log("Enviando Mensaje");
  const message = userInput.value.trim();
  const on_conected = userOnConected.value.trim();
  const chat_id = chatID.value;
  
  if (message) {

      socket.emit('send_message', {chat_id: chat_id, session_id: session_id, message: message, sender: 'user'});
      
      const message_sanitized = sanitizeInput(message);
      addMessage('user', message_sanitized);
      //addMessage_multimeia('user', message);
      fetch('/chat', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify({ message: message_sanitized , who_is_conected: on_conected, chat_id:chat_id})
      })
      .then(response => response.json())
      .then(data => {
        console.log("Respondiendo");
        console.log("Data:",data);

        if("history_process" in data){
          // console.log(data.history_process);
          appendHistory(data.history_process);
        }
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

          socket.emit('send_message', {chat_id: chat_id, session_id: session_id, message: data.response, sender: 'Machín'});
          addMessage('Machín', data.response).then(() => {
            console.log("suggested_responses:",suggested_responses);
            showQuickResponses(suggested_responses);
          });
        }

      })
      .catch(error => {
          console.error('Error:', error);
          // addMessage('Machín', 'Lo siento, algo salió mal, intentelo nuevamente o solicite la asistencia de un asesor humano, gracias...');
          addMessage('Machín', '¡Ups! Lo siento, parece que algo no salió como esperábamos. Por favor, intenta nuevamente más tarde o contacta a uno de nuestros asesores para obtener ayuda. ¡Gracias por tu paciencia!');
      });
      userInput.value = '';
  }
}

function sendMessage(sender) {
  console.log("Enviando Mensaje");
  const message = userInput.value.trim();
  const on_conected = userOnConected.value.trim();
  const chat_id = chatID.value;
  
  if (message) {

      socket.emit('send_message', {chat_id: chat_id, session_id: session_id, message: message, sender: 'user'});
      
      const message_sanitized = sanitizeInput(message);
      addMessage('user', message_sanitized);
      //addMessage_multimeia('user', message);
      fetchWithRetry('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message_sanitized, who_is_conected: on_conected, chat_id: chat_id })
      }, 15000, 2) // Timeout de 8 segundos, 2 reintentos adicionales
      .then(data => {
          console.log("Respondiendo");
          console.log("Data:", data);
      
          if ("history_process" in data) {
              appendHistory(data.history_process);
          }
        
          var suggested_responses = [];
          if ("suggested_responses" in data && data.suggested_responses.length > 0) {
              console.log("DATA suggested_responses:", data.suggested_responses);
              suggested_responses = data.suggested_responses;
          }
        
          if ("response" in data) {
              console.log("Data responses:", data.response);

              socket.emit('send_message', { chat_id: chat_id, session_id: session_id, message: data.response, sender: 'Machín' });

              addMessage('Machín', data.response).then(() => {
                  console.log("suggested_responses:", suggested_responses);
                  showQuickResponses(suggested_responses);
              });
          }
      })
      .catch(error => {
          console.error('Error:', error);
          let errorMessage = '¡Ups! Lo siento, algo salió mal. Por favor, intenta nuevamente más tarde o contacta a uno de nuestros asesores para obtener ayuda. ¡Gracias por tu paciencia!';
      
          if (error.message === 'Tiempo de espera agotado') {
              errorMessage = 'Parece que la conexión está lenta. Espera unos segundos y vuelve a intentarlo.';
          } else if (error.message.includes('Failed to fetch')) {
              errorMessage = 'No pudimos conectarnos con el servidor. Verifica tu conexión a internet e intenta de nuevo.';
          }

          socket.emit('send_message', { chat_id: chat_id, session_id: session_id, message: errorMessage, sender: 'Machín' });
          addMessage('Machín', errorMessage);
      });
      userInput.value = '';
  }
}

function sendMessageSelected_Legacy(message) {
  console.log("Enviando mensaje:", message)
  const on_conected = userOnConected.value.trim();
  const chat_id = chatID.value.trim();
  socket.emit('send_message', { session_id: session_id, chat_id:chat_id,message: message, sender: 'user'});
  if (message) {
      addMessage('user', message);

      fetch('/chat', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify({ message: message , who_is_conected: on_conected, chat_id:chat_id})
      })
      .then(response => response.json())
      .then(data => {

          console.log("Respondiendo...");
          console.log("Data:",data);

          if("history_process" in data){
            // console.log(data.history_process);
            appendHistory(data.history_process);
          }

          var suggested_responses = []
          if("suggested_responses" in data){
            if(data.suggested_responses != [] ){
              console.log("Data suggested_responses:",data.suggested_responses);
              suggested_responses = data.suggested_responses;
              // showQuickResponses(data.suggested_responses);
            }
          }
          socket.emit('send_message', { session_id: session_id, chat_id: chat_id, message: data.response, sender: 'Machín'});
          console.log("Data responses:", data.response);
          addMessage('Machín', data.response).then(() => {
            // Después de terminar el efecto de escritura, muestra las preguntas sugeridas
            console.log("Data suggested_responses:", data.suggested_responses);
            showQuickResponses(suggested_responses);
          });

      })
      .catch(error => {
          console.error('Error:', error);
          addMessage('Machín', '¡Ups! Lo siento, parece que algo no salió como esperábamos. Por favor, intenta nuevamente más tarde o contacta a uno de nuestros asesores para obtener ayuda. ¡Gracias por tu paciencia!');
          // addMessage('Machín', 'Lo siento, algo salió mal, intentelo nuevamente o solicite la asistencia de un asesor humano, gracias...');
      });
      userInput.value = '';
  }
}

function sendMessageSelected(message) {
  console.log("Enviando mensaje:", message)
  const on_conected = userOnConected.value.trim();
  const chat_id = chatID.value.trim();
  socket.emit('send_message', { session_id: session_id, chat_id:chat_id,message: message, sender: 'user'});
  if (message) {
      addMessage('user', message);
      fetchWithRetry('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message , who_is_conected: on_conected, chat_id:chat_id})
    }, 8000, 2) // Timeout de 8 segundos, 2 reintentos adicionales
    .then(data => {
      console.log("Respondiendo...");
      console.log("Data:",data);
      if("history_process" in data){
        // console.log(data.history_process);
        appendHistory(data.history_process);
      }
      var suggested_responses = []
      if("suggested_responses" in data){
        if(data.suggested_responses != [] ){
          console.log("Data suggested_responses:",data.suggested_responses);
          suggested_responses = data.suggested_responses;
          // showQuickResponses(data.suggested_responses);
        }
      }
      socket.emit('send_message', { session_id: session_id, chat_id: chat_id, message: data.response, sender: 'Machín'});
      console.log("Data responses:", data.response);
      addMessage('Machín', data.response).then(() => {
        // Después de terminar el efecto de escritura, muestra las preguntas sugeridas
        console.log("Data suggested_responses:", data.suggested_responses);
        showQuickResponses(suggested_responses);
      });      
    })
    .catch(error => {
        console.error('Error:', error);
        let errorMessage = '¡Ups! Lo siento, algo salió mal. Por favor, intenta nuevamente más tarde o contacta a uno de nuestros asesores para obtener ayuda. ¡Gracias por tu paciencia!';
    
        if (error.message === 'Tiempo de espera agotado') {
            errorMessage = 'Parece que la conexión está lenta. Espera unos segundos y vuelve a intentarlo.';
        } else if (error.message.includes('Failed to fetch')) {
            errorMessage = 'No pudimos conectarnos con el servidor. Verifica tu conexión a internet e intenta de nuevo.';
        }
    
        addMessage('Machín', errorMessage);
    });      
      userInput.value = '';
  }
}

// Función para realizar una solicitud con timeout
async function fetchWithTimeout(url, options = {}, timeout = 8000) {
  const controller = new AbortController();
  const signal = controller.signal;

  // Configuramos un timeout para abortar la solicitud si no responde a tiempo
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
      const response = await fetch(url, { ...options, signal });
      if (!response.ok) {
          throw new Error(`Error: ${response.status} ${response.statusText}`);
      }
      const data = await response.json();
      clearTimeout(timeoutId); // Limpiar el timeout si la respuesta es exitosa
      return data;
  } catch (error) {
      clearTimeout(timeoutId); // Limpiar el timeout en caso de error
      throw error; // Lanza el error para ser capturado por la función de reintentos
  }
}

// Función con reintentos
async function fetchWithRetry(url, options = {}, timeout = 8000, retries = 2) {
  for (let i = 1; i <= retries; i++) {
      try {
          const data = await fetchWithTimeout(url, options, timeout); // Intentamos la solicitud
          return data; // Si tiene éxito, retornamos los datos
      } catch (error) {
          if (i === retries) {
              throw error; // Si ya no quedan intentos, lanzamos el error
          }
          console.warn(`🔄 Reintentando... (${i + 1}/${retries})`); // Notificación de reintento
      }
  }
}



function appendHistory(history){
  for (let i = 0; i < history.length; i++) {
    //console.log(history[i].usser,history[i].message);
    addMessage_last(history[i].sender,history[i].message);
  }
}

document.addEventListener('DOMContentLoaded', async () => {

    try {
        // Llamar al endpoint de Flask para obtener la IP
        // const response = await fetch('/get_user_ip?userId=${usuario.id}');
        const response = await fetch('/get_user_ip');
        const data = await response.json();
        const videoId = `video_${Date.now()}`
        // console.log("Tu IP es:", data.ip); // Para depuración
        console.log("ID VIDEO:", videoId); // Para depuración
        userOnConected.value = data.ip;
        chatID.value = data.chat_id;
        chat_id = data.chat_id;
        firts_message = data.message;

        // Mostrar el mensaje de bienvenida del chatbot
        var suggested_responses = []
        if("suggested_responses" in data){
          if(data.suggested_responses != [] ){
            console.log("DATA suggested_responses:",data.suggested_responses);
            suggested_responses = data.suggested_responses;
            // showQuickResponses(data.suggested_responses);
          }
        }

        // Agrega el mensaje del bot con efecto de escritura
        socket.emit('join_chat', {session_id: session_id, chat_id: data.chat_id});
        
        console.log("Data responses:", firts_message);
        addMessage('Machín', firts_message).then(() => {
          // Después de terminar el efecto de escritura, muestra las preguntas sugeridas
          console.log("DATA suggested_responses:",suggested_responses);
          showQuickResponses(suggested_responses);
          
        });
        // Puedes enviar la IP al backend si necesitas registrarla
    } catch (error) {
        console.error("Error al obtener la IP:", error);
        addMessage('Machín', '¡Hola! soy el Machín de GPScontrol, bienvenido. ¿En qué puedo ayudarte hoy?');
    }

    // let videoStats = {}; 
    // let videoActual = null;

    // function enviarMetricas(videoId) {
        // if (!videoStats[videoId]) return;

        ////Enviar métricas al backend
        // fetch("/guardar_metricas", {
            // method: "POST",
            // headers: { "Content-Type": "application/json" },
            // body: JSON.stringify({ 
                // videoId: videoId,
                // tiempoVisualizado: videoStats[videoId].tiempoVisualizado,
                // vecesReproducido: videoStats[videoId].vecesReproducido,
                // interaccionesSeek: videoStats[videoId].interaccionesSeek,
                // porcentajeVisto: videoStats[videoId].porcentajeVisto,
                // tiempoAntesPlay: videoStats[videoId].tiempoAntesPlay
            // })
        // }).catch((error) => console.error("Error enviando métricas:", error));
    // }

    // function trackVideoEvents(video) {
        // let videoId = video.getAttribute("data-video-id") || `video-${Date.now()}`;
        // videoStats[videoId] = {
            // tiempoVisualizado: 0,
            // vecesReproducido: 0,
            // interaccionesSeek: 0,
            // porcentajeVisto: 0,
            // tiempoAntesPlay: 0
        // };

        // let tiempoInicio = 0;
        // let intervaloVisualizacion;
        // let intervaloActualizacion;

        // // Si es el primer video o cambia de video, reiniciamos el intervalo
        // if (videoActual !== videoId) {
            // videoActual = videoId;
            // clearInterval(intervaloActualizacion);
            // intervaloActualizacion = setInterval(() => {
                // enviarMetricas(videoId);
            // }, 300000); // 5 minutos

            // Enviar métricas iniciales si es un cambio de video
            // enviarMetricas(videoId);
        // }

        // video.addEventListener("loadeddata", () => {
            // tiempoInicio = performance.now();
        // });

        // video.addEventListener("play", () => {
            // if (video.currentTime < 1) {
                // videoStats[videoId].vecesReproducido++;
            // }

            // if (!videoStats[videoId].tiempoAntesPlay) {
                // videoStats[videoId].tiempoAntesPlay = ((performance.now() - tiempoInicio) / 1000).toFixed(2);
            // }

            // intervaloVisualizacion = setInterval(() => {
                // videoStats[videoId].tiempoVisualizado++;
            // }, 1000);
        // });

        // video.addEventListener("pause", () => {
            // clearInterval(intervaloVisualizacion);
            // videoStats[videoId].porcentajeVisto = ((videoStats[videoId].tiempoVisualizado / video.duration) * 100).toFixed(2);
            // enviarMetricas(videoId);
        // });

        // video.addEventListener("seeked", () => {
            // videoStats[videoId].interaccionesSeek++;
        // });

        // window.addEventListener("beforeunload", () => {
            // enviarMetricas(videoId);
        // });
    // }

    ////Detectar cuando se cargan nuevos videos dinámicamente
    // const observer = new MutationObserver((mutations) => {
        // mutations.forEach((mutation) => {
            // mutation.addedNodes.forEach((node) => {
                // if (node.tagName === "VIDEO") {
                    // trackVideoEvents(node);
                // }
            // });
        // });
    // });

    // observer.observe(document.body, { childList: true, subtree: true });

    // Inicializar los videos que ya están presentes al cargar la página
    // document.querySelectorAll("video").forEach((video) => trackVideoEvents(video));
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

// function typingMessage(sender) {
  // console.log("typingMessage...")
  // const chatMessages = document.getElementById('chat-messages');
  // const dots = document.querySelector('.thinking-dots');
  // if (sender === "user") {
      // dots.classList.add('show-thinking');
  // } else {
      // dots.classList.remove('show-thinking');
  // }
  // let existingTyping = document.querySelector("typing-indicator");
  // 
  // if (sender === "user") {
      // if (existingTyping) return;

      // const messageDiv = document.createElement('div');
      // messageDiv.className = "typing-indicator";
      // messageDiv.innerHTML = "<span>.</span><span>.</span><span>.</span>";

      // chatMessages.appendChild(messageDiv);
  // } else {
      // if (existingTyping) {
          // existingTyping.classList.remove('typing-indicator');
      // }
  // }
  // chatMessages.scrollTop = chatMessages.scrollHeight; // Auto-scroll
// }

function typingMessage(sender) {
  console.log("typingMessage...");
  
  const chatMessages = document.getElementById('chat-messages');
  const dots = document.querySelector('.thinking-dots');
  
  // Control de los puntos en la cabecera
  if (sender === "user") {
      dots.classList.add('show-thinking');
  } else {
      dots.classList.remove('show-thinking');
  }

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

/*
// Define the function to toggle shape and change video
function toggleShapeAndVideo() {
  const videoContainer = document.getElementById('video-container');
  const agentVideo = document.getElementById('agent-video');

  // Define the new video source
  const newVideoSource = 'new-video.mp4';

  // Toggle between circular and square shape
  videoContainer.classList.toggle('circle');
  videoContainer.classList.toggle('square');

  // Change the video source
  if (agentVideo.src.includes('agent-video.mp4')) {
    agentVideo.src = newVideoSource;
  } else {
    agentVideo.src = 'agent-video.mp4';
  }

  // Reload the video to apply the new source
  agentVideo.load();
  agentVideo.play();
}
*/

/*
// Web Speech API para reconocimiento de voz
let recognition;
if ('webkitSpeechRecognition' in window) {
    recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'es-MX';
    recognition.onresult = function (event) {
        const speechResult = event.results[0][0].transcript;
        appendMessage('user', speechResult);
        sendTextToServer(speechResult);
    };
    recognition.onerror = function (event) {
        console.error('Error de reconocimiento de voz: ', event);
    };
}
function startRecording() {
    recognition.start();
}
function stopRecording() {
    recognition.stop();
}
*/

// Inserta una respuesta rápida en el chat y oculta las sugerencias
function selectQuickResponse(response) {
  // Agregar la respuesta al chat usando sendMessageSelected()
  console.log("Enviando:",response)
  // Desaparecer las respuestas rápidas
  const quickResponses = document.getElementById("quick-responses");
  quickResponses.classList.add("fade-out");

  // Limpiar las respuestas rápidas después de la animación
  const title = quickResponses.querySelector(".title-responses");
  setTimeout(() => {
      quickResponses.innerHTML = "";
      if (title) {
        quickResponses.appendChild(title);
      }
      quickResponses.classList.remove("fade-out");
  }, 500);
  // addMessage('user',response); // Envía el mensaje como si lo hubiera escrito el usuario
  sendMessageSelected(response);
}



function showQuickResponses(responses) {
  const quickResponses = document.getElementById("quick-responses");

  // Mantener el título y eliminar solo las respuestas
  const title = quickResponses.querySelector(".title-responses");
  quickResponses.innerHTML = ""; // Borra todo el contenido

  // Volver a agregar el título después de limpiar
  if (title) {
      quickResponses.appendChild(title);
  }

  // Agregar las nuevas respuestas
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

function sanitizeInput(input) {
  // Mapa de caracteres maliciosos a sus entidades HTML seguras
  const map = {
    '<': '&lt;',
    '>': '&gt;',
    '&': '&amp;',
    '"': '&quot;',
    "'": '&#x27;',
    '/': '&#x2F;',
    '*': '&#x2A;',  // Asterisco
    '(': '&#x28;',  // Paréntesis izquierdo
    ')': '&#x29;',  // Paréntesis derecho
    '[': '&#x5B;',  // Corchete izquierdo
    ']': '&#x5D;',  // Corchete derecho
    '{': '&#x7B;',  // Llave izquierda
    '}': '&#x7D;',  // Llave derecha
  };

  // Expresión regular para detectar los caracteres maliciosos
  const regex = /[<>&"'\/*()[\]{}]/g;

  // Reemplazar caracteres maliciosos por sus equivalentes seguros
  return input.replace(regex, (char) => map[char]);
}

function numberValidate(char) {
  // Convertir el carácter a número
  let numero = parseInt(char, 10);

  // Validar si es un número
  if (!isNaN(numero)) {
      console.log(`El carácter '${char}' es un número: ${numero}`);
      return true;
  } else {
      console.log(`El carácter '${char}' no es un número.`);
      return false;
  }
}


//-------------------------> Bloquear de Click derecho y DevTools

//Bloquear clic derecho en toda la página
document.addEventListener("contextmenu", function(event) {
  event.preventDefault();
});

//Bloquear teclas para abrir DevTools (F12, Ctrl+Shift+I, Ctrl+Shift+J, Ctrl+U)
document.addEventListener("keydown", function(event) {
    if (event.key === "F12" || 
        (event.ctrlKey && event.shiftKey && (event.key === "I" || event.key === "J")) || 
        (event.ctrlKey && event.key === "U")) {
        event.preventDefault();
    }
});

// --------------------> Videos

// function video_play(id_video) {
  // var video = document.getElementById('id_video');
  // video.play(); // Inicia la reproducción automáticamente
// }

// Función para agregar un video dinámico al chat
// function agregarVideo() {
  // const chatContainer = document.getElementById("chat-container");
  // const videoId = `video_${Date.now()}`; // ID único basado en timestamp

  // const videoHTML = `
      // <video id="${videoId}" width="320" controls>
          // <source src="https://tudominio.com/videos/video.mp4" type="video/mp4">
          // Tu navegador no soporta el elemento de video.
      // </video>
  // `;

  // chatContainer.innerHTML += videoHTML;
  // inicializarEventos(videoId);
// }

// Modificamos la función de inicialización de eventos
// function inicializarEventos(videoId) {
  // const video = document.getElementById(videoId);

  // if (!video) return;

  // if (!tiempoVisualizado[videoId]) {
      // tiempoVisualizado[videoId] = 0; // Inicializa si es la primera vez
  // }

  // let inicioVisualizacion = 0;
  // let reproduciendo = false;

  // video.addEventListener("play", () => {
      // console.log(`📹 [${videoId}] Reproduciendo`);
      // inicioVisualizacion = Date.now();
      // reproduciendo = true;
  // });

  // video.addEventListener("pause", () => {
      // if (reproduciendo) {
          // tiempoVisualizado[videoId] += (Date.now() - inicioVisualizacion) / 1000;
          // console.log(`⏸️ [${videoId}] Pausado. Tiempo acumulado: ${tiempoVisualizado[videoId].toFixed(2)}s`);
      // }
      // reproduciendo = false;
  // });

  // video.addEventListener("ended", () => {
      // if (reproduciendo) {
          // tiempoVisualizado[videoId] += (Date.now() - inicioVisualizacion) / 1000;
          // console.log(`✅ [${videoId}] Finalizado. Tiempo total: ${tiempoVisualizado[videoId].toFixed(2)}s`);
      // }
      // reproduciendo = false;
  // });

  // video.addEventListener("seeked", () => {
      // console.log(`⏩ [${videoId}] Cambio de posición a ${video.currentTime.toFixed(2)}s`);
      
      // inicioVisualizacion = Date.now();
  // });

  // video.addEventListener("volumechange", () => {
    // console.log(`🔊 [${videoId}] Volumen cambiado a: ${video.volume}`);
// });

// } 