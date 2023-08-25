import React from 'react';

import classNames from 'classnames';
import {getPublicContacts} from 'agenda/utils';
import {IAgendaItem} from 'interfaces';

interface IProps {
    item: IAgendaItem
    inList?: boolean;
}

export function AgendaContacs({item, inList = false}: IProps) {
    return (
        <>
            {getPublicContacts(item).map((contact) => (
                <div
                    key={contact._id}
                    className={classNames({
                        'd-flex': inList,
                        'wire-articles__item__meta-row': !inList,
                    })}
                >
                    <i className='icon-small--user icon--gray-dark'></i>
                    <span>{`${contact.name}${(contact.name && contact.organisation) ? ', ' : ''}${contact.organisation} ${contact.phone} ${contact.mobile} `}
                        {contact.email && <a href={`mailto:${contact.email}`} target="_blank">{contact.email}</a>}
                    </span>
                </div>
            ))}
        </>
    );
}