function uploadFile(inputId, tipoDocumento) {
    var input = document.getElementById(inputId);
    var file = input.files[0];

    // Verificar si el archivo es un PDF
    if (file.type !== 'application/pdf') {
        alert('Por favor, sube un archivo PDF.');
        return; // Detener la ejecución si no es un PDF
    }

    var formData = new FormData();
    formData.append('file', file);
    formData.append('tipo_documento', tipoDocumento);

    // Obtener el token CSRF del meta tag
    var csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    // AJAX request para subir el archivo
    fetch('/upload', {
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'Completado') {
            alert('Archivo cargado con éxito');
        } else {
            alert('Error al cargar el archivo: ' + data.message);
        }
        window.location.reload();
    })
    .catch(error => {
        alert('Error al cargar el archivo');
    });
}
