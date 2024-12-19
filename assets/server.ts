const defaultOptions = {
    credentials: 'same-origin',
    redirect: 'manual',
};

interface RequestOptions {
    parseJson?: boolean;
}

function options(custom: any = {}) {
    return Object.assign({}, defaultOptions, custom);
}

function checkStatus(response: Response, requestOptions: RequestOptions = {parseJson: true}): Promise<any> {
    const {parseJson = true} = requestOptions;

    if (response.status === 204) {
        return Promise.resolve({});
    }

    if (response.status >= 200 && response.status < 300) {
        if (!parseJson) {
            return Promise.resolve(response);
        }

        const contentType = response.headers.get('Content-Type');
        if (contentType && contentType.includes('application/json')) {
            return response.json();
        }
        return Promise.resolve(response);
    }

    if (response.status === 400) {
        return response.json().then((data: any) => Promise.reject({errorData: data}));
    }

    if (response.type === 'opaqueredirect') {
        window.location.reload();
    }

    console.error(response);
    return Promise.reject(response);
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
    post(
        url: any,
        data: any,
        etag?: string,
        requestOptions: RequestOptions = {parseJson: true}
    ) {
        return fetch(url, options({
            method: 'POST',
            headers: getHeaders(etag),
            body: data ? JSON.stringify(data) : null,
        })).then((response) => checkStatus(response, requestOptions));
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
