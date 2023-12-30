function uploadFile(inputId, tipoDocumento) {
    var input = document.getElementById(inputId);
    var file = input.files[0];
    var spinner = document.getElementById('spinner');

    // Verificar si el archivo es un PDF
    if (file.type !== 'application/pdf') {
        alert('Por favor, sube un archivo PDF.');
        return;
    }

    spinner.style.display = 'block'; // Mostrar el spinner
    console.log('Mostrando spinner'); // Mensaje en consola

    var formData = new FormData();
    formData.append('file', file);
    formData.append('tipo_documento', tipoDocumento);

    var csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    fetch('/upload', {
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log('Ocultando spinner'); // Mensaje en consola
        spinner.style.display = 'none'; // Ocultar el spinner

        if (data.status === 'Completado') {
            alert('Archivo cargado con éxito');
        } else {
            alert('Error al cargar el archivo: ' + data.message);
        }
        window.location.reload(); // Puede que necesites modificar esto para evitar recargar la página si no es necesario.
    })
    .catch(error => {
        console.log('Ocultando spinner'); // Mensaje en consola
        spinner.style.display = 'none'; // Ocultar el spinner
        alert('Error al cargar el archivo');
    });
}
