const apiRequest = async (endpoint, body, method) => {
    const response = await fetch(`/api/${endpoint}`, {
        method,
        headers: {
            'Content-type': 'application/json'
        },
        body: JSON.stringify(body)
    });

    return {
        status: response.status,
        json: await response.json()
    };
};