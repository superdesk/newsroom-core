import React from 'react';
import {Provider} from 'react-redux';
import {render as _render} from 'react-dom';
import '@superdesk/common/dist/src/index.css';

export function render(store: any, App: any, element?: any, props?: any) {
    return _render(
        <Provider store={store}>
            <App {...props}/>
        </Provider>,
        element
    );
}
