import React from 'react';
import PropTypes from 'prop-types';
import {gettext} from 'utils';

export default function Content(props: any) {
    return (
        <div className={'content--' + props.type} role={gettext('dialog')} aria-label={gettext('Item Detail')}>
            <h3 className="a11y-only">{gettext('Item Detail')}</h3>
            {props.children}
        </div>
    );
}

Content.propTypes = {
    type: PropTypes.string,
    children: PropTypes.node,
};