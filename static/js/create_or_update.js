const verifyData = (fields, create_post) => {
    let ok = true;

    for(field of fields) {
        field.classList.remove('is-valid', 'is-invalid');
        if(!field.checkValidity() && (create_post || field.name != 'logo')) {
            ok = false;
            field.classList.add('is-invalid');
        }
        else {
            field.classList.add('is-valid');
        }
    }

    return ok;
};

const createFromData = fields => {
    const [name, logo, description, link] = fields;
    const formdata = new FormData();

    formdata.append('body', JSON.stringify({
        name: name.value,
        description: description.value,
        link: link.value
    }));

    if(logo.files[0] !== undefined) {
        formdata.append('logo', logo.files[0]);
    }

    return formdata;
};

const getEventListener = create_post => async event => {
    event.preventDefault();

    const fields = [
        'name', 'logo', 'description', 'link'
    ].map(n => document.querySelector(`[name=${n}]`));

    if(!verifyData(fields, create_post)) {
        return;
    }

    const formdata = createFromData(fields);
    const tid = document.querySelector('[name=tid]')?.value;
    const resp = await apiRequest('technology' + (create_post ? '' : `/${tid}`), formdata, create_post ? 'POST' : 'PATCH', 'multipart/form-data');

    if(resp.status != 200) {
        const alert = document.querySelector('#api-error');
        alert.innerHTML = resp.json.error;
        alert.removeAttribute('hidden');
    }
    else {
        window.location.href = `/technology/${tid ?? resp.json.tid}`;
    }
};

document.querySelector('button.create[type=submit]')?.addEventListener('click', getEventListener(true));
document.querySelector('button.update[type=submit]')?.addEventListener('click', getEventListener(false));