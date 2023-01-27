document.querySelector('#create-group').addEventListener('click', function(event) {
    document.querySelector('#create-group-desc').style.display = 'block';
    document.querySelector('#join-group-desc').style.display = 'none';
})

document.querySelector('#join-group').addEventListener('click', function(event) {
    document.querySelector('#join-group-desc').style.display = 'block';
    document.querySelector('#create-group-desc').style.display = 'none';
})
