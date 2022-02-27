const apiRequest = async (endpoint, body, method) => {
    const response = await fetch(`/api/${endpoint}`, {
        method,
        headers: {
            'Content-type': 'application/json'
        },
        ...(method != 'GET' && {body: JSON.stringify(body)})
    });

    return {
        status: response.status,
        json: await response.json()
    };
};