import React from 'react';

import {IArticle} from 'interfaces';
import {gettext} from 'utils';
import {getVersionsLabelText} from 'wire/utils';

interface IProps {
    item: IArticle;
    isItemDetail: boolean;
    inputRef: string;
}

export function PreviousVersions({item, isItemDetail, inputRef}: IProps) {
    if (isItemDetail) {
        return null;
    }

    const onClick = () => {
        const previousVersions = document.getElementById(inputRef);
        previousVersions && previousVersions.scrollIntoView();
    };
    const numVersions = item.ancestors?.length ?? 0;
    const versionLabelText = getVersionsLabelText(item, numVersions === 0 || numVersions > 1);

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
