document.querySelector('button[type=submit]').addEventListener('click', async event => {
    event.preventDefault();
    const fields = [
        'name', 'logo', 'description', 'link'
    ].map(n => document.querySelector(`[name=${n}]`));
    let ok = true;
    const [name, logo, description, link] = fields;

    for(field of fields) {
        field.classList.remove('is-valid', 'is-invalid');
        if(!field.checkValidity()) {
            ok = false;
            field.classList.add('is-invalid');
        }
        else {
            field.classList.add('is-valid');
        }
    }

    if(!ok) {
        return;
    }

    const formdata = new FormData();
    formdata.append('body', JSON.stringify({
        name: name.value,
        description: description.value,
        link: link.value
    }));
    formdata.append('logo', logo.files[0]);

    const resp = await apiRequest('technology', formdata, 'POST', 'multipart/form-data');

    if(resp.status != 200) {
        const alert = document.querySelector('#api-error');
        alert.innerHTML = resp.json.error;
        alert.removeAttribute('hidden');
    }
    else {
        window.location.href = `/technology/${resp.json.tid}`;
    }
});