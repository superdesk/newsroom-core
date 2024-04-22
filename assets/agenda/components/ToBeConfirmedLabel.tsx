import React from 'react';
import classNames from  'classnames';
import {IAgendaItem, IListConfig, IPreviewConfig} from 'interfaces';
import {isTopStory} from 'agenda/utils';
import {gettext} from 'utils';

interface IProps {
    item: IAgendaItem;
    size?: 'normal' | 'big';
}

export default function ToBeConfirmedLabel({item, size}: IProps) {
    const classes = classNames('label label--rounded label--orange', {
        'label--big': size === 'big',
        'mb-2': size === 'big',
    });

    return (
        item.event?.occur_status?.qcode === 'eocstat:eos3'
            ? (
                <div>
                    <span className={classes}>{gettext('To be confirmed')}</span>
                </div>
            ) : null
    );
}
