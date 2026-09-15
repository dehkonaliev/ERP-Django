document.addEventListener('DOMContentLoaded', function () {
  var closes = document.querySelectorAll('.alert-close');
  closes.forEach(function (btn) {
    btn.addEventListener('click', function () {
      btn.parentElement.remove();
    });
  });
});