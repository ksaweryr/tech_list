const apiRequest = async (endpoint, body, method, content_type = 'application/json') => {
    const response = await fetch(`/api/${endpoint}`, {
        method,
        headers: {
            ...(content_type.startsWith('multipart') || {'Content-type': content_type})
        },
        ...(method != 'GET' && {body: (content_type === 'application/json' ? JSON.stringify : x => x)(body)})
    });

    return {
        status: response.status,
        json: await response.json()
    };
};