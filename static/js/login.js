document.querySelector('button[type=submit]').addEventListener('click', async event => {
    event.preventDefault();
    const username = document.querySelector('input[name=username]').value;
    const password = document.querySelector('input[name=password]').value;
    const resp = await apiRequest('auth/login', {username, password}, 'POST');

    if(resp.status != 200) {
        const alert = document.querySelector('#api-error');
        alert.innerHTML = resp.json.error;
        alert.removeAttribute('hidden');
    }
    else {
        window.location.href = '/';
    }
});