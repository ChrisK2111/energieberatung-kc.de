document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('submitBtn').addEventListener('click', consoleLog);
    document.getElementById('submitBtn').addEventListener('click', validateForm);
});

function consoleLog(){
    console.log('abc')
}

function validateForm() {
    'use strict'
  
    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    const forms = document.querySelectorAll('.needs-validation')
  
    let allValid = true;

    // Loop over them and prevent submission
    Array.from(forms).forEach(form => {
        form.classList.add('was-validated')
        allValid = allValid * form.checkValidity();
    })

    if (allValid){
        sendContent()
    }

  }
  
function sendContent() {
    let formData = new FormData(document.getElementById('kontaktformular'));
        fetch('/py')
        .then(response => {
            if (!response.ok) {
              throw new Error('Network response was not ok');
            }
            return response
          })
          .then(data => {
            // Hier kannst du den empfangenen Daten in der Variable "data" verwenden
            // data
            formContainer = document.getElementById('formContainer');
            formContainer.innerHTML = "";
            formHeadText = document.getElementById('formHeadText');
            formHeadText.innerHTML = "Vielen Dank für Ihre Nachricht."
            console.log('irgendwas empfangen');
          })
          .catch(error => {
            console.error('There was a problem with your fetch operation:', error);
          });


}