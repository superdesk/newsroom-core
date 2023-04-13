import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import {bem} from 'assets/ui/utils';


const AMNewsIcon = ({iconType, borderRight, toolTip}: any) => {
    const css = classNames(
        'wire-articles__item__am-icons',
        bem('wire-articles__item', 'meta-time', {'border-right': borderRight})
    );
    return (
        <div className={css} data-bs-toggle="tooltip" data-bs-placement="left" title={toolTip}>
            <i className={`icon--${iconType}`}></i>
        </div>
    );
};

AMNewsIcon.propTypes = {
    iconType: PropTypes.string.isRequired,
    toolTip: PropTypes.string,
    borderRight: PropTypes.bool,

};

AMNewsIcon.defaultProps = {
    borderRight: false
};

export default AMNewsIcon;
