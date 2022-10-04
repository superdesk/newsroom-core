import React from 'react';
import PropTypes from 'prop-types';
import {hasLocation, hasLocationNotes, getEventLinks, getLocationString, getPublicContacts,
    getCalendars} from 'agenda/utils';


function AgendaPreviewMeta({item}) {
    return (
        <div className='wire-articles__item__meta'>
            <div className='wire-articles__item__meta-info'>
                {hasLocation(item) && <div className='wire-articles__item__meta-row'>
                    <i className='icon-small--location icon--gray-dark'></i>
                    <span>{getLocationString(item)}</span>
                </div>}
                {!hasLocationNotes(item) ? null : (
                    <div className='wire-articles__item__meta-row wire-articles__item__meta-row--info'>
                        <i className='icon-small--info icon--gray-dark'></i>
                        <span>{item.location[0].details[0]}</span>
                    </div>
                )}
                {getPublicContacts(item).map((contact, index) => <div
                    className='wire-articles__item__meta-row'
                    key={`${contact.name}-${index}`}>
                    <i className='icon-small--user icon--gray-dark'></i>
                    <span>{`${contact.name}${(contact.name && contact.organisation) ? ', ' : ''}${contact.organisation} ${contact.phone} ${contact.mobile} `}
                        {contact.email && <a href={`mailto:${contact.email}`} target="_blank">{contact.email}</a>}
                    </span>
                </div>)}
                {getEventLinks(item).map((link) => <div className='wire-articles__item__meta-row' key={link}>
                    <i className='icon-small--globe icon--gray-dark'></i>
                    <span><a href={link} target="_blank">{link}</a></span>
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
