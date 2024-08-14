import React, {StrictMode} from 'react';
import {Provider} from 'react-redux';
import {render as _render} from 'react-dom';
import '@superdesk/common/dist/src/index.css';

export function render<T = any>(store: any, App: any, element?: any, props?: T) {
    return _render(
        <StrictMode>
            <Provider store={store}>
                    <App {...props}/>
            </Provider>
        </StrictMode>
        ,
        element
    );
}
