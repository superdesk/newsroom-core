import * as React from 'react';
import Proptypes from 'prop-types';
import * as DOMPurify from 'dompurify';

export function HTMLContent({text}) {
    return (
        <div dangerouslySetInnerHTML={{__html: DOMPurify.sanitize(text)}} />
    );
}

HTMLContent.propTypes = {
    text: Proptypes.string.isRequired,
};
