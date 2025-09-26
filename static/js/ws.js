// function validatePhone(phone) {
  // const regexPhone = /^[0-9]{10}$/; // Solo 10 dígitos
  // if (phone.trim() === "") {
    // alert("El número telefónico es obligatorio");
    // return false;
  // }

  // if (!regexPhone.test(phone)) {
    // alert("El número telefónico debe contener solo 10 dígitos");
    // return false;
  // }
  // return true;
// }

function validatePhone(phone) {
  // Expresión regular para validar formatos flexibles
  const regexPhone = /^(\+52\s?)?(\(?\d{2,3}\)?[-.\s]?)?\d{4}[-.\s]?\d{4}$/;

  // Verificar si el campo está vacío
  if (phone.trim() === "") {
    alert("El número telefónico es obligatorio");
    return false;
  }

  // Verificar si el formato coincide
  if (!regexPhone.test(phone)) {
    alert("El formato del número telefónico no es válido");
    return false;
  }

  // Extraer solo los dígitos del número
  const digits = phone.replace(/[^0-9]/g, "");

  // Verificar que el número tenga 10 o 12 dígitos (10 sin código de país, 12 con +52)
  if (digits.length !== 10 && digits.length !== 12) {
    alert("El número telefónico debe contener 10 dígitos (sin código de país) o 12 dígitos (con +52)");
    return false;
  }

  // Si tiene 12 dígitos, asegurarse de que los primeros 2 sean "52" (código de país)
  if (digits.length === 12 && digits.substring(0, 2) !== "52") {
    alert("El código de país debe ser +52 para México");
    return false;
  }

  // Extraer los últimos 10 dígitos (número local)
  const localDigits = digits.slice(-10);

  // Reglas adicionales para evitar números inválidos o poco realistas
  if (
    // Todos los dígitos son iguales
    new Set(localDigits).size === 1 ||
    // Patrones repetitivos (ejemplo: 1212121212)
    localDigits === localDigits.substring(0, 2).repeat(5) ||
    // Secuencias ascendentes/descendentes
    localDigits === "0123456789" || localDigits === "9876543210"
  ) {
    alert("El número telefónico parece inválido o poco realista");
    return false;
  }

  // Si pasa todas las validaciones, el número es válido
  return true;
}

function getSelectedRadioValue(name) {
  const radios = document.querySelectorAll(`input[name="${name}"]`);
  for (const radio of radios) {
    if (radio.checked) {
      return radio.value;
    }
  }
  return null;
}

async function sendInfo() {
  const name = document.getElementById("name_gpc").value.trim();
  const phone = document.getElementById("phone_gpc").value.trim();
  const selectedOption = getSelectedRadioValue("contacto");

  if (name === "") {
    alert("El nombre es requerido");
    return;
  }

  if (!validatePhone(phone)) {
    return;
  }

  if (!selectedOption) {
    alert("Selecciona una opción de servicio");
    return;
  }

  const data = {
    name: name,
    phone: phone,
    option: selectedOption
  };

  try {
    const response = await fetch("/welcome_user", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    const result = await response.json();
    window.location.href = "https://machin.gpscontrol.com.mx/chat-gpscontrol";
    //alert(result.message);
  } catch (error) {
    alert("Lo sentimos, hubo un error intenta nuevamente.");
  }
}
