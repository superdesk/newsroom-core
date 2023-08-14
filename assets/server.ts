const defaultOptions = {
    credentials: 'same-origin',
    redirect: 'manual',
};

function options(custom: any = {}) {
    return Object.assign({}, defaultOptions, custom);
}

function checkStatus(response: any) {
    if (response.status === 204) {
        return {};
    } else if (response.status >= 200 && response.status < 300) {
        return response.json();
    } else if (response.status >= 400 && response.status < 500) {
        return response.json().then((data: any) => Promise.reject(data));
    } else {
        if (response.type === 'opaqueredirect') {
            window.location.reload();
        } else {
            console.error(response.statusText);
            return Promise.reject(response);
        }
    }
}

function getHeaders(etag: any) {
    const headers: any = {'Content-Type': 'application/json'};

    if (etag != null) {
        headers['If-Match'] = etag;
    }

    return headers;
}


class Server {
    /**
     * Make GET request
     *
     * @param {String} url
     * @return {Promise}
     */
    get(url: any) {
        return fetch(url, options({}))
            .then(checkStatus);
    }

    /**
     * Make GET request accepting application/json
     *
     * @param {String} url
     * @return {Promise}
     */
    getJson(url: any) {
        return fetch(url, options({
            headers: {
                Accept: 'application/json',
            },
        })).then(checkStatus);
    }

    /**
     * Make POST request to url
     *
     * @param {String} url
     * @param {Object} data
     * @return {Promise}
     */
    post(url: any, data: any) {
        return fetch(url, options({
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: data ? JSON.stringify(data) : null,
        })).then(checkStatus);
    }

    /**
     * Make POST request to url in keeps the format of the input
     *
     * @param {String} url
     * @param {Object} data
     * @return {Promise}
     */
    postFiles(url: any, data: any) {
        return fetch(url, options({
            method: 'POST',
            body: data,
        })).then(checkStatus);
    }

    /**
     * Make DELETE request to url
     *
     * @param {String} url
     * @return {Promise}
     */
    del(url: any, data: any, etag?: any) {
        return fetch(url, options({
            method: 'DELETE',
            headers: getHeaders(etag),
            body: data ? JSON.stringify(data) : null,
        })).then(checkStatus);
    }

    /**
     * Make PATCH request to url
     *
     * @param {String} url
     * @param {Object} data
     * @return {Promise}
     */
    patch(url: any, data: any, etag?: any) {
        return fetch(url, options({
            method: 'PATCH',
            headers: getHeaders(etag),
            body: JSON.stringify(data),
        })).then(checkStatus);
    }

    patchEntity(url: string, data: any, _etag: string) {
        return fetch(
            url,
            options({
                method: 'PATCH',
                headers: {'Content-Type': 'application/json', 'If-Match': _etag},
                body: JSON.stringify(data),
            })
        ).then(checkStatus);
    }
}

export default new Server();
