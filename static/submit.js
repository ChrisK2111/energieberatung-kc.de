document.addEventListener('DOMContentLoaded', () => {
  'use strict'

  let ans = updateSpamCheckQuestion()
  // Fetch all the forms we want to apply custom Bootstrap validation styles to
  const forms = document.querySelectorAll('.needs-validation')

  // Loop over them and prevent submission
  Array.from(forms).forEach(form => {
    form.addEventListener('submit', event => {
      spamCheck(ans)

      if (!form.checkValidity()) {
        event.preventDefault()
        event.stopPropagation()
      }

      form.classList.add('was-validated')
    }, false)
  })
});


function updateSpamCheckQuestion(){
  let a = Math.round(Math.random()*10)
  let b = Math.round(Math.random()*10)
  document.getElementById('spamCheckQuestion').innerHTML = 'Was ist ' + a + '+' + b + '?' 
  return String(a + b)
}

function spamCheck(ans){
  // if the input is wrong, the field is cleared and the default checkValidity method can be applied.
  if (document.getElementById('spamCheckInput').value !== ans){
    document.getElementById('spamCheckInput').value = ""
  }
}