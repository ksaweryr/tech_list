document.querySelector('button[type=submit]').addEventListener('click', async event => {
    event.preventDefault();
    const username = document.querySelector('input[name=username]');
    const password = document.querySelector('input[name=password]');
    const rpassword = document.querySelector('input[name=repeated_password]');
    let ok = true;

    for(field of [username, password, rpassword]) {
        field.classList.remove('is-valid', 'is-invalid');
    }

    for(field of [username, password]) {
        if(!field.checkValidity()) {
            ok = false;
            field.classList.add('is-invalid');
        }
        else {
            field.classList.add('is-valid');
        }
    }

    rpassword.classList.add((ok &&= rpassword.value === password.value) ? 'is-valid' : 'is-invalid');

    if(!ok) {
        return;
    }

    const resp = await apiRequest('auth/register', {username: username.value, password: password.value}, 'POST');

    if(resp.status != 200) {
        const alert = document.querySelector('#api-error');
        alert.innerHTML = resp.json.error;
        alert.removeAttribute('hidden');
    }
    else {
        window.location.href = '/';
    }
});