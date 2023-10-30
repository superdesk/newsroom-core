import React from 'react';

import {IArticle} from 'interfaces';
import {newshubApi} from 'api';
import {gettext} from 'utils';

interface IProps {
    item: IArticle;
    isItemDetail: boolean;
    inputRef: string;
}

export function PreviousVersions ({item, isItemDetail, inputRef}: IProps) {
    if (isItemDetail) {
        return null;
    }

    const onClick = () => {
        const previousVersions = document.getElementById(inputRef);
        previousVersions && previousVersions.scrollIntoView();
    };
    const numVersions = (item.ancestors ?? []).length;
    const versionLabelText = newshubApi.ui.wire.getVersionsLabelText(
        item,
        numVersions === 0 || numVersions > 1
    );

    return (
        <span>
            <div className="versions-link" onClick={onClick}>
                {gettext('{{ count }} previous {{ versionsLabel }}', {
                    versionsLabel: versionLabelText,
                    count: numVersions,
                })}
            </div>
        </span>
    );
}
