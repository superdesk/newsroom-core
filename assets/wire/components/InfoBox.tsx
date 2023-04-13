import React from 'react';
import PropTypes from 'prop-types';
import {gettext} from 'assets/utils';
import InfoBoxContent from './InfoBoxContent';
import {bem} from 'assets/ui/utils';

export default function InfoBox(props: any) {
    const className = bem('info-box', null, {
        'top': props.top,
    });
    const renderChildren = (props.children ? (Array.isArray(props.children) ? props.children : [props.children]) : [])
        .filter((c: any) => c);

    return (
        <div className={className} id={props.id || null}>
            {props.label && (
                <span className="info-box__label">{gettext('{{name}}', {name: props.label})}</span>
            )}
            {React.Children.map(renderChildren, (element, key) => <InfoBoxContent key={key} element={element} />)}
        </div>
    );
}

InfoBox.propTypes = {
    id: PropTypes.string,
    label: PropTypes.string,
    children: PropTypes.node,
    top: PropTypes.bool,
};
