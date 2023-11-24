function eliminarNotificacion(idNotificacion) {
    var csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    fetch('/eliminar-notificacion/' + idNotificacion, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        }
    })
    .then(response => {
        if (response.ok) {
            document.getElementById('notificacion-' + idNotificacion).remove();
        } else {
            alert('Error al eliminar la notificación');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
