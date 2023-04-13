import React from 'react';
import PropTypes from 'prop-types';
import {gettext} from 'assets/utils';

export function PreviousVersions ({item, isItemDetail, inputRef}: any) {
    if (isItemDetail) {
        return null;
    }

    const onClick = () => {
        const previousVersions = document.getElementById(inputRef);
        previousVersions && previousVersions.scrollIntoView();
    };

    return (
        <span>
            <div className="blue-text" onClick={onClick}>
                {gettext('{{ count }} previous versions', {
                    count: item.ancestors
                        ? item.ancestors.length
                        : '0',
                })}
            </div>
        </span>
    );
}


PreviousVersions.propTypes = {
    isItemDetail: PropTypes.bool,
    item: PropTypes.object,
    inputRef: PropTypes.string,
};
