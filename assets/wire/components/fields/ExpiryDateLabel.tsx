import React from 'react';
import {gettext, formatDate} from 'utils';
import {IArticle} from 'interfaces';

interface IProps {
    item: IArticle,
    filterGroupLabels: {
        [field: string]: string;
    },
}

export function ExpiryDateLabel (props: IProps) {
    const {item, filterGroupLabels} = props;

    if (item.expiry == null) {
        return null;
    }

    const label = filterGroupLabels?.expiry ?? gettext('Expiry Date');
    const value = formatDate(item.expiry);
    const text = label + ': ' + value;

    return (
        <span>{text}</span>
    );
}
