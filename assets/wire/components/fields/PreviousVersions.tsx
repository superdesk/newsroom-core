import React from 'react';
import PropTypes from 'prop-types';

import {gettext} from 'utils';
import {getVersionsLabelText} from 'wire/utils';

export function PreviousVersions ({item, isItemDetail, inputRef}: any) {
    if (isItemDetail) {
        return null;
    }

    const numVersions = (item.ancestors ?? []).length;
    const versionLabelText = getVersionsLabelText(item, numVersions === 0 || numVersions > 1);
    const onClick = () => {
        const previousVersions = document.getElementById(inputRef);
        previousVersions && previousVersions.scrollIntoView();
    };

    return (
        <span>
            <div className="versions-link" onClick={onClick}>
                {gettext('{{ count }} previous {{ versionsLabel }}', {
                    count: numVersions,
                    versionsLabel: versionLabelText,
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
