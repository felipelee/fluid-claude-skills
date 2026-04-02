document.addEventListener('DOMContentLoaded', function () {

onElementInserted('body', 'select.custom-theme-select', function (e) {
  initSelect(e)
})

document.querySelectorAll('select.custom-theme-select').forEach(el => {
  initSelect(el)
})


function initSelect (el) {
  new TomSelect(el, {
    allowEmptyOption: false,
    controlInput: null,
  })
}
}); 