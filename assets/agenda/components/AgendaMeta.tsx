import React from 'react';
import PropTypes from 'prop-types';
import {hasLocation, getEventLinks, getLocationString, getCalendars, getLocationDetails} from 'agenda/utils';
import {AgendaContacs} from './AgendaContacts';
import {IAgendaItem} from 'interfaces';

const url = (link: any) => link.startsWith('http') ? link : 'https://' + link;

interface IProps {
    item: IAgendaItem
}

function AgendaPreviewMeta({item}: IProps) {
    return (
        <div className='wire-articles__item__meta'>
            <div className='wire-articles__item__meta-info'>
                {hasLocation(item) && <div className='wire-articles__item__meta-row'>
                    <i className='icon-small--location icon--gray-dark'></i>
                    <span>{getLocationString(item)}</span>
                </div>}
                {getLocationDetails(item) && (
                    <div className='wire-articles__item__meta-row wire-articles__item__meta-row--info'>
                        <i className='icon-small--info icon--gray-dark'></i>
                        <span>{getLocationDetails(item)}</span>
                    </div>
                )}
                <AgendaContacs item={item} />
                {getEventLinks(item).map((link: any) => <div className='wire-articles__item__meta-row' key={link}>
                    <i className='icon-small--globe icon--gray-dark'></i>
                    <span><a href={url(link)} target="_blank">{link}</a></span>
                </div>)}
                {getCalendars(item) && <div className='wire-articles__item__meta-row'>
                    <i className='icon-small--calendar icon--gray-dark'></i>
                    <span>{getCalendars(item)}</span>
                </div>}
            </div>
        </div>
    );
}

AgendaPreviewMeta.propTypes = {
    item: PropTypes.object,
    isItemDetail: PropTypes.bool,
    inputRef: PropTypes.string,
};

export default AgendaPreviewMeta;
